"""
LLM Service for Genassista EDU
Comprehensive AI integration with OpenAI GPT models for educational analysis
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
import asyncio
import aiohttp
import json
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger("Genassista-EDU-pythonAPI.llm")

@dataclass
class LLMConfig:
    """Configuration for LLM service"""
    api_key: str
    base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    model: str = os.getenv("LLM_MODEL", "gpt-4")
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = int(os.getenv("LLM_TIMEOUT", "60"))

class LLMService:
    """Comprehensive LLM service for educational AI analysis"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        # Support both OpenAI and Groq API keys
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("LLM_MODEL", "gpt-4")
        
        # If Groq API key is set, use Groq defaults
        if os.getenv("GROQ_API_KEY") and not os.getenv("LLM_BASE_URL"):
            base_url = "https://api.groq.com/openai/v1"
            model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")  # Updated to current model
        
        self.config = config or LLMConfig(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        
        if not self.config.api_key:
            logger.warning("No API key provided (neither GROQ_API_KEY nor OPENAI_API_KEY). LLM service will have limited functionality.")
    
    async def analyze_student_work(self, 
                                 content: str, 
                                 assignment_type: str = "essay",
                                 student_level: str = "5",
                                 subject: str = "engelska") -> Dict[str, Any]:
        """
        Comprehensive analysis of student work using LLM
        
        Args:
            content: Student's work content
            assignment_type: Type of assignment (essay, presentation, etc.)
            student_level: Student level (5, 6, etc.)
            subject: Subject (engelska, svenska, etc.)
        
        Returns:
            Comprehensive analysis result
        """
        try:
            prompt = self._build_analysis_prompt(content, assignment_type, student_level, subject)
            
            response = await self._call_llm(prompt, max_tokens=2000)
            
            if response:
                return self._parse_analysis_response(response, content)
            else:
                return self._fallback_analysis(content)
                
        except Exception as e:
            logger.error(f"Student work analysis failed: {e}")
            return self._fallback_analysis(content)
    
    async def generate_feedback(self, 
                              analysis: Dict[str, Any], 
                              student_id: str,
                              assignment_id: str) -> str:
        """
        Generate personalized feedback based on analysis
        
        Args:
            analysis: Analysis result from analyze_student_work
            student_id: Student identifier
            assignment_id: Assignment identifier
        
        Returns:
            Personalized feedback text
        """
        try:
            prompt = self._build_feedback_prompt(analysis, student_id, assignment_id)
            
            response = await self._call_llm(prompt, max_tokens=1500)
            
            if response:
                return response.strip()
            else:
                return self._generate_fallback_feedback(analysis)
                
        except Exception as e:
            logger.error(f"Feedback generation failed: {e}")
            return self._generate_fallback_feedback(analysis)
    
    async def suggest_improvements(self, 
                                 content: str, 
                                 current_level: str,
                                 target_level: str) -> List[str]:
        """
        Suggest specific improvements to reach target level
        
        Args:
            content: Student's work content
            current_level: Current assessed level (E, C, A)
            target_level: Target level to achieve
        
        Returns:
            List of specific improvement suggestions
        """
        try:
            prompt = self._build_improvement_prompt(content, current_level, target_level)
            
            response = await self._call_llm(prompt, max_tokens=1000)
            
            if response:
                return self._parse_improvement_response(response)
            else:
                return self._fallback_improvements(current_level, target_level)
                
        except Exception as e:
            logger.error(f"Improvement suggestions failed: {e}")
            return self._fallback_improvements(current_level, target_level)
    
    async def generate_questions(self, 
                               content: str, 
                               question_type: str = "comprehension",
                               difficulty: str = "medium") -> List[Dict[str, Any]]:
        """
        Generate questions based on content
        
        Args:
            content: Content to generate questions from
            question_type: Type of questions (comprehension, analysis, synthesis)
            difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            List of generated questions with answers
        """
        try:
            prompt = self._build_question_prompt(content, question_type, difficulty)
            
            response = await self._call_llm(prompt, max_tokens=1500)
            
            if response:
                return self._parse_question_response(response)
            else:
                return self._fallback_questions(content, question_type)
                
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return self._fallback_questions(content, question_type)
    
    async def summarize_content(self, 
                              content: str, 
                              summary_type: str = "key_points") -> str:
        """
        Generate content summary
        
        Args:
            content: Content to summarize
            summary_type: Type of summary (key_points, detailed, brief)
        
        Returns:
            Summary text
        """
        try:
            prompt = self._build_summary_prompt(content, summary_type)
            
            response = await self._call_llm(prompt, max_tokens=800)
            
            if response:
                return response.strip()
            else:
                return self._fallback_summary(content)
                
        except Exception as e:
            logger.error(f"Content summarization failed: {e}")
            return self._fallback_summary(content)
    
    async def translate_content(self, 
                              content: str, 
                              target_language: str = "swedish") -> str:
        """
        Translate content to target language
        
        Args:
            content: Content to translate
            target_language: Target language
        
        Returns:
            Translated content
        """
        try:
            prompt = f"Translate the following text to {target_language}. Maintain the original meaning and style:\n\n{content}"
            
            response = await self._call_llm(prompt, max_tokens=2000)
            
            if response:
                return response.strip()
            else:
                return content  # Return original if translation fails
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return content
    
    async def generate_text(self, 
                          prompt: str, 
                          max_tokens: int = 1000, 
                          temperature: float = 0.7) -> str:
        """
        Generate text using LLM with custom prompt
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0.0-1.0)
        
        Returns:
            Generated text
        """
        try:
            response = await self._call_llm(prompt, max_tokens, temperature)
            
            if response:
                return response.strip()
            else:
                return "Text generation failed - LLM service unavailable"
                
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return "Text generation failed due to error"
    
    async def _call_llm(self, prompt: str, max_tokens: int = None, temperature: float = None) -> Optional[str]:
        """Make API call to LLM (supports OpenAI, Ollama, Groq, etc.)"""
        # If no API key and base_url is OpenAI, skip (requires paid API)
        if not self.config.api_key and "openai.com" in self.config.base_url:
            logger.warning("No API key provided for OpenAI. Use Ollama or another free alternative.")
            return None
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                headers = {
                    "Content-Type": "application/json"
                }
                
                # Only add Authorization header if API key is provided (Ollama doesn't require it)
                if self.config.api_key and self.config.api_key != "ollama":
                    headers["Authorization"] = f"Bearer {self.config.api_key}"
                
                data = {
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": "Du är en expert på svensk gymnasieutbildning och Skolverkets Gy25-kriterier. Du hjälper lärare och elever med pedagogisk analys och feedback."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens or self.config.max_tokens,
                    "temperature": temperature or self.config.temperature
                }
                
                async with session.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"LLM API error: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None
    
    def _build_analysis_prompt(self, content: str, assignment_type: str, student_level: str, subject: str) -> str:
        """Build prompt for student work analysis"""
        return f"""
Analysera följande elevuppgift enligt Skolverkets Gy25-kriterier för {subject} nivå {student_level}:

UPPGIFTSTYP: {assignment_type}
ELEVENS ARBETE:
{content}

Ge en detaljerad analys som inkluderar:

1. NIVÅBEDÖMNING (E, C, eller A):
   - Motivera din bedömning baserat på Skolverkets Gy25-kriterier
   - Specificera vilka delar som stöder bedömningen

2. STYRKOR:
   - Lista 3-5 specifika styrkor i arbetet
   - Ge konkreta exempel från texten

3. FÖRBÄTTRINGSOMRÅDEN:
   - Identifiera 3-5 områden som behöver utveckling
   - Var specifik och konstruktiv

4. SPRÅKLIG ANALYS:
   - Ordförråd och språklig variation
   - Meningar och textstruktur
   - Grammatik och stavning

5. INNEHÅLLSANALYS:
   - Argumentation och logik
   - Exempel och bevisföring
   - Originalitet och kreativitet

6. GY25-KOPPLING:
   - Vilka delar av läroplanen uppfylls?
   - Vilka kunskapskrav nås?

Svara på svenska och var pedagogisk och konstruktiv.
"""
    
    def _build_feedback_prompt(self, analysis: Dict[str, Any], student_id: str, assignment_id: str) -> str:
        """Build prompt for feedback generation"""
        level = analysis.get('level', 'C')
        strengths = analysis.get('strengths', [])
        improvements = analysis.get('improvements', [])
        
        return f"""
Baserat på följande analys, skriv personlig feedback till elev {student_id} för uppgift {assignment_id}:

NIVÅ: {level}
STYRKOR: {', '.join(strengths[:3])}
FÖRBÄTTRINGSOMRÅDEN: {', '.join(improvements[:3])}

Skriv feedback som:
- Är personlig och uppmuntrande
- Fokuserar på utveckling och nästa steg
- Ger konkreta exempel och råd
- Är anpassad för {level}-nivån
- Följer Skolverkets pedagogiska principer

Längd: 150-300 ord
Ton: Positiv och konstruktiv
"""
    
    def _build_improvement_prompt(self, content: str, current_level: str, target_level: str) -> str:
        """Build prompt for improvement suggestions"""
        return f"""
Eleven har skrivit följande text som bedömts som {current_level}-nivå. 
Ge 5 specifika förslag för att nå {target_level}-nivån:

TEXT:
{content}

Ge konkreta, genomförbara förslag som:
- Är specifika och mätbara
- Fokuserar på de viktigaste förbättringsområdena
- Inkluderar exempel på hur eleven kan arbeta
- Är anpassade för elevens nuvarande nivå

Formatera som en numrerad lista.
"""
    
    def _build_question_prompt(self, content: str, question_type: str, difficulty: str) -> str:
        """Build prompt for question generation"""
        return f"""
Generera 5 {difficulty} {question_type}-frågor baserat på följande innehåll:

INNEHÅLL:
{content}

FRÅGETYPER:
- Förståelse: Vad, vem, när, var
- Analys: Hur, varför, jämför
- Syntes: Skapa, utveckla, kombinera

Svårighetsgrad: {difficulty}

Formatera som JSON med följande struktur:
[
  {{
    "question": "Frågan här",
    "answer": "Svaret här",
    "type": "comprehension/analysis/synthesis",
    "difficulty": "easy/medium/hard"
  }}
]
"""
    
    def _build_summary_prompt(self, content: str, summary_type: str) -> str:
        """Build prompt for content summarization"""
        type_instructions = {
            "key_points": "Sammanfatta de viktigaste punkterna i 3-5 punkter",
            "detailed": "Ge en detaljerad sammanfattning som behåller viktiga detaljer",
            "brief": "Ge en kort sammanfattning i 1-2 meningar"
        }
        
        instruction = type_instructions.get(summary_type, type_instructions["key_points"])
        
        return f"""
{instruction} av följande text:

{content}

Sammanfattningen ska vara:
- Tydlig och lättförståelig
- Bevara huvudbudskapet
- Använda elevens eget språk när möjligt
- Vara pedagogisk och hjälpsam
"""
    
    def _parse_analysis_response(self, response: str, content: str) -> Dict[str, Any]:
        """Parse LLM analysis response into structured format"""
        lines = response.split('\n')
        
        analysis = {
            'level': 'C',  # Default
            'strengths': [],
            'improvements': [],
            'language_analysis': {},
            'content_analysis': {},
            'gy25_connection': '',
            'confidence': 0.8,
            'raw_response': response,
            'word_count': len(content.split()),
            'analyzed_at': datetime.now().isoformat()
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'nivå' in line.lower() and ('E' in line or 'C' in line or 'A' in line):
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
            elif 'språk' in line.lower():
                current_section = 'language_analysis'
            elif 'innehåll' in line.lower():
                current_section = 'content_analysis'
            elif 'gy25' in line.lower() or 'gy11' in line.lower() or 'läroplan' in line.lower():
                current_section = 'gy25_connection'
            
            # Extract content
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                content_item = line[1:].strip()
                if current_section == 'strengths':
                    analysis['strengths'].append(content_item)
                elif current_section == 'improvements':
                    analysis['improvements'].append(content_item)
                elif current_section == 'gy25_connection':
                    analysis['gy25_connection'] += content_item + ' '
        
        return analysis
    
    def _parse_improvement_response(self, response: str) -> List[str]:
        """Parse improvement suggestions response"""
        lines = response.split('\n')
        improvements = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                clean_line = line
                if line[0].isdigit():
                    clean_line = line.split('.', 1)[1].strip() if '.' in line else line
                elif line.startswith('-') or line.startswith('•'):
                    clean_line = line[1:].strip()
                
                if clean_line:
                    improvements.append(clean_line)
        
        return improvements[:5]  # Limit to 5 suggestions
    
    def _parse_question_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse question generation response"""
        try:
            # Try to parse as JSON
            questions = json.loads(response)
            if isinstance(questions, list):
                return questions
        except:
            pass
        
        # Fallback: parse as text
        questions = []
        lines = response.split('\n')
        current_question = {}
        
        for line in lines:
            line = line.strip()
            if 'question' in line.lower() or 'fråga' in line.lower():
                if current_question:
                    questions.append(current_question)
                current_question = {'question': line, 'answer': '', 'type': 'comprehension', 'difficulty': 'medium'}
            elif 'answer' in line.lower() or 'svar' in line.lower():
                if current_question:
                    current_question['answer'] = line
        
        if current_question:
            questions.append(current_question)
        
        return questions[:5]  # Limit to 5 questions
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available"""
        words = content.split()
        word_count = len(words)
        sentences = content.split('.')
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
            'language_analysis': {
                'word_count': word_count,
                'avg_sentence_length': avg_sentence_length,
                'vocabulary_level': 'basic' if word_count < 200 else 'intermediate' if word_count < 400 else 'advanced'
            },
            'content_analysis': {
                'structure': 'basic' if word_count < 200 else 'good',
                'argumentation': 'limited' if word_count < 200 else 'developing'
            },
            'gy25_connection': f"Texten följer grundläggande struktur för Engelska 5",
            'confidence': 0.6,
            'raw_response': f"Heuristik-analys: {level}-nivå baserat på längd och struktur",
            'word_count': word_count,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _generate_fallback_feedback(self, analysis: Dict[str, Any]) -> str:
        """Generate fallback feedback when LLM is not available"""
        level = analysis.get('level', 'C')
        strengths = analysis.get('strengths', [])
        improvements = analysis.get('improvements', [])
        
        feedback = f"Denna text når {level}-nivå enligt Skolverkets Gy25-kriterier.\n\n"
        
        if strengths:
            feedback += "Styrkor:\n"
            for strength in strengths[:3]:
                feedback += f"• {strength}\n"
            feedback += "\n"
        
        if improvements:
            feedback += "Förbättringsområden:\n"
            for improvement in improvements[:3]:
                feedback += f"• {improvement}\n"
        
        return feedback
    
    def _fallback_improvements(self, current_level: str, target_level: str) -> List[str]:
        """Fallback improvement suggestions"""
        improvements = {
            ('E', 'C'): [
                "Utveckla dina argument mer detaljerat",
                "Använd längre och mer varierade meningar",
                "Lägg till exempel som stöder dina påståenden",
                "Förklara dina tankar mer utförligt",
                "Kontrollera stavning och grammatik"
            ],
            ('C', 'A'): [
                "Utveckla mer sofistikerade analyser",
                "Använd mer avancerat språk och längre meningar",
                "Visa djupare kritiskt tänkande med flera perspektiv",
                "Experimentera med olika skrivtekniker",
                "Utveckla dina analytiska färdigheter"
            ]
        }
        
        return improvements.get((current_level, target_level), [
            "Fortsätt att utveckla dina skrivfärdigheter",
            "Läs mer för att utöka ditt ordförråd",
            "Öva på att strukturera dina texter bättre"
        ])
    
    def _fallback_questions(self, content: str, question_type: str) -> List[Dict[str, Any]]:
        """Fallback question generation"""
        return [
            {
                "question": "Vad är huvudtemat i denna text?",
                "answer": "Huvudtemat behöver identifieras baserat på innehållet",
                "type": "comprehension",
                "difficulty": "easy"
            },
            {
                "question": "Hur försöker författaren övertyga läsaren?",
                "answer": "Analysera argumentationen och bevisföringen",
                "type": "analysis",
                "difficulty": "medium"
            }
        ]
    
    def _fallback_summary(self, content: str) -> str:
        """Fallback content summary"""
        words = content.split()
        if len(words) > 100:
            return f"Texten handlar om {content[:200]}... och innehåller {len(words)} ord."
        else:
            return content

# Global instance
llm_service = LLMService()
