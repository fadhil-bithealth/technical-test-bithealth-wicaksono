from pydantic import BaseModel
from typing import List, Optional


class DocumentRequest(BaseModel):
    text: str
