from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse
from typing import List, Dict, Any, Union
from app.config.setting import settings
from app.services.EmbeddingService import embedding_manager

class QdrantDB:
    """
    A class for interacting with Qdrant database.
    
    Attributes:
        client: Qdrant client instance
        collection_name: Current active collection
    """
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = settings.VECTOR_SIZE
        
        try:
            self.client = QdrantClient(url=settings.QDRANT_URL)
            # Check connection basic info
            self.client.get_collections()
        except Exception as e:
            # Sesuai referensi, kita log atau allow failure (di sini saya set client None agar Service tau)
            print(f"Failed to connect to Qdrant: {str(e)}")
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    def check_if_collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists in Qdrant."""
        if not self.client: return False
        try:
            return self.client.collection_exists(collection_name=collection_name)
        except Exception:
            return False

    def create_collection(self, collection_name: str, force_recreate: bool = False) -> None:
        """Create a new collection with specified vector params."""
        if not self.client: return

        if self.check_if_collection_exists(collection_name) and not force_recreate:
            return 
        
        # Qdrant recreate_collection handles delete + create
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
        )

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        if not self.client: return
        try:
            self.client.delete_collection(collection_name=collection_name)
        except Exception:
            pass

    def index_documents(
        self, 
        docs: List[Dict[str, Any]], 
        collection_name: str = None
    ) -> bool:
        """
        Index documents into Qdrant. 
        Automatically generates embeddings for 'text' field if vector is missing.
        """
        if not self.client: return False
        
        target_collection = collection_name or self.collection_name
        points = []

        for doc in docs:
            text = doc.get("text", "")
            doc_id = doc.get("id")
            
            # Generate embedding using our manager if not present
            vector = doc.get("vector")
            if not vector and text:
                vector = embedding_manager.fake_embed(text)
            
            if vector and doc_id is not None:
                # Payload is everything except vector and id
                payload = {k: v for k, v in doc.items() if k not in ["vector", "id"]}
                
                points.append(PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload
                ))

        if points:
            try:
                self.client.upsert(
                    collection_name=target_collection,
                    points=points
                )
                return True
            except Exception as e:
                print(f"Error indexing documents: {e}")
                return False
        return False

    def search(self, query_text: str, limit: int = 2, collection_name: str = None) -> List[Any]:
        """
        Search for nearest neighbors.
        Automatically converts query text to embedding.
        """
        if not self.client: return []
        
        target_collection = collection_name or self.collection_name
        
        # Generate query embedding
        query_vector = embedding_manager.fake_embed(query_text)
        
        try:
            hits = self.client.search(
                collection_name=target_collection,
                query_vector=query_vector,
                limit=limit
            )
            return hits
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return []

# Global instance
qdrant_db = QdrantDB()