#!/usr/bin/env python3
"""
Complete System Test for Genassista EDU Python API
Tests all functionality including AI analysis, feedback, and RAG system
"""

import asyncio
import json
import logging
import tempfile
import os
from pathlib import Path
import requests
import time

# Add the app directory to Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.servies.ai_analysis_service import ai_analysis_service
from app.servies.feedback_service import feedback_service
from app.servies.llm_service import llm_service
from app.servies.rag_service import rag_service
from app.servies.document_service import document_processor

logger = logging.getLogger("complete_system_test")

class SystemTester:
    """Comprehensive system tester for Genassista EDU"""
    
    def __init__(self, base_url: str = None):
        # Använd PORT miljövariabel om ingen base_url anges
        if base_url is None:
            port = os.getenv("PORT", "8001")
            base_url = f"http://localhost:{port}"
        self.base_url = base_url
        self.test_results = {}
    
    async def test_all_services(self) -> Dict[str, Any]:
        """Test all services comprehensively"""
        print("🚀 Starting Complete System Test for Genassista EDU")
        print("=" * 60)
        
        # Test results
        results = {
            'ai_analysis': await self.test_ai_analysis(),
            'feedback_generation': await self.test_feedback_generation(),
            'llm_services': await self.test_llm_services(),
            'rag_system': await self.test_rag_system(),
            'document_processing': await self.test_document_processing(),
            'api_endpoints': await self.test_api_endpoints(),
            'integration': await self.test_integration()
        }
        
        # Calculate overall success
        total_tests = sum(len(category) for category in results.values() if isinstance(category, dict))
        passed_tests = sum(
            len([test for test in category.values() if test.get('success', False)])
            for category in results.values() if isinstance(category, dict)
        )
        
        results['overall'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'overall_success': passed_tests == total_tests
        }
        
        return results
    
    async def test_ai_analysis(self) -> Dict[str, Any]:
        """Test AI analysis service"""
        print("\n🤖 Testing AI Analysis Service...")
        
        results = {}
        
        # Test 1: Basic analysis
        try:
            test_content = """
            This essay discusses the importance of education in modern society. 
            Education is crucial for personal development and social progress. 
            Students need access to quality education to succeed in life.
            """
            
            analysis = await ai_analysis_service.analyze_student_submission(
                content=test_content,
                submission_type="essay",
                student_id="test_student_1",
                assignment_id="test_assignment_1",
                subject="engelska",
                level="5"
            )
            
            results['basic_analysis'] = {
                'success': True,
                'level': analysis['overall_assessment'].get('assessed_level', 'Unknown'),
                'confidence': analysis['overall_assessment'].get('confidence', 0),
                'message': 'Basic analysis completed successfully'
            }
            
        except Exception as e:
            results['basic_analysis'] = {
                'success': False,
                'error': str(e),
                'message': 'Basic analysis failed'
            }
        
        # Test 2: Content quality analysis
        try:
            content_analysis = analysis.get('content_quality', {})
            results['content_quality'] = {
                'success': True,
                'word_count': content_analysis.get('word_count', 0),
                'coherence_score': content_analysis.get('coherence_score', 0),
                'message': 'Content quality analysis completed'
            }
            
        except Exception as e:
            results['content_quality'] = {
                'success': False,
                'error': str(e),
                'message': 'Content quality analysis failed'
            }
        
        # Test 3: Language skills analysis
        try:
            language_analysis = analysis.get('language_skills', {})
            results['language_skills'] = {
                'success': True,
                'vocabulary_richness': language_analysis.get('vocabulary_richness', 0),
                'language_level': language_analysis.get('language_level', 0),
                'message': 'Language skills analysis completed'
            }
            
        except Exception as e:
            results['language_skills'] = {
                'success': False,
                'error': str(e),
                'message': 'Language skills analysis failed'
            }
        
        return results
    
    async def test_feedback_generation(self) -> Dict[str, Any]:
        """Test feedback generation service"""
        print("\n📝 Testing Feedback Generation Service...")
        
        results = {}
        
        # Test 1: Teacher feedback
        try:
            test_analysis = {
                'overall_assessment': {
                    'assessed_level': 'C',
                    'strengths': ['Good structure', 'Clear arguments'],
                    'areas_for_improvement': ['More examples needed', 'Develop vocabulary']
                }
            }
            
            teacher_feedback = await feedback_service._generate_teacher_feedback(test_analysis)
            
            results['teacher_feedback'] = {
                'success': True,
                'feedback_length': len(teacher_feedback.get('content', '')),
                'level': teacher_feedback.get('assessment_level', 'Unknown'),
                'message': 'Teacher feedback generated successfully'
            }
            
        except Exception as e:
            results['teacher_feedback'] = {
                'success': False,
                'error': str(e),
                'message': 'Teacher feedback generation failed'
            }
        
        # Test 2: Student feedback
        try:
            student_feedback = await feedback_service._generate_student_feedback(test_analysis)
            
            results['student_feedback'] = {
                'success': True,
                'feedback_length': len(student_feedback.get('content', '')),
                'encouragement': bool(student_feedback.get('encouragement', '')),
                'message': 'Student feedback generated successfully'
            }
            
        except Exception as e:
            results['student_feedback'] = {
                'success': False,
                'error': str(e),
                'message': 'Student feedback generation failed'
            }
        
        # Test 3: Comprehensive feedback
        try:
            comprehensive_feedback = await feedback_service.generate_comprehensive_feedback(
                content="Test essay content",
                student_id="test_student_2",
                assignment_id="test_assignment_2"
            )
            
            results['comprehensive_feedback'] = {
                'success': True,
                'feedback_types': len([k for k in comprehensive_feedback.keys() if 'feedback' in k]),
                'has_action_plan': 'action_plan' in comprehensive_feedback,
                'message': 'Comprehensive feedback generated successfully'
            }
            
        except Exception as e:
            results['comprehensive_feedback'] = {
                'success': False,
                'error': str(e),
                'message': 'Comprehensive feedback generation failed'
            }
        
        return results
    
    async def test_llm_services(self) -> Dict[str, Any]:
        """Test LLM services"""
        print("\n🧠 Testing LLM Services...")
        
        results = {}
        
        # Test 1: Basic LLM call
        try:
            response = await llm_service._call_llm("Hej, kan du svara på svenska?", max_tokens=50)
            
            results['basic_llm_call'] = {
                'success': response is not None,
                'response_length': len(response) if response else 0,
                'message': 'Basic LLM call completed' if response else 'Basic LLM call failed'
            }
            
        except Exception as e:
            results['basic_llm_call'] = {
                'success': False,
                'error': str(e),
                'message': 'Basic LLM call failed'
            }
        
        # Test 2: Student work analysis
        try:
            analysis = await llm_service.analyze_student_work(
                content="This is a test essay about education.",
                assignment_type="essay",
                student_level="5",
                subject="engelska"
            )
            
            results['student_work_analysis'] = {
                'success': True,
                'level': analysis.get('level', 'Unknown'),
                'has_strengths': bool(analysis.get('strengths', [])),
                'message': 'Student work analysis completed'
            }
            
        except Exception as e:
            results['student_work_analysis'] = {
                'success': False,
                'error': str(e),
                'message': 'Student work analysis failed'
            }
        
        # Test 3: Question generation
        try:
            questions = await llm_service.generate_questions(
                content="Education is important for society.",
                question_type="comprehension",
                difficulty="medium"
            )
            
            results['question_generation'] = {
                'success': True,
                'num_questions': len(questions),
                'message': 'Question generation completed'
            }
            
        except Exception as e:
            results['question_generation'] = {
                'success': False,
                'error': str(e),
                'message': 'Question generation failed'
            }
        
        return results
    
    async def test_rag_system(self) -> Dict[str, Any]:
        """Test RAG system"""
        print("\n🔍 Testing RAG System...")
        
        results = {}
        
        # Test 1: Document processing
        try:
            test_content = "This is a test document for RAG processing."
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_content)
                temp_file = f.name
            
            try:
                doc_result = document_processor.process_document(temp_file)
                
                results['document_processing'] = {
                    'success': doc_result.get('processing_success', False),
                    'content_extracted': bool(doc_result.get('content', '')),
                    'message': 'Document processing completed' if doc_result.get('processing_success') else 'Document processing failed'
                }
                
            finally:
                os.unlink(temp_file)
            
        except Exception as e:
            results['document_processing'] = {
                'success': False,
                'error': str(e),
                'message': 'Document processing failed'
            }
        
        # Test 2: Vector database
        try:
            stats = rag_service.get_database_stats()
            
            results['vector_database'] = {
                'success': bool(stats),
                'documents_count': stats.get('documents_count', 0),
                'knowledge_items_count': stats.get('knowledge_items_count', 0),
                'message': 'Vector database accessible'
            }
            
        except Exception as e:
            results['vector_database'] = {
                'success': False,
                'error': str(e),
                'message': 'Vector database test failed'
            }
        
        # Test 3: Knowledge search
        try:
            knowledge_results = await rag_service.search_knowledge(
                query="What are the requirements for grade A?",
                subject="engelska",
                level="5"
            )
            
            results['knowledge_search'] = {
                'success': True,
                'results_count': len(knowledge_results),
                'message': 'Knowledge search completed'
            }
            
        except Exception as e:
            results['knowledge_search'] = {
                'success': False,
                'error': str(e),
                'message': 'Knowledge search failed'
            }
        
        return results
    
    async def test_document_processing(self) -> Dict[str, Any]:
        """Test document processing"""
        print("\n📄 Testing Document Processing...")
        
        results = {}
        
        # Test 1: Text processing
        try:
            test_content = "This is a test text for document processing."
            chunks = document_processor.chunk_content(test_content)
            
            results['text_processing'] = {
                'success': True,
                'chunks_created': len(chunks),
                'message': 'Text processing completed'
            }
            
        except Exception as e:
            results['text_processing'] = {
                'success': False,
                'error': str(e),
                'message': 'Text processing failed'
            }
        
        # Test 2: Metadata extraction
        try:
            metadata = document_processor.extract_metadata(test_content)
            
            results['metadata_extraction'] = {
                'success': True,
                'word_count': metadata.get('word_count', 0),
                'sentence_count': metadata.get('sentence_count', 0),
                'message': 'Metadata extraction completed'
            }
            
        except Exception as e:
            results['metadata_extraction'] = {
                'success': False,
                'error': str(e),
                'message': 'Metadata extraction failed'
            }
        
        return results
    
    async def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        results = {}
        
        # Test 1: Health check
        try:
            response = requests.get(f"{self.base_url}/api/version1/health", timeout=10)
            
            results['health_check'] = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'message': 'Health check completed'
            }
            
        except Exception as e:
            results['health_check'] = {
                'success': False,
                'error': str(e),
                'message': 'Health check failed'
            }
        
        # Test 2: AI analysis endpoint
        try:
            test_data = {
                'content': 'This is a test essay for API testing.',
                'student_id': 'test_student_api',
                'assignment_id': 'test_assignment_api',
                'submission_type': 'essay',
                'subject': 'engelska',
                'level': '5'
            }
            
            response = requests.post(
                f"{self.base_url}/api/version1/ai/analyze/submission",
                data=test_data,
                timeout=30
            )
            
            results['ai_analysis_endpoint'] = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'message': 'AI analysis endpoint test completed'
            }
            
        except Exception as e:
            results['ai_analysis_endpoint'] = {
                'success': False,
                'error': str(e),
                'message': 'AI analysis endpoint test failed'
            }
        
        # Test 3: Quick feedback endpoint
        try:
            test_data = {
                'content': 'This is a test essay for quick feedback.',
                'student_id': 'test_student_quick',
                'assignment_id': 'test_assignment_quick'
            }
            
            response = requests.post(
                f"{self.base_url}/api/version1/ai/feedback/quick",
                data=test_data,
                timeout=30
            )
            
            results['quick_feedback_endpoint'] = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'message': 'Quick feedback endpoint test completed'
            }
            
        except Exception as e:
            results['quick_feedback_endpoint'] = {
                'success': False,
                'error': str(e),
                'message': 'Quick feedback endpoint test failed'
            }
        
        return results
    
    async def test_integration(self) -> Dict[str, Any]:
        """Test system integration"""
        print("\n🔗 Testing System Integration...")
        
        results = {}
        
        # Test 1: End-to-end workflow
        try:
            # Step 1: Analyze student work
            analysis = await ai_analysis_service.analyze_student_submission(
                content="This is an integrated test essay about the importance of education in society.",
                submission_type="essay",
                student_id="integration_test_student",
                assignment_id="integration_test_assignment",
                subject="engelska",
                level="5"
            )
            
            # Step 2: Generate feedback
            feedback = await feedback_service.generate_comprehensive_feedback(
                content="This is an integrated test essay about the importance of education in society.",
                student_id="integration_test_student",
                assignment_id="integration_test_assignment"
            )
            
            # Step 3: Generate questions
            questions = await llm_service.generate_questions(
                content="This is an integrated test essay about the importance of education in society.",
                question_type="comprehension",
                difficulty="medium"
            )
            
            results['end_to_end_workflow'] = {
                'success': True,
                'analysis_completed': bool(analysis),
                'feedback_generated': bool(feedback),
                'questions_generated': len(questions) > 0,
                'message': 'End-to-end workflow completed successfully'
            }
            
        except Exception as e:
            results['end_to_end_workflow'] = {
                'success': False,
                'error': str(e),
                'message': 'End-to-end workflow failed'
            }
        
        # Test 2: Performance test
        try:
            start_time = time.time()
            
            # Run multiple analyses in parallel
            tasks = []
            for i in range(3):
                task = ai_analysis_service.analyze_student_submission(
                    content=f"Test essay {i} about education and society.",
                    submission_type="essay",
                    student_id=f"perf_test_student_{i}",
                    assignment_id=f"perf_test_assignment_{i}",
                    subject="engelska",
                    level="5"
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            results['performance_test'] = {
                'success': True,
                'duration_seconds': duration,
                'analyses_per_second': 3 / duration,
                'message': 'Performance test completed'
            }
            
        except Exception as e:
            results['performance_test'] = {
                'success': False,
                'error': str(e),
                'message': 'Performance test failed'
            }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print test results in a formatted way"""
        print("\n📊 Test Results Summary")
        print("=" * 40)
        
        for category, tests in results.items():
            if category == 'overall':
                continue
                
            print(f"\n{category.upper().replace('_', ' ')}:")
            
            if isinstance(tests, dict):
                for test_name, test_result in tests.items():
                    status = "✅ PASS" if test_result.get('success', False) else "❌ FAIL"
                    message = test_result.get('message', 'No message')
                    print(f"  {test_name}: {status} - {message}")
            else:
                print(f"  {tests}")
        
        # Overall summary
        overall = results.get('overall', {})
        print(f"\n🎯 OVERALL SUMMARY:")
        print(f"  Total Tests: {overall.get('total_tests', 0)}")
        print(f"  Passed: {overall.get('passed_tests', 0)}")
        print(f"  Success Rate: {overall.get('success_rate', 0):.1%}")
        print(f"  Overall Status: {'✅ ALL TESTS PASSED' if overall.get('overall_success', False) else '❌ SOME TESTS FAILED'}")

async def main():
    """Main test function"""
    tester = SystemTester()
    
    try:
        results = await tester.test_all_services()
        tester.print_results(results)
        
        # Save results to file
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Test results saved to test_results.json")
        
        # Return success status
        overall_success = results.get('overall', {}).get('overall_success', False)
        return overall_success
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
