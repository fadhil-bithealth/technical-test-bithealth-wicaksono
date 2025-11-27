from pydantic import BaseModel
from typing import List, Optional

class AddDocumentResponse(BaseModel):
    id: int
    status: str