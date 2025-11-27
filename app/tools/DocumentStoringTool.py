from app.config.qdrant import qdrant_db

class StorageTool:
    def __init__(self):
        self.docs_memory = []
        self.using_qdrant = False
        
        # Init connection logic setup
        if qdrant_db.is_available():
            # Ensure collection exists on startup
            qdrant_db.create_collection(qdrant_db.collection_name, force_recreate=True)
            self.using_qdrant = True
        else:
            print("⚠️ Qdrant not available. Using in-memory fallback.")
            self.using_qdrant = False

    def add_document(self, text: str) -> int:
        doc_id = len(self.docs_memory)
        self.docs_memory.append(text)

        if self.using_qdrant:
            # Siapkan dokumen dalam format dict
            doc = {
                "id": doc_id,
                "text": text
                # "vector": ... (akan di-generate otomatis oleh QdrantDB)
            }
            # Delegate ke QdrantDB wrapper
            qdrant_db.index_documents([doc])
            
        return doc_id

    def search(self, query: str, limit: int = 2) -> list:
        results = []
        if self.using_qdrant:
            # Delegate search ke QdrantDB wrapper (otomatis embed query)
            hits = qdrant_db.search(query_text=query, limit=limit)
            for hit in hits:
                results.append(hit.payload["text"])
        else:
            # Fallback logic
            for doc in self.docs_memory:
                if query.lower() in doc.lower():
                    results.append(doc)
            if not results and self.docs_memory:
                results = [self.docs_memory[0]]
        return results

    def get_status(self):
        return {
            "qdrant_ready": self.using_qdrant,
            "in_memory_docs_count": len(self.docs_memory)
        }