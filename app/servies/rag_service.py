"""
RAG (Retrieval-Augmented Generation) Service
Combines document retrieval with AI analysis for educational feedback
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import aiohttp
import json
from datetime import datetime

from .document_service import document_processor
from .vector_service import vector_db
from .embedding_service import embedding_service

logger = logging.getLogger("Genassista-EDU-pythonAPI.rag")

class RAGService:
    """Main RAG service for document analysis and feedback generation"""
    
    def __init__(self):
        # Support both Groq and OpenAI API keys (Groq uses OpenAI-compatible API)
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_api_key = groq_key or openai_key
        
        # Set base URL based on which API key is available
        if groq_key:
            self.openai_base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        else:
            self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not self.openai_api_key:
            logger.warning("No API key provided (neither GROQ_API_KEY nor OPENAI_API_KEY). RAG service will have limited functionality.")
    
    async def process_and_store_document(self, file_path: str, 
                                       metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document and store it in the vector database
        
        Args:
            file_path: Path to the document
            metadata: Document metadata (student_id, assignment_id, etc.)
        
        Returns:
            Processing result with document ID and status
        """
        try:
            # Process the document
            doc_result = document_processor.process_document(file_path)
            
            if not doc_result.get('processing_success', False):
                return {
                    'success': False,
                    'error': doc_result.get('error', 'Document processing failed'),
                    'document_id': None
                }
            
            # Generate document ID
            document_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file_path) % 10000}"
            
            # Extract content and create chunks
            content = doc_result.get('content', '')
            if not content.strip():
                return {
                    'success': False,
                    'error': 'No content extracted from document',
                    'document_id': None
                }
            
            # Create chunks for vector storage
            chunks = document_processor.chunk_content(content)
            
            # Add embeddings to chunks
            chunks_with_embeddings = await embedding_service.embed_document_chunks(chunks)
            
            # Store in vector database
            store_success = vector_db.add_document(
                document_id=document_id,
                content=content,
                metadata={
                    **metadata,
                    'file_name': doc_result.get('file_name', ''),
                    'file_type': doc_result.get('file_type', ''),
                    'word_count': doc_result.get('word_count', 0),
                    'processed_at': datetime.now().isoformat()
                },
                chunks=chunks_with_embeddings
            )
            
            if not store_success:
                return {
                    'success': False,
                    'error': 'Failed to store document in vector database',
                    'document_id': document_id
                }
            
            return {
                'success': True,
                'document_id': document_id,
                'content_length': len(content),
                'chunks_count': len(chunks),
                'metadata': doc_result
            }
            
        except Exception as e:
            logger.error(f"Failed to process and store document: {e}")
            return {
                'success': False,
                'error': str(e),
                'document_id': None
            }
    
    async def analyze_student_submission(self, submission_content: str, 
                                       assignment_id: str, 
                                       student_id: str) -> Dict[str, Any]:
        """
        Analyze a student submission using RAG
        
        Args:
            submission_content: Student's submission text
            assignment_id: Assignment identifier
            student_id: Student identifier
        
        Returns:
            Analysis result with feedback and suggestions
        """
        try:
            # Search for relevant knowledge base items
            knowledge_results = vector_db.search_knowledge(
                query=submission_content,
                subject="engelska",
                level="5",
                n_results=5
            )
            
            # Search for similar student submissions (for context)
            similar_submissions = vector_db.search_documents(
                query=submission_content,
                n_results=3,
                filter_metadata={"type": "student_submission"}
            )
            
            # Prepare context for AI analysis
            context = self._build_analysis_context(
                submission_content,
                knowledge_results,
                similar_submissions
            )
            
            # Generate AI analysis
            analysis = await self._generate_ai_analysis(context, submission_content)
            
            # Generate Skolverket-compliant feedback
            feedback = self._generate_skolverket_feedback(analysis, submission_content)
            
            return {
                'success': True,
                'analysis': analysis,
                'feedback': feedback,
                'knowledge_used': knowledge_results,
                'similar_submissions': similar_submissions,
                'submission_metadata': {
                    'assignment_id': assignment_id,
                    'student_id': student_id,
                    'word_count': len(submission_content.split()),
                    'analyzed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze student submission: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None,
                'feedback': None
            }
    
    def _build_analysis_context(self, submission: str, 
                               knowledge: List[Dict[str, Any]], 
                               similar: List[Dict[str, Any]]) -> str:
        """Build context for AI analysis"""
        context_parts = []
        
        # Add Skolverket knowledge
        if knowledge:
            context_parts.append("RELEVANT CURRICULUM KNOWLEDGE:")
            for item in knowledge[:3]:  # Top 3 most relevant
                context_parts.append(f"- {item['content']}")
        
        # Add similar submissions context
        if similar:
            context_parts.append("\nSIMILAR STUDENT SUBMISSIONS (for context):")
            for sub in similar[:2]:  # Top 2 most similar
                context_parts.append(f"- {sub['content'][:200]}...")
        
        # Add submission to analyze
        context_parts.append(f"\nSTUDENT SUBMISSION TO ANALYZE:\n{submission}")
        
        return "\n".join(context_parts)
    
    async def _generate_ai_analysis(self, context: str, submission: str) -> Dict[str, Any]:
        """Generate AI analysis using OpenAI API"""
        if not self.openai_api_key:
            # Fallback to simple heuristic analysis
            return self._heuristic_analysis(submission)
        
        try:
            prompt = f"""
Du är en expert på svensk gymnasieutbildning och Skolverkets Gy25-kriterier för Engelska 5.

Analysera följande elevuppgift enligt Skolverkets Gy25 bedömningskriterier:

{context}

Ge en detaljerad analys som inkluderar:
1. Nivåbedömning (E, C, eller A)
2. Styrkor i texten
3. Förbättringsområden
4. Specifika tips för nästa steg
5. Koppling till Gy25-kriterier

Svara på svenska och var konstruktiv och hjälpsam.
"""
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "Du är en expert på svensk gymnasieutbildning och Skolverkets Gy25-kriterier."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{self.openai_base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        
                        # Parse AI response into structured format
                        return self._parse_ai_response(ai_response)
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        return self._heuristic_analysis(submission)
        
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._heuristic_analysis(submission)
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        # Simple parsing - in production, you'd want more sophisticated parsing
        lines = ai_response.split('\n')
        
        analysis = {
            'level': 'C',  # Default
            'strengths': [],
            'improvements': [],
            'tips': [],
            'gy25_connection': '',
            'raw_response': ai_response
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'nivå' in line.lower() or 'level' in line.lower():
                if 'E' in line.upper():
                    analysis['level'] = 'E'
                elif 'A' in line.upper():
                    analysis['level'] = 'A'
                else:
                    analysis['level'] = 'C'
            
            elif 'styrk' in line.lower():
                current_section = 'strengths'
            elif 'förbättr' in line.lower() or 'utveckl' in line.lower():
                current_section = 'improvements'
            elif 'tips' in line.lower() or 'nästa' in line.lower():
                current_section = 'tips'
            elif 'gy25' in line.lower() or 'gy11' in line.lower() or 'kriterier' in line.lower():
                current_section = 'gy25_connection'
            
            elif line.startswith('-') or line.startswith('•'):
                content = line[1:].strip()
                if current_section and current_section in analysis:
                    if isinstance(analysis[current_section], list):
                        analysis[current_section].append(content)
                    else:
                        analysis[current_section] = content
        
        return analysis
    
    def _heuristic_analysis(self, submission: str) -> Dict[str, Any]:
        """Fallback heuristic analysis when AI is not available"""
        words = submission.split()
        word_count = len(words)
        sentences = submission.split('.')
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        # Simple level determination
        if word_count < 200 or avg_sentence_length < 8:
            level = 'E'
        elif word_count < 400 or avg_sentence_length < 15:
            level = 'C'
        else:
            level = 'A'
        
        return {
            'level': level,
            'strengths': [
                f"Texten är {word_count} ord lång",
                "Innehåller relevant information" if word_count > 100 else "Kort men fokuserad"
            ],
            'improvements': [
                f"Utveckla argumenten mer (nu {word_count} ord, försök nå 300+)" if word_count < 300 else "Bra längd",
                f"Använd längre meningar (genomsnitt {avg_sentence_length:.1f} ord per mening)" if avg_sentence_length < 12 else "Bra meningslängd"
            ],
            'tips': [
                "Läs igenom texten en gång till",
                "Lägg till exempel som stöder dina argument",
                "Kontrollera stavning och grammatik"
            ],
            'gy25_connection': f"Texten följer grundläggande struktur för Engelska 5",
            'raw_response': f"Heuristik-analys: {level}-nivå baserat på längd och struktur"
        }
    
    def _generate_skolverket_feedback(self, analysis: Dict[str, Any], 
                                    submission: str) -> str:
        """Generate Skolverket-compliant feedback"""
        level = analysis.get('level', 'C')
        strengths = analysis.get('strengths', [])
        improvements = analysis.get('improvements', [])
        tips = analysis.get('tips', [])
        
        feedback_parts = []
        
        # Level assessment
        feedback_parts.append(f"Denna text når {level}-nivå enligt Skolverkets kriterier för Engelska 5.")
        
        # Strengths
        if strengths:
            feedback_parts.append("\nStyrkor:")
            for strength in strengths[:3]:  # Top 3 strengths
                feedback_parts.append(f"• {strength}")
        
        # Improvements
        if improvements:
            feedback_parts.append("\nFörbättringsområden:")
            for improvement in improvements[:3]:  # Top 3 improvements
                feedback_parts.append(f"• {improvement}")
        
        # Next steps
        if tips:
            feedback_parts.append("\nNästa steg:")
            for tip in tips[:3]:  # Top 3 tips
                feedback_parts.append(f"• {tip}")
        
        # Gy25 connection
        gy25_connection = analysis.get('gy25_connection', '')
        if gy25_connection:
            feedback_parts.append(f"\nKoppling till Gy25: {gy25_connection}")
        
        return "\n".join(feedback_parts)
    
    async def search_documents(self, query: str, 
                             filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search documents in the vector database"""
        try:
            results = vector_db.search_documents(
                query=query,
                n_results=10,
                filter_metadata=filters
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG database"""
        try:
            return vector_db.get_collection_stats()
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

# Global instance
rag_service = RAGService()
