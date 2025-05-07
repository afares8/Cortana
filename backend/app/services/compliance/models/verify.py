from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.models.base import TimestampModel

class CustomerVerification(TimestampModel):
    id: int
    customer_id: Optional[int] = None
    customer_name: str
    customer_type: str  # natural or legal
    verification_data: Dict[str, Any]
    pep_status: str  # clear, watchlist, matched
    sanctions_status: str  # clear, watchlist, matched
    overall_status: str  # clear, watchlist, matched
    created_by: Optional[int] = None  # user_id
    notes: Optional[str] = None
