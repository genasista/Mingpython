"""
Embedding Service for RAG System
Handles text embeddings using OpenAI's text-embedding-ada-002
"""

import os
import logging
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
import json
from dataclasses import dataclass

logger = logging.getLogger("Genassista-EDU-pythonAPI.embedding")

@dataclass
class EmbeddingConfig:
    """Configuration for embedding service"""
    api_key: str
    model: str = "text-embedding-ada-002"
    base_url: str = "https://api.openai.com/v1"
    max_tokens: int = 8191
    batch_size: int = 100

class EmbeddingService:
    """Handles text embeddings for RAG system"""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        # Support both Groq and OpenAI API keys (Groq uses OpenAI-compatible API)
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        api_key = groq_key or openai_key
        
        # Set base URL based on which API key is available
        if groq_key:
            base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        else:
            base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        
        self.config = config or EmbeddingConfig(
            api_key=api_key,
            base_url=base_url
        )
        
        if not self.config.api_key:
            logger.warning("No API key provided (neither GROQ_API_KEY nor OPENAI_API_KEY). Embedding service will not work.")
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for a single text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None if failed
        """
        if not self.config.api_key:
            logger.error("No API key available for embeddings")
            return None
        
        try:
            # Truncate text if too long
            if len(text) > self.config.max_tokens * 4:  # Rough estimate
                text = text[:self.config.max_tokens * 4]
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "input": text,
                    "model": self.config.model
                }
                
                async with session.post(
                    f"{self.config.base_url}/embeddings",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["data"][0]["embedding"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Embedding API error: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Get embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors (None for failed ones)
        """
        if not self.config.api_key:
            logger.error("No API key available for embeddings")
            return [None] * len(texts)
        
        # Process in batches
        results = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)
        
        return results
    
    async def _process_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Process a batch of texts for embeddings"""
        try:
            # Truncate texts if needed
            truncated_texts = []
            for text in texts:
                if len(text) > self.config.max_tokens * 4:
                    text = text[:self.config.max_tokens * 4]
                truncated_texts.append(text)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "input": truncated_texts,
                    "model": self.config.model
                }
                
                async with session.post(
                    f"{self.config.base_url}/embeddings",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return [item["embedding"] for item in result["data"]]
                    else:
                        error_text = await response.text()
                        logger.error(f"Batch embedding API error: {response.status} - {error_text}")
                        return [None] * len(texts)
        
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            return [None] * len(texts)
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import numpy as np
            
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
        
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]]) -> Dict[str, Any]:
        """
        Find the most similar embedding from a list of candidates
        
        Args:
            query_embedding: Query vector
            candidate_embeddings: List of candidate vectors
        
        Returns:
            Dictionary with index and similarity score
        """
        if not candidate_embeddings:
            return {"index": -1, "similarity": 0.0}
        
        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            if candidate is not None:
                sim = self.cosine_similarity(query_embedding, candidate)
                similarities.append((i, sim))
        
        if not similarities:
            return {"index": -1, "similarity": 0.0}
        
        # Find best match
        best_index, best_similarity = max(similarities, key=lambda x: x[1])
        
        return {
            "index": best_index,
            "similarity": best_similarity
        }
    
    async def embed_document_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add embeddings to document chunks
        
        Args:
            chunks: List of chunk dictionaries with 'content' field
        
        Returns:
            Updated chunks with embeddings
        """
        if not self.config.api_key:
            logger.warning("No API key - returning chunks without embeddings")
            return chunks
        
        # Extract texts
        texts = [chunk['content'] for chunk in chunks]
        
        # Get embeddings
        embeddings = await self.get_embeddings_batch(texts)
        
        # Add embeddings to chunks
        updated_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            updated_chunk = chunk.copy()
            if embedding is not None:
                updated_chunk['embedding'] = embedding
                updated_chunk['has_embedding'] = True
            else:
                updated_chunk['has_embedding'] = False
                logger.warning(f"Failed to get embedding for chunk {i}")
            
            updated_chunks.append(updated_chunk)
        
        return updated_chunks
    
    def validate_embedding(self, embedding: List[float]) -> bool:
        """Validate that an embedding is properly formatted"""
        if not isinstance(embedding, list):
            return False
        
        if len(embedding) == 0:
            return False
        
        # Check if all elements are numbers
        try:
            for val in embedding:
                float(val)
            return True
        except (ValueError, TypeError):
            return False

# Global instance
embedding_service = EmbeddingService()
