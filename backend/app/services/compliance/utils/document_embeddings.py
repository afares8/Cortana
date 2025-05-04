from typing import List, Dict, Any, Optional, Tuple
import os
import logging
import tempfile
from pathlib import Path
import numpy as np
import faiss
import pdfplumber
import pickle
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangchainDocument

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual model that works well with Spanish
EMBEDDING_DIMENSION = 384  # Dimension of the embeddings for the selected model
CHUNK_SIZE = 1000  # Size of text chunks for embedding
CHUNK_OVERLAP = 200  # Overlap between chunks
FAISS_INDEX_PATH = "compliance_manual_index.faiss"
DOCUMENT_CHUNKS_PATH = "compliance_manual_chunks.pkl"

class DocumentEmbeddings:
    """
    Class for creating and querying document embeddings using Sentence Transformers and FAISS.
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL, index_path: Optional[str] = None, chunks_path: Optional[str] = None):
        """
        Initialize the document embeddings system.
        
        Args:
            model_name: Name of the Sentence Transformers model to use
            index_path: Path to the FAISS index file
            chunks_path: Path to the document chunks file
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path or FAISS_INDEX_PATH
        self.chunks_path = chunks_path or DOCUMENT_CHUNKS_PATH
        self.index = None
        self.document_chunks = []
        
        self._load_resources()
    
    def _load_resources(self) -> None:
        """
        Load the FAISS index and document chunks if they exist.
        """
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.chunks_path, 'rb') as f:
                    self.document_chunks = pickle.load(f)
                logger.info(f"Loaded existing index with {self.index.ntotal} vectors and {len(self.document_chunks)} document chunks")
            else:
                logger.info("No existing index found. Will create a new one when documents are added.")
                self.index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
                self.document_chunks = []
        except Exception as e:
            logger.error(f"Error loading resources: {str(e)}")
            self.index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
            self.document_chunks = []
    
    def _save_resources(self) -> None:
        """
        Save the FAISS index and document chunks.
        """
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.chunks_path, 'wb') as f:
                pickle.dump(self.document_chunks, f)
            logger.info(f"Saved index with {self.index.ntotal} vectors and {len(self.document_chunks)} document chunks")
        except Exception as e:
            logger.error(f"Error saving resources: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def chunk_text(self, text: str) -> List[LangchainDocument]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: Text to split into chunks
            
        Returns:
            List of document chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.create_documents([text])
        return chunks
    
    def embed_document(self, pdf_path: str, document_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Extract text from a PDF, chunk it, and create embeddings.
        
        Args:
            pdf_path: Path to the PDF file
            document_metadata: Additional metadata about the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                logger.error(f"Failed to extract text from {pdf_path}")
                return False
            
            chunks = self.chunk_text(text)
            logger.info(f"Created {len(chunks)} chunks from document")
            
            embeddings = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "chunk_id": i,
                    "source": pdf_path,
                    "page_content": chunk.page_content,
                }
                if document_metadata:
                    chunk_metadata.update(document_metadata)
                
                self.document_chunks.append({
                    "text": chunk.page_content,
                    "metadata": chunk_metadata
                })
                
                embedding = self.model.encode(chunk.page_content)
                embeddings.append(embedding)
            
            if embeddings:
                embeddings_array = np.array(embeddings).astype('float32')
                self.index.add(embeddings_array)
                
                self._save_resources()
                
                logger.info(f"Successfully embedded document with {len(embeddings)} chunks")
                return True
            else:
                logger.error("No embeddings created")
                return False
                
        except Exception as e:
            logger.error(f"Error embedding document: {str(e)}")
            return False
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar chunks to the query.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of similar chunks with their metadata and similarity scores
        """
        try:
            query_embedding = self.model.encode(query).reshape(1, -1).astype('float32')
            
            distances, indices = self.index.search(query_embedding, k=min(k, self.index.ntotal))
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1:  # -1 means no result
                    chunk = self.document_chunks[idx]
                    results.append({
                        "text": chunk["text"],
                        "metadata": chunk["metadata"],
                        "score": float(1.0 - distances[0][i] / 100.0)  # Convert distance to similarity score
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []
    
    def get_relevant_context(self, query: str, k: int = 5) -> str:
        """
        Get relevant context for a query.
        
        Args:
            query: Query text
            k: Number of chunks to include in the context
            
        Returns:
            Concatenated text of the most relevant chunks
        """
        results = self.search(query, k=k)
        if not results:
            return ""
        
        results.sort(key=lambda x: x["score"], reverse=True)
        
        context = "\n\n".join([f"[Relevance: {r['score']:.2f}] {r['text']}" for r in results])
        return context

document_embeddings = DocumentEmbeddings()
