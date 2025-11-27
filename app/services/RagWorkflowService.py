from app.tools.DocumentStoringTool import StorageTool  # <-- Changed to tools

class WorkflowService:
    def __init__(self, storage_service: StorageTool):
        """
        Service ini HANYA berisi detail eksekusi (Business Logic):
        - Logic Retrieval (Panggil Storage)
        - Logic Generation (Panggil LLM)
        
        Tidak ada definisi Graph di sini.
        """
        self.storage = storage_service

    # --- NODE IMPLEMENTATIONS (Detail Logic) ---
    # Method dibuat public agar bisa dipanggil oleh Controller saat menyusun Graph
    
    def retrieve_node(self, state):
        """
        Logic untuk Node Retrieval.
        Mengambil pertanyaan dari state -> Search di Storage -> Simpan context ke state.
        """
        query = state["question"]
        # Pemanggilan Tools (Storage Service)
        results = self.storage.search(query)
        state["context"] = results
        return state

    def answer_node(self, state):
        """
        Logic untuk Node Answer.
        Mengambil context dari state -> Generate jawaban via LLM -> Simpan answer ke state.
        """
        ctx = state["context"]
        # Pemanggilan logic LLM (bisa dipisah lagi ke LLMService jika kompleks)
        answer = self._call_llm_generation(ctx)
        state["answer"] = answer
        return state

    # --- INTERNAL HELPER / TOOLS ---

    def _call_llm_generation(self, context: list) -> str:
        """
        Simulasi pemanggilan LLM.
        """
        if context:
            # Logic prompt engineering sederhana
            return f"Based on context, I found this: '{context[0][:100]}...'"
        else:
            return "Sorry, I don't know based on the available context."