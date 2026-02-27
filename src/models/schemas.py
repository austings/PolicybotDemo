# src/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class Justification(BaseModel):
    reason: str
    details: Optional[str] = None

class Audit(BaseModel):
    timestamp: str
    method: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class InferredCode(BaseModel):
    code: str
    confidence: float
    justification: Justification

class InferenceResult(BaseModel):
    inferred_codes: List[InferredCode] = Field(default_factory=list)
    audit: Audit
    
class CachedInferenceEntry(BaseModel):
    key: str
    result: InferenceResult

class CachedResultStore(BaseModel):
    version: str = "v1"
    entries: Dict[str, InferenceResult] = Field(default_factory=dict)
    
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()