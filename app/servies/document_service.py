"""
Document Processing Service for RAG System
Handles PDF, Word, and image (handwriting) processing with OCR
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import tempfile
import mimetypes

# Document processing imports
import PyPDF2
import docx
from PIL import Image
import pytesseract
import easyocr

logger = logging.getLogger("Genassista-EDU-pythonAPI.document")

class DocumentProcessor:
    """Processes various document types for RAG system"""
    
    def __init__(self):
        self.supported_types = {
            'application/pdf': self._process_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._process_docx,
            'application/msword': self._process_doc,
            'image/jpeg': self._process_image,
            'image/png': self._process_image,
            'image/tiff': self._process_image,
        }
        
        # Initialize OCR engines
        self.easyocr_reader = None
        self._init_ocr()
    
    def _init_ocr(self):
        """Initialize OCR engines"""
        try:
            # EasyOCR for better handwriting recognition
            self.easyocr_reader = easyocr.Reader(['en', 'sv'])
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
            self.easyocr_reader = None
    
    def process_document(self, file_path: Union[str, Path], 
                        file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a document and extract text content
        
        Args:
            file_path: Path to the document
            file_type: MIME type of the document (auto-detected if None)
        
        Returns:
            Dictionary with extracted content and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect file type if not provided
        if file_type is None:
            file_type, _ = mimetypes.guess_type(str(file_path))
        
        if file_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        try:
            # Process the document
            processor = self.supported_types[file_type]
            result = processor(file_path)
            
            # Add metadata
            result.update({
                'file_name': file_path.name,
                'file_type': file_type,
                'file_size': file_path.stat().st_size,
                'processing_success': True
            })
            
            logger.info(f"Successfully processed {file_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            return {
                'file_name': file_path.name,
                'file_type': file_type,
                'content': '',
                'processing_success': False,
                'error': str(e)
            }
    
    def _process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Process PDF documents"""
        content = ""
        pages = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        content += page_text + "\n"
                        pages.append({
                            'page_number': page_num + 1,
                            'content': page_text.strip()
                        })
                
                return {
                    'content': content.strip(),
                    'pages': pages,
                    'total_pages': len(pdf_reader.pages),
                    'document_type': 'pdf'
                }
        except Exception as e:
            logger.error(f"PDF processing error: {e}")
            raise
    
    def _process_docx(self, file_path: Path) -> Dict[str, Any]:
        """Process DOCX documents"""
        try:
            doc = docx.Document(file_path)
            content = ""
            paragraphs = []
            
            for para in doc.paragraphs:
                para_text = para.text.strip()
                if para_text:
                    content += para_text + "\n"
                    paragraphs.append({
                        'text': para_text,
                        'style': para.style.name if para.style else 'Normal'
                    })
            
            return {
                'content': content.strip(),
                'paragraphs': paragraphs,
                'document_type': 'docx'
            }
        except Exception as e:
            logger.error(f"DOCX processing error: {e}")
            raise
    
    def _process_doc(self, file_path: Path) -> Dict[str, Any]:
        """Process legacy DOC documents (converts to DOCX first)"""
        # For legacy DOC files, we'd need python-docx2txt or similar
        # For now, return basic processing
        return {
            'content': f"Legacy DOC file: {file_path.name}",
            'document_type': 'doc',
            'note': 'Legacy DOC format - limited processing available'
        }
    
    def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """Process images with OCR for handwriting recognition"""
        try:
            # Load image
            image = Image.open(file_path)
            
            # Try EasyOCR first (better for handwriting)
            if self.easyocr_reader:
                try:
                    results = self.easyocr_reader.readtext(str(file_path))
                    content = " ".join([result[1] for result in results])
                    confidence_scores = [result[2] for result in results]
                    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
                    
                    return {
                        'content': content,
                        'ocr_method': 'easyocr',
                        'confidence': avg_confidence,
                        'document_type': 'image_ocr'
                    }
                except Exception as e:
                    logger.warning(f"EasyOCR failed, falling back to Tesseract: {e}")
            
            # Fallback to Tesseract
            content = pytesseract.image_to_string(image, lang='eng+swe')
            
            return {
                'content': content.strip(),
                'ocr_method': 'tesseract',
                'document_type': 'image_ocr'
            }
            
        except Exception as e:
            logger.error(f"Image OCR processing error: {e}")
            raise
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from document content"""
        words = content.split()
        sentences = content.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'character_count': len(content),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'average_sentence_length': len(words) / len(sentences) if sentences else 0
        }
    
    def chunk_content(self, content: str, chunk_size: int = 1000, 
                     overlap: int = 200) -> List[Dict[str, Any]]:
        """
        Split content into chunks for vector storage
        
        Args:
            content: Text content to chunk
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks
        
        Returns:
            List of chunk dictionaries
        """
        if len(content) <= chunk_size:
            return [{
                'content': content,
                'chunk_index': 0,
                'start_char': 0,
                'end_char': len(content)
            }]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence endings within the last 100 characters
                search_start = max(start, end - 100)
                sentence_end = content.rfind('.', search_start, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk_content = content[start:end].strip()
            if chunk_content:
                chunks.append({
                    'content': chunk_content,
                    'chunk_index': chunk_index,
                    'start_char': start,
                    'end_char': end,
                    'word_count': len(chunk_content.split())
                })
                chunk_index += 1
            
            start = end - overlap if end < len(content) else end
        
        return chunks

# Global instance
document_processor = DocumentProcessor()
