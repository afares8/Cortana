from typing import Optional, Dict, Any
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    """Request model for the generate endpoint."""
    inputs: str
    max_new_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    do_sample: Optional[bool] = True
    repetition_penalty: Optional[float] = 1.1
    debug: Optional[bool] = False

class GenerateResponse(BaseModel):
    """Response model for the generate endpoint."""
    generated_text: str
    is_fallback: bool
    model: str
    error: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
