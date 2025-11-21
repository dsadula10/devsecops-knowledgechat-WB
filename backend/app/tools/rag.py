import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os
from app.models import PolicySearchResult


class RAGTool:
    """RAG tool for searching security policies using ChromaDB"""
    
    def __init__(self):
        self.chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME", "security_policies")
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def search(self, query: str, top_k: int = 3) -> List[PolicySearchResult]:
        """Search security policies using semantic similarity"""
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Parse results
        search_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 1.0
                
                search_results.append(PolicySearchResult(
                    content=doc,
                    source=metadata.get('source', 'Unknown'),
                    page=metadata.get('page'),
                    score=1.0 - distance  # Convert distance to similarity score
                ))
        
        return search_results
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Generate IDs
        ids = [f"doc_{i}_{hash(doc)}" for i, doc in enumerate(documents)]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        """Return tool definition for the agent"""
        return {
            "name": "search_policies",
            "description": "Search security policies and guidelines using semantic similarity. Use this to answer questions about security policies, OWASP guidelines, password requirements, encryption standards, compliance requirements, and company security procedures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant policy information"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top results to return (default: 3)",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
