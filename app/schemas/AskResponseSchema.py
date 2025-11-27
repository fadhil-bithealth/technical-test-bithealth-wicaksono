from pydantic import BaseModel
from typing import List, Optional

class AskResponse(BaseModel):
    question: str
    answer: str
    context_used: List[str]
    latency_sec: float
