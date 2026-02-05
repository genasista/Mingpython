"""
Feedback Service for Genassista EDU
Comprehensive feedback generation system for educational content
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime
import json

from .llm_service import llm_service
from .ai_analysis_service import ai_analysis_service

logger = logging.getLogger("Genassista-EDU-pythonAPI.feedback")

class FeedbackService:
    """Comprehensive feedback generation service for educational content"""
    
    def __init__(self):
        self.llm = llm_service
        self.ai_analysis = ai_analysis_service
    
    async def generate_comprehensive_feedback(self, 
                                            content: str,
                                            student_id: str,
                                            assignment_id: str,
                                            submission_type: str = "essay",
                                            subject: str = "engelska",
                                            level: str = "5") -> Dict[str, Any]:
        """
        Generate comprehensive feedback for student work
        
        Args:
            content: Student's work content
            student_id: Student identifier
            assignment_id: Assignment identifier
            submission_type: Type of submission
            subject: Subject area
            level: Student level
        
        Returns:
            Comprehensive feedback package
        """
        try:
            # Get AI analysis
            analysis = await self.ai_analysis.analyze_student_submission(
                content=content,
                submission_type=submission_type,
                student_id=student_id,
                assignment_id=assignment_id,
                subject=subject,
                level=level
            )
            
            # Generate different types of feedback
            feedback_tasks = [
                self._generate_teacher_feedback(analysis),
                self._generate_student_feedback(analysis),
                self._generate_parent_feedback(analysis),
                self._generate_peer_feedback(analysis),
                self._generate_self_reflection_questions(analysis)
            ]
            
            # Wait for all feedback generation to complete
            feedback_results = await asyncio.gather(*feedback_tasks, return_exceptions=True)
            
            # Combine all feedback
            comprehensive_feedback = {
                'feedback_id': f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'student_id': student_id,
                'assignment_id': assignment_id,
                'submission_type': submission_type,
                'subject': subject,
                'level': level,
                'generated_at': datetime.now().isoformat(),
                'analysis': analysis,
                'teacher_feedback': feedback_results[0] if not isinstance(feedback_results[0], Exception) else {},
                'student_feedback': feedback_results[1] if not isinstance(feedback_results[1], Exception) else {},
                'parent_feedback': feedback_results[2] if not isinstance(feedback_results[2], Exception) else {},
                'peer_feedback': feedback_results[3] if not isinstance(feedback_results[3], Exception) else {},
                'self_reflection': feedback_results[4] if not isinstance(feedback_results[4], Exception) else {},
                'action_plan': await self._generate_action_plan(analysis),
                'progress_tracking': await self._generate_progress_tracking(analysis),
                'resources': await self._generate_learning_resources(analysis)
            }
            
            return comprehensive_feedback
            
        except Exception as e:
            logger.error(f"Comprehensive feedback generation failed: {e}")
            return self._fallback_feedback(content, student_id, assignment_id)
    
    async def _generate_teacher_feedback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback for teachers"""
        try:
            # Use LLM to generate teacher-specific feedback
            prompt = self._build_teacher_feedback_prompt(analysis)
            feedback_text = await self.llm._call_llm(prompt, max_tokens=2000)  # Ökad för mer detaljerad feedback
            
            if not feedback_text:
                feedback_text = self._fallback_teacher_feedback(analysis)
            
            return {
                'type': 'teacher',
                'content': feedback_text,
                'assessment_level': analysis['overall_assessment'].get('assessed_level', 'C'),
                'key_strengths': analysis['overall_assessment'].get('strengths', []),
                'improvement_areas': analysis['overall_assessment'].get('areas_for_improvement', []),
                'recommendations': analysis.get('recommendations', []),
                'next_steps': analysis.get('next_steps', []),
                'confidence': analysis['overall_assessment'].get('confidence', 0.5)
            }
            
        except Exception as e:
            logger.error(f"Teacher feedback generation failed: {e}")
            return self._fallback_teacher_feedback(analysis)
    
    async def _generate_student_feedback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback for students"""
        try:
            # Use LLM to generate student-friendly feedback
            prompt = self._build_student_feedback_prompt(analysis)
            feedback_text = await self.llm._call_llm(prompt, max_tokens=1500)  # Ökad för mer detaljerad feedback
            
            if not feedback_text:
                feedback_text = self._fallback_student_feedback(analysis)
            
            return {
                'type': 'student',
                'content': feedback_text,
                'level': analysis['overall_assessment'].get('assessed_level', 'C'),
                'strengths': self._extract_student_strengths(analysis),
                'improvements': self._extract_student_improvements(analysis),
                'encouragement': self._generate_encouragement(analysis),
                'specific_actions': self._extract_specific_actions(analysis)
            }
            
        except Exception as e:
            logger.error(f"Student feedback generation failed: {e}")
            return self._fallback_student_feedback(analysis)
    
    async def _generate_parent_feedback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback for parents"""
        try:
            # Use LLM to generate parent-friendly feedback
            prompt = self._build_parent_feedback_prompt(analysis)
            feedback_text = await self.llm._call_llm(prompt, max_tokens=600)
            
            if not feedback_text:
                feedback_text = self._fallback_parent_feedback(analysis)
            
            return {
                'type': 'parent',
                'content': feedback_text,
                'child_progress': self._assess_child_progress(analysis),
                'strengths': self._extract_parent_strengths(analysis),
                'areas_to_support': self._extract_areas_to_support(analysis),
                'home_support': self._generate_home_support_suggestions(analysis),
                'communication': self._generate_communication_guidance(analysis)
            }
            
        except Exception as e:
            logger.error(f"Parent feedback generation failed: {e}")
            return self._fallback_parent_feedback(analysis)
    
    async def _generate_peer_feedback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate peer feedback guidelines"""
        try:
            # Use LLM to generate peer feedback guidelines
            prompt = self._build_peer_feedback_prompt(analysis)
            feedback_text = await self.llm._call_llm(prompt, max_tokens=500)
            
            if not feedback_text:
                feedback_text = self._fallback_peer_feedback(analysis)
            
            return {
                'type': 'peer',
                'content': feedback_text,
                'focus_areas': self._extract_peer_focus_areas(analysis),
                'questions_to_ask': self._generate_peer_questions(analysis),
                'positive_comments': self._generate_positive_comments(analysis),
                'constructive_suggestions': self._generate_constructive_suggestions(analysis)
            }
            
        except Exception as e:
            logger.error(f"Peer feedback generation failed: {e}")
            return self._fallback_peer_feedback(analysis)
    
    async def _generate_self_reflection_questions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate self-reflection questions for students"""
        try:
            # Use LLM to generate reflection questions
            prompt = self._build_self_reflection_prompt(analysis)
            questions_text = await self.llm._call_llm(prompt, max_tokens=600)
            
            if not questions_text:
                questions_text = self._fallback_self_reflection(analysis)
            
            return {
                'type': 'self_reflection',
                'content': questions_text,
                'questions': self._parse_reflection_questions(questions_text),
                'focus_areas': self._extract_reflection_focus_areas(analysis),
                'goals': self._generate_reflection_goals(analysis),
                'next_steps': self._generate_reflection_next_steps(analysis)
            }
            
        except Exception as e:
            logger.error(f"Self-reflection generation failed: {e}")
            return self._fallback_self_reflection(analysis)
    
    async def _generate_action_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate action plan for improvement"""
        try:
            level = analysis['overall_assessment'].get('assessed_level', 'C')
            improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
            
            action_plan = {
                'immediate_actions': [],
                'short_term_goals': [],
                'long_term_goals': [],
                'timeline': {},
                'resources_needed': [],
                'success_metrics': []
            }
            
            # Immediate actions (1-3 days)
            if 'struktur' in str(improvements).lower():
                action_plan['immediate_actions'].append({
                    'action': 'Granska textens struktur',
                    'description': 'Läs igenom texten och identifiera huvudavsnitt',
                    'time_required': '30 minuter',
                    'priority': 'high'
                })
            
            if 'språk' in str(improvements).lower():
                action_plan['immediate_actions'].append({
                    'action': 'Kontrollera språk och stavning',
                    'description': 'Använd stavningskontroll och läs texten högt',
                    'time_required': '20 minuter',
                    'priority': 'medium'
                })
            
            # Short-term goals (1-2 weeks)
            action_plan['short_term_goals'].append({
                'goal': 'Förbättra argumentation',
                'description': 'Utveckla dina argument med mer detaljer och exempel',
                'target_date': '2 veckor',
                'success_criteria': 'Lägg till minst 3 konkreta exempel'
            })
            
            # Long-term goals (1 month+)
            action_plan['long_term_goals'].append({
                'goal': 'Utveckla kritiskt tänkande',
                'description': 'Öva på att analysera och utvärdera information',
                'target_date': '1 månad',
                'success_criteria': 'Kan identifiera olika perspektiv i texter'
            })
            
            return action_plan
            
        except Exception as e:
            logger.error(f"Action plan generation failed: {e}")
            return self._fallback_action_plan()
    
    async def _generate_progress_tracking(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate progress tracking framework"""
        try:
            current_level = analysis['overall_assessment'].get('assessed_level', 'C')
            strengths = analysis['overall_assessment'].get('strengths', [])
            improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
            
            progress_tracking = {
                'current_status': {
                    'level': current_level,
                    'strengths': strengths,
                    'areas_for_improvement': improvements
                },
                'progress_indicators': [
                    'Textlängd och struktur',
                    'Språklig variation',
                    'Kritiskt tänkande',
                    'Kreativitet och originalitet',
                    'Gy25-efterlevnad'
                ],
                'measurement_methods': [
                    'Självbedömning',
                    'Lärarens observationer',
                    'Peer feedback',
                    'Portfolio-granskning',
                    'Reflektion och diskussion'
                ],
                'milestones': self._generate_milestones(current_level),
                'checkpoints': self._generate_checkpoints()
            }
            
            return progress_tracking
            
        except Exception as e:
            logger.error(f"Progress tracking generation failed: {e}")
            return self._fallback_progress_tracking()
    
    async def _generate_learning_resources(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate learning resources and materials"""
        try:
            subject = analysis.get('subject', 'engelska')
            level = analysis.get('level', '5')
            improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
            
            resources = {
                'reading_materials': self._generate_reading_materials(subject, level),
                'writing_exercises': self._generate_writing_exercises(improvements),
                'online_tools': self._generate_online_tools(subject),
                'reference_materials': self._generate_reference_materials(subject, level),
                'practice_activities': self._generate_practice_activities(improvements),
                'assessment_rubrics': self._generate_assessment_rubrics(subject, level)
            }
            
            return resources
            
        except Exception as e:
            logger.error(f"Learning resources generation failed: {e}")
            return self._fallback_learning_resources()
    
    # Prompt building methods
    def _build_teacher_feedback_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build prompt for teacher feedback"""
        level = analysis['overall_assessment'].get('assessed_level', 'C')
        strengths = analysis['overall_assessment'].get('strengths', [])
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        content_quality = analysis.get('content_quality', {})
        language_skills = analysis.get('language_skills', {})
        critical_thinking = analysis.get('critical_thinking', {})
        creativity = analysis.get('creativity', {})
        gy25_compliance = analysis.get('gy25_compliance', {})
        
        # Detaljerad analys
        coherence_score = content_quality.get('coherence_score', 0)
        language_level = language_skills.get('language_level', 0)
        critical_score = critical_thinking.get('critical_thinking_score', 0)
        creativity_score = creativity.get('creativity_score', 0)
        curriculum_alignment = gy25_compliance.get('curriculum_alignment', 0)
        
        return f"""
Skriv detaljerad och professionell feedback för lärare. Feedbacken måste vara SPECIFIK och KONKRET med pedagogiska insikter.

NUVARANDE NIVÅ: {level}
STYRKOR: {', '.join(strengths[:5]) if strengths else 'Inga specifika styrkor'}
FÖRBÄTTRINGSOMRÅDEN: {', '.join(improvements[:5]) if improvements else 'Inga specifika förbättringsområden'}

DETALJERAD ANALYS:
- Sammanhållning (coherence): {coherence_score:.2f}/1.0
- Språknivå: {language_level:.2f}/1.0
- Kritiskt tänkande: {critical_score:.2f}/1.0
- Kreativitet: {creativity_score:.2f}/1.0
- Läroplanstillstämning: {curriculum_alignment:.2f}/1.0

INSTRUKTIONER FÖR DETALJERAD FEEDBACK:

1. PEDAGOGISKA INSIKTER:
   - Vad visar elevens arbete om deras lärande?
   - Vilka områden behöver särskilt fokus?
   - Vilka styrkor kan byggas vidare på?

2. SPECIFIKA OBSERVATIONER:
   - Citera specifika delar av texten som visar styrkor/svagheter
   - Förklara pedagogiskt varför dessa delar är relevanta
   - Identifiera mönster i elevens arbete

3. UNDERVISNINGSFÖRSLAG:
   - Konkreta förslag för individuell undervisning
   - Material och resurser som kan hjälpa
   - Övningar och aktiviteter för specifika områden

4. KLASSRUMSDISKUSSION:
   - Vilka områden kan diskuteras i klassen?
   - Vilka exempel kan användas (anonymiserat)?
   - Vilka koncept behöver förtydligas?

5. UTVECKLINGSÅTGÄRDER:
   - Konkreta steg för elevens utveckling
   - Tidslinje och mål
   - Hur mäta framsteg

VIKTIGT:
- INTE bara "Bra jobbat" eller "Detta får C"
- INTE generiska kommentarer
- JA: Specifika observationer med exempel
- JA: Pedagogiska insikter och förslag
- JA: Konkreta undervisningsåtgärder
- JA: Detaljerad analys av alla aspekter

Längd: 400-600 ord (mycket detaljerad feedback)
Ton: Professionell, analytisk och stödjande
Struktur: 1) Pedagogiska insikter, 2) Specifika observationer, 3) Undervisningsförslag, 4) Utvecklingsåtgärder
"""
    
    def _build_student_feedback_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build prompt for student feedback"""
        level = analysis['overall_assessment'].get('assessed_level', 'C')
        strengths = analysis['overall_assessment'].get('strengths', [])
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        content_quality = analysis.get('content_quality', {})
        language_skills = analysis.get('language_skills', {})
        critical_thinking = analysis.get('critical_thinking', {})
        recommendations = analysis.get('recommendations', [])
        
        # Extrahera specifika detaljer
        grammar_issues = language_skills.get('grammar_issues', [])
        spelling_issues = language_skills.get('spelling_issues', [])
        vocabulary_score = language_skills.get('vocabulary_richness', 0)
        coherence_score = content_quality.get('coherence_score', 0)
        
        return f"""
Skriv detaljerad och konstruktiv feedback till eleven. Feedbacken måste vara SPECIFIK och KONKRET, INTE generisk.

NUVARANDE NIVÅ: {level}
TEXTENS STYRKOR: {', '.join(strengths[:5]) if strengths else 'Inga specifika styrkor identifierade'}
FÖRBÄTTRINGSOMRÅDEN: {', '.join(improvements[:5]) if improvements else 'Inga specifika förbättringsområden'}

DETALJERAD ANALYS:
- Sammanhållning (coherence): {coherence_score:.2f}/1.0
- Ordförråd: {vocabulary_score:.2f}/1.0
- Grammatikfel: {len(grammar_issues)} st
- Stavfel: {len(spelling_issues)} st

INSTRUKTIONER FÖR DETALJERAD FEEDBACK:

1. STYRKOR (minst 3 specifika exempel):
   - Citera specifika delar av texten som visar styrkor
   - Förklara VARFÖR dessa delar är bra
   - Exempel: "Din användning av [specifik teknik/exempel] visar..."

2. FÖRBÄTTRINGSOMRÅDEN (minst 3 konkreta förslag):
   - För varje förbättringsområde, ge SPECIFIKA exempel från texten
   - Förklara HUR eleven kan förbättra
   - Ge konkreta nästa steg med exempel
   - Exempel: "I meningen [citera specifik mening] kan du förbättra genom att [konkret förslag]"

3. KONKRETA HANDLINGAR:
   - Ge 3-5 specifika, genomförbara steg eleven kan ta
   - Varje steg ska vara konkret och mätbar
   - Exempel: "Öva på att använda övergångsord mellan paragrafen, t.ex. 'därför', 'emellertid', 'dessutom'"

4. NÄSTA STEG:
   - Ge konkret riktning för nästa uppgift
   - Förklara vad eleven ska fokusera på
   - Motivera till fortsatt lärande

VIKTIGT:
- INTE bara "Bra jobbat!" eller "Detta får C"
- INTE generiska kommentarer
- INTE bara betygsnivå
- JA: Specifika exempel från texten
- JA: Konkreta förbättringsförslag
- JA: Handlingsbara steg
- JA: Detaljerad analys av vad som fungerar och vad som kan förbättras

Längd: 300-500 ord (detaljerad feedback)
Ton: Positiv men konstruktiv och specifik
Struktur: 1) Styrkor med exempel, 2) Förbättringsområden med exempel, 3) Konkreta steg, 4) Nästa steg
"""
    
    def _build_parent_feedback_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build prompt for parent feedback"""
        level = analysis['overall_assessment'].get('assessed_level', 'C')
        strengths = analysis['overall_assessment'].get('strengths', [])
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        
        return f"""
Skriv feedback till föräldrar om barnets arbete:

NIVÅ: {level}
STYRKOR: {', '.join(strengths[:3])}
FÖRBÄTTRINGSOMRÅDEN: {', '.join(improvements[:3])}

Feedbacken ska:
- Vara informativ och stödjande
- Fokusera på barnets utveckling
- Ge råd för hemmastöd
- Vara lättförståelig för föräldrar
- Motivera till engagemang

Längd: 150-200 ord
Ton: Informativ och stödjande
"""
    
    def _build_peer_feedback_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build prompt for peer feedback"""
        level = analysis['overall_assessment'].get('assessed_level', 'C')
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        
        return f"""
Skriv riktlinjer för peer feedback:

NIVÅ: {level}
FÖRBÄTTRINGSOMRÅDEN: {', '.join(improvements[:3])}

Riktlinjerna ska:
- Vara lämpliga för elever
- Fokusera på konstruktiv feedback
- Ge konkreta frågor att ställa
- Inkludera positiva kommentarer
- Vara enkla att följa

Längd: 100-150 ord
Ton: Vänlig och konstruktiv
"""
    
    def _build_self_reflection_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build prompt for self-reflection questions"""
        level = analysis['overall_assessment'].get('assessed_level', 'C')
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        
        return f"""
Generera självreflektion frågor för eleven:

NIVÅ: {level}
FÖRBÄTTRINGSOMRÅDEN: {', '.join(improvements[:3])}

Frågorna ska:
- Vara anpassade för elevens nivå
- Fokusera på lärande och utveckling
- Vara öppna och reflekterande
- Hjälpa eleven att förstå sin egen utveckling
- Motivera till fortsatt lärande

Generera 5-7 frågor
"""
    
    # Helper methods for feedback generation
    def _extract_student_strengths(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract strengths for student feedback"""
        strengths = analysis['overall_assessment'].get('strengths', [])
        return strengths[:3]  # Top 3 strengths
    
    def _extract_student_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract improvements for student feedback"""
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        return improvements[:3]  # Top 3 improvements
    
    def _generate_encouragement(self, analysis: Dict[str, Any]) -> str:
        """Generate encouragement message"""
        level = analysis['overall_assessment'].get('assessed_level', 'C')
        
        encouragement_messages = {
            'E': "Du har gjort ett bra försök! Fortsätt att utveckla dina färdigheter.",
            'C': "Bra jobbat! Du visar god förståelse och kan utveckla dig vidare.",
            'A': "Utmärkt arbete! Du visar avancerad förståelse och kreativitet."
        }
        
        return encouragement_messages.get(level, "Bra jobbat! Fortsätt att utveckla dina färdigheter.")
    
    def _extract_specific_actions(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract specific actions for student"""
        recommendations = analysis.get('recommendations', [])
        actions = []
        
        for rec in recommendations[:3]:  # Top 3 recommendations
            if 'specific_actions' in rec:
                actions.extend(rec['specific_actions'][:2])  # Top 2 actions per recommendation
        
        return actions[:5]  # Limit to 5 actions
    
    def _assess_child_progress(self, analysis: Dict[str, Any]) -> str:
        """Assess child's progress for parents"""
        level = analysis['overall_assessment'].get('assessed_level', 'C')
        confidence = analysis['overall_assessment'].get('confidence', 0.5)
        
        if level == 'A' and confidence > 0.7:
            return "Ditt barn visar utmärkt utveckling och når höga nivåer."
        elif level == 'C' and confidence > 0.6:
            return "Ditt barn visar god utveckling och når förväntade nivåer."
        else:
            return "Ditt barn utvecklar sina färdigheter och behöver fortsatt stöd."
    
    def _extract_parent_strengths(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract strengths for parent feedback"""
        strengths = analysis['overall_assessment'].get('strengths', [])
        return strengths[:2]  # Top 2 strengths for parents
    
    def _extract_areas_to_support(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract areas where parents can provide support"""
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        return improvements[:2]  # Top 2 areas for parent support
    
    def _generate_home_support_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate home support suggestions"""
        return [
            "Läs tillsammans och diskutera texter",
            "Uppmuntra till skrivande hemma",
            "Diskutera olika ämnen och perspektiv",
            "Hjälp till att strukturera tankar före skrivande"
        ]
    
    def _generate_communication_guidance(self, analysis: Dict[str, Any]) -> str:
        """Generate communication guidance for parents"""
        return "Diskutera arbetet positivt och fokusera på utveckling snarare än betyg."
    
    def _extract_peer_focus_areas(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract focus areas for peer feedback"""
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        return improvements[:2]  # Top 2 areas for peer focus
    
    def _generate_peer_questions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate questions for peer feedback"""
        return [
            "Vad tycker du är det bästa med texten?",
            "Vilken del skulle du vilja veta mer om?",
            "Hur kunde texten förbättras?",
            "Vilken del var tydligast?"
        ]
    
    def _generate_positive_comments(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate positive comments for peer feedback"""
        strengths = analysis['overall_assessment'].get('strengths', [])
        return strengths[:2]  # Top 2 strengths for positive comments
    
    def _generate_constructive_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate constructive suggestions for peer feedback"""
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        return improvements[:2]  # Top 2 improvements for suggestions
    
    def _parse_reflection_questions(self, questions_text: str) -> List[str]:
        """Parse reflection questions from text"""
        lines = questions_text.split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or 'fråga' in line.lower()):
                # Remove numbering if present
                clean_line = line
                if line[0].isdigit():
                    clean_line = line.split('.', 1)[1].strip() if '.' in line else line
                questions.append(clean_line)
        
        return questions[:7]  # Limit to 7 questions
    
    def _extract_reflection_focus_areas(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract focus areas for self-reflection"""
        improvements = analysis['overall_assessment'].get('areas_for_improvement', [])
        return improvements[:3]  # Top 3 areas for reflection
    
    def _generate_reflection_goals(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate reflection goals"""
        return [
            "Förstå mina styrkor och utvecklingsområden",
            "Planera nästa steg i min utveckling",
            "Reflektera över mina lärandeprocesser"
        ]
    
    def _generate_reflection_next_steps(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps for reflection"""
        return [
            "Granska feedbacken noggrant",
            "Identifiera konkreta förbättringsområden",
            "Sätt mål för nästa uppgift"
        ]
    
    def _generate_milestones(self, current_level: str) -> List[Dict[str, Any]]:
        """Generate milestones based on current level"""
        milestones = {
            'E': [
                {'milestone': 'Förbättra textstruktur', 'target': '2 veckor'},
                {'milestone': 'Utöka ordförråd', 'target': '1 månad'},
                {'milestone': 'Nå C-nivå', 'target': '2 månader'}
            ],
            'C': [
                {'milestone': 'Utveckla kritiskt tänkande', 'target': '3 veckor'},
                {'milestone': 'Förbättra språklig variation', 'target': '1 månad'},
                {'milestone': 'Nå A-nivå', 'target': '2 månader'}
            ],
            'A': [
                {'milestone': 'Behålla A-nivå', 'target': '1 månad'},
                {'milestone': 'Utveckla kreativitet', 'target': '2 månader'},
                {'milestone': 'Bli mentor för andra', 'target': '3 månader'}
            ]
        }
        
        return milestones.get(current_level, milestones['C'])
    
    def _generate_checkpoints(self) -> List[Dict[str, Any]]:
        """Generate checkpoints for progress tracking"""
        return [
            {'checkpoint': 'Vecka 1', 'focus': 'Granska feedback och planera'},
            {'checkpoint': 'Vecka 2', 'focus': 'Börja arbeta med förbättringar'},
            {'checkpoint': 'Vecka 3', 'focus': 'Utvärdera framsteg'},
            {'checkpoint': 'Vecka 4', 'focus': 'Reflektera och planera nästa steg'}
        ]
    
    def _generate_reading_materials(self, subject: str, level: str) -> List[Dict[str, Any]]:
        """Generate reading materials"""
        materials = {
            'engelska': [
                {'title': 'British Literature Overview', 'level': level, 'type': 'textbook'},
                {'title': 'Writing Skills Guide', 'level': level, 'type': 'guide'},
                {'title': 'Critical Thinking Exercises', 'level': level, 'type': 'workbook'}
            ],
            'svenska': [
                {'title': 'Svensk Litteratur', 'level': level, 'type': 'textbook'},
                {'title': 'Skrivteknik', 'level': level, 'type': 'guide'},
                {'title': 'Textanalys', 'level': level, 'type': 'workbook'}
            ]
        }
        
        return materials.get(subject, materials['engelska'])
    
    def _generate_writing_exercises(self, improvements: List[str]) -> List[Dict[str, Any]]:
        """Generate writing exercises based on improvements"""
        exercises = []
        
        if any('struktur' in imp.lower() for imp in improvements):
            exercises.append({
                'title': 'Textstruktur-övningar',
                'description': 'Öva på att organisera texter logiskt',
                'duration': '30 minuter',
                'difficulty': 'medium'
            })
        
        if any('språk' in imp.lower() for imp in improvements):
            exercises.append({
                'title': 'Språkutveckling',
                'description': 'Utöka ordförråd och förbättra språkbruk',
                'duration': '20 minuter',
                'difficulty': 'easy'
            })
        
        return exercises
    
    def _generate_online_tools(self, subject: str) -> List[Dict[str, Any]]:
        """Generate online tools"""
        tools = {
            'engelska': [
                {'name': 'Grammarly', 'type': 'writing_assistant', 'url': 'grammarly.com'},
                {'name': 'Merriam-Webster', 'type': 'dictionary', 'url': 'merriam-webster.com'},
                {'name': 'BBC Learning English', 'type': 'learning_platform', 'url': 'bbc.co.uk/learningenglish'}
            ],
            'svenska': [
                {'name': 'Svenska Akademiens Ordbok', 'type': 'dictionary', 'url': 'svenska.se'},
                {'name': 'Språkrådet', 'type': 'language_authority', 'url': 'sprakradet.se'},
                {'name': 'Litteraturbanken', 'type': 'literature', 'url': 'litteraturbanken.se'}
            ]
        }
        
        return tools.get(subject, tools['engelska'])
    
    def _generate_reference_materials(self, subject: str, level: str) -> List[Dict[str, Any]]:
        """Generate reference materials"""
        materials = {
            'engelska': [
                {'title': 'English Grammar Guide', 'level': level, 'type': 'reference'},
                {'title': 'Writing Style Manual', 'level': level, 'type': 'reference'},
                {'title': 'Literature Analysis Guide', 'level': level, 'type': 'reference'}
            ],
            'svenska': [
                {'title': 'Svensk Grammatik', 'level': level, 'type': 'reference'},
                {'title': 'Skrivhandbok', 'level': level, 'type': 'reference'},
                {'title': 'Litteraturanalys', 'level': level, 'type': 'reference'}
            ]
        }
        
        return materials.get(subject, materials['engelska'])
    
    def _generate_practice_activities(self, improvements: List[str]) -> List[Dict[str, Any]]:
        """Generate practice activities"""
        activities = []
        
        for improvement in improvements[:3]:  # Top 3 improvements
            if 'struktur' in improvement.lower():
                activities.append({
                    'title': 'Strukturera dina tankar',
                    'description': 'Skapa en plan innan du skriver',
                    'time_required': '15 minuter',
                    'frequency': 'dagligen'
                })
            elif 'språk' in improvement.lower():
                activities.append({
                    'title': 'Språkliga variationer',
                    'description': 'Använd olika ord och meningar',
                    'time_required': '10 minuter',
                    'frequency': 'dagligen'
                })
        
        return activities
    
    def _generate_assessment_rubrics(self, subject: str, level: str) -> List[Dict[str, Any]]:
        """Generate assessment rubrics"""
        return [
            {
                'title': f'Bedömningsmatris {subject} nivå {level}',
                'criteria': ['Innehåll', 'Struktur', 'Språk', 'Kreativitet'],
                'levels': ['E', 'C', 'A'],
                'description': 'Använd för självbedömning och peer feedback'
            }
        ]
    
    # Fallback methods
    def _fallback_feedback(self, content: str, student_id: str, assignment_id: str) -> Dict[str, Any]:
        """Fallback feedback when generation fails"""
        return {
            'feedback_id': f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'student_id': student_id,
            'assignment_id': assignment_id,
            'generated_at': datetime.now().isoformat(),
            'teacher_feedback': self._fallback_teacher_feedback({}),
            'student_feedback': self._fallback_student_feedback({}),
            'parent_feedback': self._fallback_parent_feedback({}),
            'peer_feedback': self._fallback_peer_feedback({}),
            'self_reflection': self._fallback_self_reflection({}),
            'action_plan': self._fallback_action_plan(),
            'progress_tracking': self._fallback_progress_tracking(),
            'resources': self._fallback_learning_resources()
        }
    
    def _fallback_teacher_feedback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback teacher feedback"""
        return {
            'type': 'teacher',
            'content': 'Grundläggande feedback genererad. Granska arbetet noggrant och ge specifik återkoppling.',
            'assessment_level': 'C',
            'key_strengths': ['Grundläggande förståelse'],
            'improvement_areas': ['Utveckla argumentation'],
            'recommendations': [],
            'next_steps': [],
            'confidence': 0.5
        }
    
    def _fallback_student_feedback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback student feedback"""
        return {
            'type': 'student',
            'content': 'Bra jobbat! Fortsätt att utveckla dina färdigheter.',
            'level': 'C',
            'strengths': ['Grundläggande förståelse'],
            'improvements': ['Utveckla argumentation'],
            'encouragement': 'Fortsätt att arbeta hårt!',
            'specific_actions': ['Läs mer', 'Öva på att skriva']
        }
    
    def _fallback_parent_feedback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback parent feedback"""
        return {
            'type': 'parent',
            'content': 'Ditt barn utvecklar sina färdigheter. Fortsätt att stödja lärandet hemma.',
            'child_progress': 'Utvecklar sina färdigheter',
            'strengths': ['Grundläggande förståelse'],
            'areas_to_support': ['Läsning och skrivande'],
            'home_support': ['Läs tillsammans', 'Diskutera texter'],
            'communication': 'Uppmuntra och stöd'
        }
    
    def _fallback_peer_feedback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback peer feedback"""
        return {
            'type': 'peer',
            'content': 'Ge konstruktiv feedback och fokusera på utveckling.',
            'focus_areas': ['Innehåll', 'Struktur'],
            'questions_to_ask': ['Vad tycker du?', 'Hur kunde det förbättras?'],
            'positive_comments': ['Bra jobbat!'],
            'constructive_suggestions': ['Utveckla mer']
        }
    
    def _fallback_self_reflection(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback self-reflection"""
        return {
            'type': 'self_reflection',
            'content': 'Reflektera över ditt arbete och planera nästa steg.',
            'questions': [
                'Vad gick bra?',
                'Vad kan förbättras?',
                'Vad ska jag fokusera på nästa gång?'
            ],
            'focus_areas': ['Innehåll', 'Struktur'],
            'goals': ['Förbättra skrivfärdigheter'],
            'next_steps': ['Granska feedback', 'Planera nästa steg']
        }
    
    def _fallback_action_plan(self) -> Dict[str, Any]:
        """Fallback action plan"""
        return {
            'immediate_actions': [
                {'action': 'Granska feedback', 'description': 'Läs igenom kommentarerna', 'time_required': '15 minuter', 'priority': 'high'}
            ],
            'short_term_goals': [
                {'goal': 'Förbättra skrivfärdigheter', 'description': 'Öva på att skriva', 'target_date': '2 veckor', 'success_criteria': 'Skriv regelbundet'}
            ],
            'long_term_goals': [
                {'goal': 'Utveckla kritiskt tänkande', 'description': 'Analysera och utvärdera', 'target_date': '1 månad', 'success_criteria': 'Kan analysera texter'}
            ],
            'timeline': {},
            'resources_needed': ['Skrivmaterial', 'Läsmaterial'],
            'success_metrics': ['Textkvalitet', 'Självförtroende']
        }
    
    def _fallback_progress_tracking(self) -> Dict[str, Any]:
        """Fallback progress tracking"""
        return {
            'current_status': {
                'level': 'C',
                'strengths': ['Grundläggande förståelse'],
                'areas_for_improvement': ['Utveckla argumentation']
            },
            'progress_indicators': ['Textkvalitet', 'Språkutveckling'],
            'measurement_methods': ['Självbedömning', 'Lärarens observationer'],
            'milestones': [
                {'milestone': 'Förbättra struktur', 'target': '2 veckor'},
                {'milestone': 'Utveckla språk', 'target': '1 månad'}
            ],
            'checkpoints': [
                {'checkpoint': 'Vecka 1', 'focus': 'Granska feedback'},
                {'checkpoint': 'Vecka 2', 'focus': 'Börja förbättra'}
            ]
        }
    
    def _fallback_learning_resources(self) -> Dict[str, Any]:
        """Fallback learning resources"""
        return {
            'reading_materials': [
                {'title': 'Grundläggande skrivguide', 'level': '5', 'type': 'guide'}
            ],
            'writing_exercises': [
                {'title': 'Skrivövningar', 'description': 'Öva på att skriva', 'duration': '30 minuter', 'difficulty': 'medium'}
            ],
            'online_tools': [
                {'name': 'Stavningskontroll', 'type': 'tool', 'url': 'example.com'}
            ],
            'reference_materials': [
                {'title': 'Grammatikguide', 'level': '5', 'type': 'reference'}
            ],
            'practice_activities': [
                {'title': 'Daglig skrivning', 'description': 'Skriv varje dag', 'time_required': '15 minuter', 'frequency': 'dagligen'}
            ],
            'assessment_rubrics': [
                {'title': 'Bedömningsmatris', 'criteria': ['Innehåll', 'Språk'], 'levels': ['E', 'C', 'A'], 'description': 'Använd för bedömning'}
            ]
        }

# Global instance
feedback_service = FeedbackService()
