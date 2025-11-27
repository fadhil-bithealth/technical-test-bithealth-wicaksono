from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str
