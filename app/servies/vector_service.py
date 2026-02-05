"""
Vector Database Service for RAG System
Handles document embeddings and similarity search using ChromaDB
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import uuid
from datetime import datetime

import chromadb
from chromadb.config import Settings
import numpy as np

logger = logging.getLogger("Genassista-EDU-pythonAPI.vector")

class VectorDatabase:
    """Manages document embeddings and similarity search"""
    
    def __init__(self, persist_directory: str = "data/vector_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Collection names
        self.documents_collection = "documents"
        self.knowledge_collection = "skolverket_knowledge"
        
        # Initialize collections
        self._init_collections()
    
    def _init_collections(self):
        """Initialize ChromaDB collections"""
        try:
            # Documents collection
            self.doc_collection = self.client.get_or_create_collection(
                name=self.documents_collection,
                metadata={"description": "Uploaded documents and student submissions"}
            )
            
            # Knowledge base collection
            self.knowledge_collection = self.client.get_or_create_collection(
                name=self.knowledge_collection,
                metadata={"description": "Skolverket curriculum and assessment criteria"}
            )
            
            logger.info("Vector database collections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
            raise
    
    def add_document(self, document_id: str, content: str, 
                    metadata: Dict[str, Any], chunks: List[Dict[str, Any]]) -> bool:
        """
        Add a document to the vector database
        
        Args:
            document_id: Unique identifier for the document
            content: Full document content
            metadata: Document metadata
            chunks: List of content chunks
        
        Returns:
            Success status
        """
        try:
            # Prepare data for ChromaDB
            chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            chunk_contents = [chunk['content'] for chunk in chunks]
            chunk_metadata = []
            
            for i, chunk in enumerate(chunks):
                chunk_meta = {
                    'document_id': document_id,
                    'chunk_index': chunk['chunk_index'],
                    'start_char': chunk['start_char'],
                    'end_char': chunk['end_char'],
                    'word_count': chunk['word_count'],
                    **metadata
                }
                chunk_metadata.append(chunk_meta)
            
            # Add to collection
            self.doc_collection.add(
                ids=chunk_ids,
                documents=chunk_contents,
                metadatas=chunk_metadata
            )
            
            logger.info(f"Added document {document_id} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document {document_id}: {e}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5, 
                        filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of similar documents with scores
        """
        try:
            # Perform similarity search
            results = self.doc_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity_score': 1 - distance,  # Convert distance to similarity
                        'rank': i + 1
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def add_knowledge_base(self, knowledge_items: List[Dict[str, Any]]) -> bool:
        """
        Add Skolverket knowledge base items
        
        Args:
            knowledge_items: List of knowledge items with content and metadata
        
        Returns:
            Success status
        """
        try:
            # Prepare data
            item_ids = [f"kb_{uuid.uuid4().hex[:8]}" for _ in knowledge_items]
            contents = [item['content'] for item in knowledge_items]
            metadatas = []
            
            for item in knowledge_items:
                metadata = {
                    'type': item.get('type', 'general'),
                    'subject': item.get('subject', 'engelska'),
                    'level': item.get('level', '5'),
                    'criteria': item.get('criteria', ''),
                    'created_at': datetime.now().isoformat()
                }
                metadatas.append(metadata)
            
            # Add to knowledge collection
            self.knowledge_collection.add(
                ids=item_ids,
                documents=contents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(knowledge_items)} knowledge base items")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add knowledge base: {e}")
            return False
    
    def search_knowledge(self, query: str, subject: str = "engelska", 
                        level: str = "5", n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search Skolverket knowledge base
        
        Args:
            query: Search query
            subject: Subject filter (e.g., "engelska")
            level: Level filter (e.g., "5")
            n_results: Number of results to return
        
        Returns:
            List of relevant knowledge items
        """
        try:
            # Search with filters
            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=n_results,
                where={
                    "subject": subject,
                    "level": level
                }
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (content, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'content': content,
                        'metadata': metadata,
                        'relevance_score': 1 - distance,
                        'rank': i + 1
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            results = self.doc_collection.get(
                where={"document_id": document_id}
            )
            
            chunks = []
            if results['documents']:
                for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                    chunks.append({
                        'content': doc,
                        'metadata': metadata,
                        'chunk_index': metadata.get('chunk_index', i)
                    })
            
            return sorted(chunks, key=lambda x: x['chunk_index'])
            
        except Exception as e:
            logger.error(f"Failed to get document chunks: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks"""
        try:
            # Get all chunk IDs for this document
            results = self.doc_collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.doc_collection.delete(ids=results['ids'])
                logger.info(f"Deleted document {document_id} with {len(results['ids'])} chunks")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        try:
            doc_count = self.doc_collection.count()
            knowledge_count = self.knowledge_collection.count()
            
            return {
                'documents_count': doc_count,
                'knowledge_items_count': knowledge_count,
                'total_chunks': doc_count,  # Assuming 1 chunk per document for simplicity
                'collections': {
                    'documents': self.documents_collection,
                    'knowledge': self.knowledge_collection
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

# Global instance
vector_db = VectorDatabase()
