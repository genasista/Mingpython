#!/usr/bin/env python3
"""
Test RAG System
Tests document processing, vector storage, and AI analysis
"""

import asyncio
import json
import logging
from pathlib import Path
import tempfile
import os

# Add the app directory to Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.servies.rag_service import rag_service
from app.servies.document_service import document_processor
from app.servies.vector_service import vector_db

logger = logging.getLogger("rag_test")

async def test_document_processing():
    """Test document processing functionality"""
    print("🔍 Testing Document Processing...")
    
    # Create a test text file
    test_content = """
    This is a test essay about British literature. 
    The student discusses various authors and their contributions to English literature.
    The essay shows good understanding of the topic but could be more detailed.
    The writing style is clear but lacks some sophistication.
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Test document processing
        result = document_processor.process_document(temp_file)
        
        print(f"✅ Document processing: {result.get('processing_success', False)}")
        print(f"   Content length: {len(result.get('content', ''))}")
        print(f"   Word count: {len(result.get('content', '').split())}")
        
        # Test chunking
        chunks = document_processor.chunk_content(result.get('content', ''))
        print(f"   Chunks created: {len(chunks)}")
        
        return result.get('content', '')
        
    finally:
        os.unlink(temp_file)

async def test_vector_database():
    """Test vector database functionality"""
    print("\n🗄️ Testing Vector Database...")
    
    try:
        # Test knowledge base search
        results = vector_db.search_knowledge(
            query="What are the requirements for grade A in English?",
            subject="engelska",
            level="5",
            n_results=3
        )
        
        print(f"✅ Knowledge search: {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['content'][:100]}... (Score: {result['relevance_score']:.3f})")
        
        # Test document search
        doc_results = vector_db.search_documents(
            query="British literature essay",
            n_results=3
        )
        
        print(f"✅ Document search: {len(doc_results)} results")
        
        # Get stats
        stats = vector_db.get_collection_stats()
        print(f"✅ Database stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector database test failed: {e}")
        return False

async def test_rag_analysis():
    """Test RAG analysis functionality"""
    print("\n🤖 Testing RAG Analysis...")
    
    try:
        # Test text analysis
        test_text = """
        This essay discusses the theme of love in Shakespeare's sonnets. 
        The student shows good understanding of the basic concepts but could develop 
        their analysis more deeply. The writing is clear but lacks some sophistication.
        The essay demonstrates knowledge of the subject matter but could benefit from 
        more detailed examples and deeper critical thinking.
        """
        
        analysis = await rag_service.analyze_student_submission(
            submission_content=test_text,
            assignment_id="test_assignment_1",
            student_id="test_student_1"
        )
        
        if analysis["success"]:
            print("✅ RAG analysis successful")
            print(f"   Predicted level: {analysis['analysis'].get('level', 'Unknown')}")
            print(f"   Strengths: {len(analysis['analysis'].get('strengths', []))}")
            print(f"   Improvements: {len(analysis['analysis'].get('improvements', []))}")
            print(f"   Knowledge used: {len(analysis['knowledge_used'])}")
            
            # Print feedback
            feedback = analysis['feedback']
            print(f"\n📝 Generated Feedback:")
            print(f"   {feedback[:200]}...")
            
        else:
            print(f"❌ RAG analysis failed: {analysis.get('error', 'Unknown error')}")
        
        return analysis["success"]
        
    except Exception as e:
        print(f"❌ RAG analysis test failed: {e}")
        return False

async def test_document_upload_and_analysis():
    """Test complete document upload and analysis workflow"""
    print("\n📄 Testing Document Upload and Analysis...")
    
    try:
        # Create a test document
        test_content = """
        Essay: The Impact of Technology on Education
        
        Technology has revolutionized the way we learn and teach. In this essay, 
        I will discuss the positive and negative effects of technology on education.
        
        Positive effects include increased access to information, personalized learning, 
        and improved engagement. Students can now access vast amounts of information 
        online and learn at their own pace.
        
        However, there are also negative effects such as decreased face-to-face interaction, 
        potential for distraction, and the digital divide between students with and without 
        access to technology.
        
        In conclusion, technology has both benefits and drawbacks in education. 
        It is important to use technology wisely and ensure that all students have 
        equal access to educational resources.
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Process and store document
            result = await rag_service.process_and_store_document(
                file_path=temp_file,
                metadata={
                    "student_id": "test_student_2",
                    "assignment_id": "test_assignment_2",
                    "document_type": "student_submission",
                    "original_filename": "technology_essay.txt"
                }
            )
            
            if result["success"]:
                print(f"✅ Document uploaded: {result['document_id']}")
                print(f"   Content length: {result['content_length']}")
                print(f"   Chunks: {result['chunks_count']}")
                
                # Analyze the document
                analysis = await rag_service.analyze_student_submission(
                    submission_content=test_content,
                    assignment_id="test_assignment_2",
                    student_id="test_student_2"
                )
                
                if analysis["success"]:
                    print("✅ Document analysis successful")
                    print(f"   Level: {analysis['analysis'].get('level', 'Unknown')}")
                    print(f"   Feedback length: {len(analysis['feedback'])}")
                else:
                    print(f"❌ Document analysis failed: {analysis.get('error')}")
                
            else:
                print(f"❌ Document upload failed: {result.get('error')}")
        
        finally:
            os.unlink(temp_file)
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Document upload test failed: {e}")
        return False

async def test_knowledge_base_search():
    """Test knowledge base search functionality"""
    print("\n📚 Testing Knowledge Base Search...")
    
    try:
        # Test various queries
        test_queries = [
            "What are the requirements for grade A in English 5?",
            "How should I give feedback to students at E level?",
            "What are the criteria for written communication?",
            "How can students improve from C to A level?",
            "What is the central content for English 5?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            results = vector_db.search_knowledge(
                query=query,
                subject="engelska",
                level="5",
                n_results=2
            )
            
            print(f"   Results: {len(results)}")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['content'][:100]}... (Score: {result['relevance_score']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Knowledge base search test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Testing RAG System")
    print("=" * 50)
    
    # Test results
    results = {}
    
    # Test document processing
    content = await test_document_processing()
    results["document_processing"] = bool(content)
    
    # Test vector database
    results["vector_database"] = await test_vector_database()
    
    # Test RAG analysis
    results["rag_analysis"] = await test_rag_analysis()
    
    # Test document upload and analysis
    results["document_upload"] = await test_document_upload_and_analysis()
    
    # Test knowledge base search
    results["knowledge_search"] = await test_knowledge_base_search()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RAG system is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
