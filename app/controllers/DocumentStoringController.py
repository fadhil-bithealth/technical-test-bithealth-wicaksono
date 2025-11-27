import logging
from typing import Dict, Any

from app.schemas.DocumentRequestSchema import DocumentRequest
from app.tools.DocumentStoringTool import StorageTool

# Setup logger
logger = logging.getLogger(__name__)

class StorageController:
    def __init__(self):
        """
        Controller khusus untuk manajemen Storage/Database.
        """
        self.storage_service = StorageTool()

    async def handle_add_document(self, req: DocumentRequest) -> Dict[str, Any]:
        """
        Menangani penambahan dokumen baru.
        """
        try:
            doc_id = self.storage_service.add_document(req.text)
            return {"id": doc_id, "status": "added"}
            
        except Exception as e:
            logger.error(f"Error in add_document: {e}", exc_info=True)
            return {
                "success": False, 
                "message": f"Failed to add document: {str(e)}",
                "status_code": 500
            }

    async def get_storage_status(self) -> Dict[str, Any]:
        """
        Cek status spesifik untuk Storage (Qdrant/Memory).
        """
        try:
            return self.storage_service.get_status()
        except Exception as e:
            logger.error(f"Error checking storage status: {e}")
            return {"error": str(e)}

# Global instance
storage_controller = StorageController()