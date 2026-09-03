"""
Route Pydantic schemas for API validation
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RouteCreate(BaseModel):
    """Schema for creating a route"""
    vehicle_id: str
    destination: str
    is_alternative: bool = False

class RouteUpdate(BaseModel):
    """Schema for updating a route"""
    status: Optional[str] = None
    approved_at: Optional[datetime] = None