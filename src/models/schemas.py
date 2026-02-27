from pydantic import BaseModel
from typing import List, Optional

class Justification(BaseModel):
    reason: str
    details: Optional[str] = None

class Audit(BaseModel):
    timestamp: str
    method: str
    parameters: dict

class InferredCode(BaseModel):
    code: str
    confidence: float
    justification: Justification

class InferenceResult(BaseModel):
    inferred_codes: List[InferredCode]
    audit: Audit