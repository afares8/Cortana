from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ContextualGenerateRequest(BaseModel):
    """
    Request schema for the contextual generate endpoint.
    """
    query: str
    user_id: Optional[int] = None
    max_new_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    debug: Optional[bool] = False

class ContextualGenerateResponse(BaseModel):
    """
    Response schema for the contextual generate endpoint.
    """
    generated_text: str
    is_fallback: bool = False
    model: str = "teknium/OpenHermes-2.5-Mistral-7B"
    intent: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    original_query: Optional[str] = None
    enhanced_prompt: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
