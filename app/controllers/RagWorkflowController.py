
from typing import Dict, Any
from app.schemas.QuestionRequestSchema import QuestionRequest
from app.services.RagWorkflowService import WorkflowService
from app.tools.DocumentStoringTool import StorageTool
import logging
import time
from langgraph.graph import StateGraph, END  # LangGraph pindah ke Controller
from app.services.RagWorkflowService import WorkflowService

# Setup logger
logger = logging.getLogger(__name__)

class WorkflowController:
    def __init__(self):
        """
        Controller ini bertanggung jawab untuk:
        1. Setup Dependencies.
        2. Mendefinisikan & Mengkompilasi Workflow (Graph).
        """
        # 1. Init Services & Tools
        self.storage_service = StorageTool()
        self.workflow_service = WorkflowService(self.storage_service)
        
        # 2. Initiate Workflow/Graph (Orchestration)
        self.app = self._build_graph()

    def _build_graph(self):
        """
        Mendefinisikan struktur 'Workflow-nya mau gimana'.
        Controller mengatur alur, tapi logic detailnya memanggil Service.
        """
        workflow = StateGraph(dict)
        
        # Add Nodes (Menggunakan function dari WorkflowService)
        workflow.add_node("retrieve", self.workflow_service.retrieve_node)
        workflow.add_node("answer", self.workflow_service.answer_node)
        
        # Set Flow (Edges)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "answer")
        workflow.add_edge("answer", END)
        
        return workflow.compile()

    async def handle_ask_question(self, req: QuestionRequest) -> Dict[str, Any]:
        """
        Endpoint handler.
        """
        start = time.time()
        try:
            # Controller menjalankan graph yang sudah disusun
            result = self.app.invoke({"question": req.question})
            
            return {
                "question": req.question,
                "answer": result["answer"],
                "context_used": result.get("context", []),
                "latency_sec": round(time.time() - start, 3)
            }
            
        except Exception as e:
            logger.error(f"Error in ask_question: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"RAG Workflow failed: {str(e)}",
                "status_code": 500
            }
            
    async def is_workflow_ready(self) -> bool:
        return self.app is not None

# Global instance
workflow_controller = WorkflowController()