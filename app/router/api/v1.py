from fastapi import APIRouter, HTTPException
from app.schemas.AskResponseSchema import AskResponse
from app.schemas.DocumentResponseSchema import AddDocumentResponse
from app.schemas.QuestionRequestSchema import  QuestionRequest
from app.schemas.DocumentRequestSchema import DocumentRequest
from app.schemas.AskResponseSchema import AskResponse
from app.controllers.RagWorkflowController import workflow_controller
from app.controllers.DocumentStoringController import storage_controller

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_endpoint(req: QuestionRequest):
    # Panggil WorkflowController
    result = await workflow_controller.handle_ask_question(req)
    
    if "success" in result and result["success"] is False:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result["message"])
        
    return result

@router.post("/add", response_model=AddDocumentResponse)
async def add_endpoint(req: DocumentRequest):
    # Panggil StorageController
    result = await storage_controller.handle_add_document(req)
    
    if "success" in result and result["success"] is False:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result["message"])
        
    return result

@router.get("/status")
async def status_endpoint():
    storage_status = await storage_controller.get_storage_status()
    workflow_ready = await workflow_controller.is_workflow_ready()
    
    storage_status["graph_ready"] = workflow_ready
    return storage_status