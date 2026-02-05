"""
AI Analysis Service for Genassista EDU
Comprehensive AI-powered analysis of student work with educational focus
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime
import json

from .llm_service import llm_service
from .rag_service import rag_service
from .document_service import document_processor

logger = logging.getLogger("Genassista-EDU-pythonAPI.ai_analysis")

class AIAnalysisService:
    """Comprehensive AI analysis service for educational content"""
    
    def __init__(self):
        self.llm = llm_service
        self.rag = rag_service
        self.doc_processor = document_processor
    
    async def analyze_student_submission(self, 
                                       content: str,
                                       submission_type: str = "essay",
                                       student_id: str = None,
                                       assignment_id: str = None,
                                       subject: str = "engelska",
                                       level: str = "5") -> Dict[str, Any]:
        """
        Comprehensive analysis of student submission
        
        Args:
            content: Student's submission content
            submission_type: Type of submission (essay, presentation, etc.)
            student_id: Student identifier
            assignment_id: Assignment identifier
            subject: Subject (engelska, svenska, etc.)
            level: Student level (5, 6, etc.)
        
        Returns:
            Comprehensive analysis result
        """
        try:
            # Start multiple analysis tasks in parallel
            tasks = [
                self._analyze_content_quality(content, submission_type, subject, level),
                self._analyze_language_skills(content, subject, level),
                self._analyze_critical_thinking(content, subject, level),
                self._analyze_creativity(content, submission_type),
                self._analyze_gy25_compliance(content, subject, level)
            ]
            
            # Wait for all analyses to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            analysis = {
                'submission_id': f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'student_id': student_id,
                'assignment_id': assignment_id,
                'submission_type': submission_type,
                'subject': subject,
                'level': level,
                'analyzed_at': datetime.now().isoformat(),
                'content_quality': results[0] if not isinstance(results[0], Exception) else {},
                'language_skills': results[1] if not isinstance(results[1], Exception) else {},
                'critical_thinking': results[2] if not isinstance(results[2], Exception) else {},
                'creativity': results[3] if not isinstance(results[3], Exception) else {},
                'gy25_compliance': results[4] if not isinstance(results[4], Exception) else {},
                'overall_assessment': {},
                'recommendations': [],
                'next_steps': []
            }
            
            # Generate overall assessment
            analysis['overall_assessment'] = await self._generate_overall_assessment(analysis)
            
            # Generate recommendations
            analysis['recommendations'] = await self._generate_recommendations(analysis)
            
            # Generate next steps
            analysis['next_steps'] = await self._generate_next_steps(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(content, submission_type, subject, level)
    
    async def _analyze_content_quality(self, content: str, submission_type: str, subject: str, level: str) -> Dict[str, Any]:
        """Analyze content quality and structure"""
        try:
            # Use LLM for content analysis
            analysis = await self.llm.analyze_student_work(content, submission_type, level, subject)
            
            # Extract content-specific metrics
            words = content.split()
            sentences = content.split('.')
            paragraphs = content.split('\n\n')
            
            return {
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'paragraph_count': len([p for p in paragraphs if p.strip()]),
                'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
                'avg_words_per_paragraph': len(words) / len(paragraphs) if paragraphs else 0,
                'structure_quality': analysis.get('content_analysis', {}).get('structure', 'basic'),
                'argumentation_quality': analysis.get('content_analysis', {}).get('argumentation', 'limited'),
                'coherence_score': self._calculate_coherence_score(content),
                'completeness_score': self._calculate_completeness_score(content, submission_type),
                'llm_analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Content quality analysis failed: {e}")
            return self._fallback_content_analysis(content)
    
    async def _analyze_language_skills(self, content: str, subject: str, level: str) -> Dict[str, Any]:
        """Analyze language skills and proficiency"""
        try:
            # Basic language metrics
            words = content.split()
            unique_words = set(word.lower().strip('.,!?;:"') for word in words)
            
            # Vocabulary analysis
            vocabulary_richness = len(unique_words) / len(words) if words else 0
            
            # Sentence complexity
            sentences = content.split('.')
            complex_sentences = [s for s in sentences if len(s.split()) > 15]
            sentence_complexity = len(complex_sentences) / len(sentences) if sentences else 0
            
            # Language level assessment
            language_level = self._assess_language_level(content, vocabulary_richness, sentence_complexity)
            
            return {
                'vocabulary_richness': vocabulary_richness,
                'sentence_complexity': sentence_complexity,
                'language_level': language_level,
                'grammar_issues': self._identify_grammar_issues(content),
                'spelling_issues': self._identify_spelling_issues(content),
                'style_consistency': self._assess_style_consistency(content),
                'word_diversity': len(unique_words),
                'total_words': len(words)
            }
            
        except Exception as e:
            logger.error(f"Language skills analysis failed: {e}")
            return self._fallback_language_analysis(content)
    
    async def _analyze_critical_thinking(self, content: str, subject: str, level: str) -> Dict[str, Any]:
        """Analyze critical thinking skills"""
        try:
            # Look for critical thinking indicators
            critical_indicators = {
                'questioning': self._count_question_words(content),
                'analysis': self._count_analysis_words(content),
                'evaluation': self._count_evaluation_words(content),
                'synthesis': self._count_synthesis_words(content),
                'evidence': self._count_evidence_words(content),
                'perspectives': self._count_perspective_words(content)
            }
            
            # Calculate critical thinking score
            total_indicators = sum(critical_indicators.values())
            critical_thinking_score = min(total_indicators / 10, 1.0)  # Normalize to 0-1
            
            return {
                'critical_thinking_score': critical_thinking_score,
                'indicators': critical_indicators,
                'analysis_depth': self._assess_analysis_depth(content),
                'evidence_quality': self._assess_evidence_quality(content),
                'perspective_taking': self._assess_perspective_taking(content),
                'logical_reasoning': self._assess_logical_reasoning(content)
            }
            
        except Exception as e:
            logger.error(f"Critical thinking analysis failed: {e}")
            return self._fallback_critical_thinking_analysis(content)
    
    async def _analyze_creativity(self, content: str, submission_type: str) -> Dict[str, Any]:
        """Analyze creativity and originality"""
        try:
            # Creativity indicators
            creativity_indicators = {
                'original_phrases': self._count_original_phrases(content),
                'metaphors_similes': self._count_figurative_language(content),
                'unique_perspectives': self._count_unique_perspectives(content),
                'creative_vocabulary': self._count_creative_vocabulary(content),
                'narrative_elements': self._count_narrative_elements(content)
            }
            
            # Calculate creativity score
            total_creativity = sum(creativity_indicators.values())
            creativity_score = min(total_creativity / 20, 1.0)  # Normalize to 0-1
            
            return {
                'creativity_score': creativity_score,
                'indicators': creativity_indicators,
                'originality_level': self._assess_originality(content),
                'imagination_use': self._assess_imagination_use(content),
                'artistic_expression': self._assess_artistic_expression(content, submission_type)
            }
            
        except Exception as e:
            logger.error(f"Creativity analysis failed: {e}")
            return self._fallback_creativity_analysis(content)
    
    async def _analyze_gy25_compliance(self, content: str, subject: str, level: str) -> Dict[str, Any]:
        """Analyze compliance with Gy25 curriculum"""
        try:
            # Search knowledge base for relevant criteria
            knowledge_results = await self.rag.search_knowledge(
                query=content,
                subject=subject,
                level=level
            )
            
            # Analyze against Gy25 criteria
            compliance_analysis = {
                'knowledge_base_relevance': len(knowledge_results),
                'curriculum_alignment': self._assess_curriculum_alignment(content, subject, level),
                'learning_objectives_met': self._assess_learning_objectives(content, subject, level),
                'assessment_criteria_met': self._assess_assessment_criteria(content, subject, level),
                'pedagogical_value': self._assess_pedagogical_value(content, subject, level),
                'knowledge_used': knowledge_results[:3]  # Top 3 most relevant
            }
            
            return compliance_analysis
            
        except Exception as e:
            logger.error(f"Gy25 compliance analysis failed: {e}")
            return self._fallback_gy25_analysis(content, subject, level)
    
    async def _generate_overall_assessment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment based on all analyses"""
        try:
            # Calculate overall scores
            content_score = analysis['content_quality'].get('coherence_score', 0.5)
            language_score = analysis['language_skills'].get('language_level', 0.5)
            critical_score = analysis['critical_thinking'].get('critical_thinking_score', 0.5)
            creativity_score = analysis['creativity'].get('creativity_score', 0.5)
            gy25_score = analysis['gy25_compliance'].get('curriculum_alignment', 0.5)
            
            # Weighted overall score
            overall_score = (
                content_score * 0.25 +
                language_score * 0.25 +
                critical_score * 0.20 +
                creativity_score * 0.15 +
                gy25_score * 0.15
            )
            
            # Determine level (convert to grade suggestion format)
            if overall_score >= 0.8:
                level = 'A'
                grade_suggestion = 'A/B'  # Always return as suggestion, never direct grade
            elif overall_score >= 0.6:
                level = 'C'
                grade_suggestion = 'C/D'  # Always return as suggestion, never direct grade
            else:
                level = 'E'
                grade_suggestion = 'E/D'  # Always return as suggestion, never direct grade
            
            return {
                'overall_score': overall_score,
                'assessed_level': level,
                'grade_suggestion': grade_suggestion,  # Always a suggestion like "C/D", never direct grade
                'strengths': self._identify_overall_strengths(analysis),
                'areas_for_improvement': self._identify_improvement_areas(analysis),
                'confidence': self._calculate_assessment_confidence(analysis)
            }
            
        except Exception as e:
            logger.error(f"Overall assessment generation failed: {e}")
            return self._fallback_overall_assessment()
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific recommendations for improvement"""
        try:
            recommendations = []
            
            # Content recommendations
            if analysis['content_quality'].get('coherence_score', 0) < 0.6:
                recommendations.append({
                    'category': 'content',
                    'priority': 'high',
                    'recommendation': 'Förbättra textens struktur och sammanhang',
                    'specific_actions': [
                        'Använd tydliga övergångar mellan paragrafen',
                        'Skapa en logisk följd i dina argument',
                        'Använd rubriker eller inledande meningar för varje avsnitt'
                    ]
                })
            
            # Language recommendations
            if analysis['language_skills'].get('language_level', 0) < 0.6:
                recommendations.append({
                    'category': 'language',
                    'priority': 'medium',
                    'recommendation': 'Utveckla ditt språk och ordförråd',
                    'specific_actions': [
                        'Läs mer för att utöka ditt ordförråd',
                        'Använd varierade meningar',
                        'Kontrollera stavning och grammatik'
                    ]
                })
            
            # Critical thinking recommendations
            if analysis['critical_thinking'].get('critical_thinking_score', 0) < 0.6:
                recommendations.append({
                    'category': 'critical_thinking',
                    'priority': 'high',
                    'recommendation': 'Utveckla ditt kritiska tänkande',
                    'specific_actions': [
                        'Ställ fler frågor om ämnet',
                        'Jämför olika perspektiv',
                        'Använd bevis för att stödja dina argument'
                    ]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return self._fallback_recommendations()
    
    async def _generate_next_steps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate next steps for student development"""
        try:
            next_steps = []
            
            # Immediate next steps
            next_steps.append({
                'timeline': 'immediate',
                'action': 'Granska feedbacken och identifiera huvudområden för förbättring',
                'resources': ['Lärarens kommentarer', 'Bedömningskriterier', 'Exempel på bra texter']
            })
            
            # Short-term steps (1-2 weeks)
            next_steps.append({
                'timeline': 'short_term',
                'action': 'Arbeta med de specifika förbättringsområdena',
                'resources': ['Skrivövningar', 'Språkutvecklingsmaterial', 'Peer feedback']
            })
            
            # Long-term steps (1 month+)
            next_steps.append({
                'timeline': 'long_term',
                'action': 'Fortsätt utveckla dina skrivfärdigheter och kritiska tänkande',
                'resources': ['Läsning av olika genrer', 'Skrivworkshops', 'Självreflektion']
            })
            
            return next_steps
            
        except Exception as e:
            logger.error(f"Next steps generation failed: {e}")
            return self._fallback_next_steps()
    
    # Helper methods for analysis
    def _calculate_coherence_score(self, content: str) -> float:
        """Calculate text coherence score"""
        # Simple coherence calculation based on transition words and sentence connections
        transition_words = ['men', 'dock', 'därför', 'således', 'dessutom', 'för det första', 'för det andra']
        sentences = content.split('.')
        
        if len(sentences) < 2:
            return 0.5
        
        transition_count = sum(1 for word in transition_words if word in content.lower())
        coherence_score = min(transition_count / len(sentences), 1.0)
        
        return coherence_score
    
    def _calculate_completeness_score(self, content: str, submission_type: str) -> float:
        """Calculate content completeness score"""
        word_count = len(content.split())
        
        # Expected word counts for different submission types
        expected_counts = {
            'essay': 300,
            'short_answer': 50,
            'presentation': 200,
            'report': 500
        }
        
        expected = expected_counts.get(submission_type, 200)
        completeness = min(word_count / expected, 1.0)
        
        return completeness
    
    def _assess_language_level(self, content: str, vocabulary_richness: float, sentence_complexity: float) -> float:
        """Assess overall language level"""
        # Combine vocabulary richness and sentence complexity
        language_level = (vocabulary_richness + sentence_complexity) / 2
        return min(language_level, 1.0)
    
    def _identify_grammar_issues(self, content: str) -> List[str]:
        """Identify potential grammar issues"""
        issues = []
        
        # Simple grammar checks
        if 'är är' in content.lower():
            issues.append('Dubbel verbform')
        if 'och och' in content.lower():
            issues.append('Dubbel konjunktion')
        
        return issues
    
    def _identify_spelling_issues(self, content: str) -> List[str]:
        """Identify potential spelling issues"""
        # This would typically use a spell checker
        # For now, return empty list
        return []
    
    def _assess_style_consistency(self, content: str) -> float:
        """Assess writing style consistency"""
        # Simple style consistency check
        sentences = content.split('.')
        if len(sentences) < 2:
            return 0.5
        
        # Check for consistent sentence length
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if not lengths:
            return 0.5
        
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        consistency = 1.0 - min(variance / (avg_length ** 2), 1.0)
        
        return consistency
    
    def _count_question_words(self, content: str) -> int:
        """Count question words indicating critical thinking"""
        question_words = ['varför', 'hur', 'vad', 'när', 'var', 'vem', 'vilken', 'vilka']
        return sum(1 for word in question_words if word in content.lower())
    
    def _count_analysis_words(self, content: str) -> int:
        """Count analysis-related words"""
        analysis_words = ['analysera', 'undersöka', 'jämföra', 'utvärdera', 'bedöma', 'granska']
        return sum(1 for word in analysis_words if word in content.lower())
    
    def _count_evaluation_words(self, content: str) -> int:
        """Count evaluation-related words"""
        evaluation_words = ['värdera', 'bedöma', 'kritisera', 'granska', 'utvärdera', 'analysera']
        return sum(1 for word in evaluation_words if word in content.lower())
    
    def _count_synthesis_words(self, content: str) -> int:
        """Count synthesis-related words"""
        synthesis_words = ['kombinera', 'sammanfatta', 'syntetisera', 'integrera', 'förena', 'skapa']
        return sum(1 for word in synthesis_words if word in content.lower())
    
    def _count_evidence_words(self, content: str) -> int:
        """Count evidence-related words"""
        evidence_words = ['bevis', 'exempel', 'data', 'statistik', 'källa', 'referens']
        return sum(1 for word in evidence_words if word in content.lower())
    
    def _count_perspective_words(self, content: str) -> int:
        """Count perspective-taking words"""
        perspective_words = ['perspektiv', 'synvinkel', 'åsikt', 'ståndpunkt', 'hållning', 'uppfattning']
        return sum(1 for word in perspective_words if word in content.lower())
    
    def _assess_analysis_depth(self, content: str) -> float:
        """Assess depth of analysis"""
        # Simple analysis depth assessment
        analysis_indicators = self._count_analysis_words(content) + self._count_evaluation_words(content)
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        depth_score = min(analysis_indicators / (word_count / 100), 1.0)
        return depth_score
    
    def _assess_evidence_quality(self, content: str) -> float:
        """Assess quality of evidence used"""
        evidence_count = self._count_evidence_words(content)
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        evidence_score = min(evidence_count / (word_count / 200), 1.0)
        return evidence_score
    
    def _assess_perspective_taking(self, content: str) -> float:
        """Assess ability to consider multiple perspectives"""
        perspective_count = self._count_perspective_words(content)
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        perspective_score = min(perspective_count / (word_count / 300), 1.0)
        return perspective_score
    
    def _assess_logical_reasoning(self, content: str) -> float:
        """Assess logical reasoning ability"""
        logical_words = ['därför', 'således', 'följaktligen', 'alltså', 'med andra ord', 'detta betyder']
        logical_count = sum(1 for word in logical_words if word in content.lower())
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        reasoning_score = min(logical_count / (word_count / 200), 1.0)
        return reasoning_score
    
    def _count_original_phrases(self, content: str) -> int:
        """Count original or creative phrases"""
        # Simple originality check - count unique phrases
        sentences = content.split('.')
        unique_phrases = set(s.strip().lower() for s in sentences if s.strip())
        return len(unique_phrases)
    
    def _count_figurative_language(self, content: str) -> int:
        """Count metaphors, similes, and other figurative language"""
        figurative_indicators = ['som', 'liknar', 'minns', 'bildligt', 'metafor', 'liknelse']
        return sum(1 for indicator in figurative_indicators if indicator in content.lower())
    
    def _count_unique_perspectives(self, content: str) -> int:
        """Count unique perspectives or viewpoints"""
        perspective_indicators = ['jag tycker', 'enligt min åsikt', 'från min synvinkel', 'personligen']
        return sum(1 for indicator in perspective_indicators if indicator in content.lower())
    
    def _count_creative_vocabulary(self, content: str) -> int:
        """Count creative or advanced vocabulary"""
        # Simple creative vocabulary check
        words = content.split()
        creative_words = [word for word in words if len(word) > 8 and word.isalpha()]
        return len(creative_words)
    
    def _count_narrative_elements(self, content: str) -> int:
        """Count narrative or storytelling elements"""
        narrative_indicators = ['först', 'sedan', 'slutligen', 'under tiden', 'medan', 'när']
        return sum(1 for indicator in narrative_indicators if indicator in content.lower())
    
    def _assess_originality(self, content: str) -> float:
        """Assess overall originality"""
        originality_indicators = (
            self._count_original_phrases(content) +
            self._count_figurative_language(content) +
            self._count_unique_perspectives(content)
        )
        
        word_count = len(content.split())
        if word_count == 0:
            return 0.0
        
        originality_score = min(originality_indicators / (word_count / 100), 1.0)
        return originality_score
    
    def _assess_imagination_use(self, content: str) -> float:
        """Assess use of imagination"""
        imagination_indicators = ['fantasi', 'föreställa', 'tänka sig', 'drömma', 'kreativ', 'originell']
        imagination_count = sum(1 for indicator in imagination_indicators if indicator in content.lower())
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        imagination_score = min(imagination_count / (word_count / 200), 1.0)
        return imagination_score
    
    def _assess_artistic_expression(self, content: str, submission_type: str) -> float:
        """Assess artistic expression based on submission type"""
        if submission_type in ['essay', 'creative_writing', 'poetry']:
            artistic_indicators = ['bildligt', 'metafor', 'liknelse', 'kreativ', 'konstnärlig']
            artistic_count = sum(1 for indicator in artistic_indicators if indicator in content.lower())
            word_count = len(content.split())
            
            if word_count == 0:
                return 0.0
            
            artistic_score = min(artistic_count / (word_count / 150), 1.0)
            return artistic_score
        
        return 0.5  # Neutral score for non-artistic submissions
    
    def _assess_curriculum_alignment(self, content: str, subject: str, level: str) -> float:
        """Assess alignment with curriculum"""
        # Simple curriculum alignment check
        curriculum_keywords = {
            'engelska': ['english', 'british', 'american', 'literature', 'culture', 'language'],
            'svenska': ['svensk', 'litteratur', 'kultur', 'språk', 'historia'],
            'matematik': ['ekvation', 'funktion', 'geometri', 'algebra', 'statistik']
        }
        
        keywords = curriculum_keywords.get(subject, [])
        if not keywords:
            return 0.5
        
        keyword_count = sum(1 for keyword in keywords if keyword in content.lower())
        alignment_score = min(keyword_count / len(keywords), 1.0)
        
        return alignment_score
    
    def _assess_learning_objectives(self, content: str, subject: str, level: str) -> float:
        """Assess achievement of learning objectives"""
        # Simple learning objectives assessment
        objective_indicators = ['förstår', 'kan förklara', 'analyserar', 'jämför', 'utvärderar']
        objective_count = sum(1 for indicator in objective_indicators if indicator in content.lower())
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        objective_score = min(objective_count / (word_count / 200), 1.0)
        return objective_score
    
    def _assess_assessment_criteria(self, content: str, subject: str, level: str) -> float:
        """Assess meeting of assessment criteria"""
        # Simple assessment criteria check
        criteria_indicators = ['tydligt', 'strukturerat', 'logiskt', 'bevisat', 'motiverat']
        criteria_count = sum(1 for indicator in criteria_indicators if indicator in content.lower())
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        criteria_score = min(criteria_count / (word_count / 150), 1.0)
        return criteria_score
    
    def _assess_pedagogical_value(self, content: str, subject: str, level: str) -> float:
        """Assess pedagogical value of the content"""
        # Simple pedagogical value assessment
        pedagogical_indicators = ['lär', 'utvecklar', 'förstår', 'reflekterar', 'tänker']
        pedagogical_count = sum(1 for indicator in pedagogical_indicators if indicator in content.lower())
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        pedagogical_score = min(pedagogical_count / (word_count / 250), 1.0)
        return pedagogical_score
    
    def _identify_overall_strengths(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify overall strengths from analysis"""
        strengths = []
        
        if analysis['content_quality'].get('coherence_score', 0) > 0.7:
            strengths.append('Tydlig textstruktur och sammanhang')
        
        if analysis['language_skills'].get('language_level', 0) > 0.7:
            strengths.append('Utvecklat språk och ordförråd')
        
        if analysis['critical_thinking'].get('critical_thinking_score', 0) > 0.7:
            strengths.append('Gott kritiskt tänkande')
        
        if analysis['creativity'].get('creativity_score', 0) > 0.7:
            strengths.append('Kreativt och originellt innehåll')
        
        return strengths
    
    def _identify_improvement_areas(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement from analysis"""
        improvements = []
        
        if analysis['content_quality'].get('coherence_score', 0) < 0.6:
            improvements.append('Förbättra textens struktur och sammanhang')
        
        if analysis['language_skills'].get('language_level', 0) < 0.6:
            improvements.append('Utveckla språk och ordförråd')
        
        if analysis['critical_thinking'].get('critical_thinking_score', 0) < 0.6:
            improvements.append('Utveckla kritiskt tänkande')
        
        if analysis['creativity'].get('creativity_score', 0) < 0.6:
            improvements.append('Öka kreativitet och originalitet')
        
        return improvements
    
    def _calculate_assessment_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence in the assessment"""
        # Simple confidence calculation based on data quality
        confidence_factors = []
        
        # Content quality confidence
        if analysis['content_quality'].get('word_count', 0) > 100:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Language analysis confidence
        if analysis['language_skills'].get('total_words', 0) > 50:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Overall confidence
        confidence = sum(confidence_factors) / len(confidence_factors)
        return confidence
    
    # Fallback methods
    def _fallback_analysis(self, content: str, submission_type: str, subject: str, level: str) -> Dict[str, Any]:
        """Fallback analysis when AI services fail"""
        return {
            'submission_id': f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'submission_type': submission_type,
            'subject': subject,
            'level': level,
            'analyzed_at': datetime.now().isoformat(),
            'content_quality': self._fallback_content_analysis(content),
            'language_skills': self._fallback_language_analysis(content),
            'critical_thinking': self._fallback_critical_thinking_analysis(content),
            'creativity': self._fallback_creativity_analysis(content),
            'gy25_compliance': self._fallback_gy25_analysis(content, subject, level),
            'overall_assessment': self._fallback_overall_assessment(),
            'recommendations': self._fallback_recommendations(),
            'next_steps': self._fallback_next_steps()
        }
    
    def _fallback_content_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback content analysis"""
        words = content.split()
        return {
            'word_count': len(words),
            'sentence_count': len(content.split('.')),
            'coherence_score': 0.5,
            'completeness_score': 0.5,
            'structure_quality': 'basic',
            'argumentation_quality': 'limited'
        }
    
    def _fallback_language_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback language analysis"""
        words = content.split()
        return {
            'vocabulary_richness': 0.5,
            'sentence_complexity': 0.5,
            'language_level': 0.5,
            'grammar_issues': [],
            'spelling_issues': [],
            'style_consistency': 0.5,
            'word_diversity': len(set(words)),
            'total_words': len(words)
        }
    
    def _fallback_critical_thinking_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback critical thinking analysis"""
        return {
            'critical_thinking_score': 0.5,
            'indicators': {},
            'analysis_depth': 0.5,
            'evidence_quality': 0.5,
            'perspective_taking': 0.5,
            'logical_reasoning': 0.5
        }
    
    def _fallback_creativity_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback creativity analysis"""
        return {
            'creativity_score': 0.5,
            'indicators': {},
            'originality_level': 0.5,
            'imagination_use': 0.5,
            'artistic_expression': 0.5
        }
    
    def _fallback_gy25_analysis(self, content: str, subject: str, level: str) -> Dict[str, Any]:
        """Fallback Gy25 analysis"""
        return {
            'knowledge_base_relevance': 0,
            'curriculum_alignment': 0.5,
            'learning_objectives_met': 0.5,
            'assessment_criteria_met': 0.5,
            'pedagogical_value': 0.5,
            'knowledge_used': []
        }
    
    def _fallback_overall_assessment(self) -> Dict[str, Any]:
        """Fallback overall assessment"""
        return {
            'overall_score': 0.5,
            'assessed_level': 'C',
            'grade_suggestion': 'C/D',  # Always a suggestion, never direct grade
            'strengths': ['Grundläggande förståelse'],
            'areas_for_improvement': ['Utveckla argumentation'],
            'confidence': 0.6
        }
    
    def _fallback_recommendations(self) -> List[Dict[str, Any]]:
        """Fallback recommendations"""
        return [
            {
                'category': 'general',
                'priority': 'medium',
                'recommendation': 'Fortsätt utveckla dina skrivfärdigheter',
                'specific_actions': ['Läs mer', 'Öva på att skriva', 'Sök feedback']
            }
        ]
    
    def _fallback_next_steps(self) -> List[Dict[str, Any]]:
        """Fallback next steps"""
        return [
            {
                'timeline': 'immediate',
                'action': 'Granska feedbacken',
                'resources': ['Lärarens kommentarer']
            }
        ]

# Global instance
ai_analysis_service = AIAnalysisService()
