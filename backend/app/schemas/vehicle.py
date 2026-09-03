"""
Vehicle Pydantic schemas for API validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VehicleCreate(BaseModel):
    """Schema for creating a vehicle"""
    name: str
    position_lat: float
    position_lng: float
    speed: float = 0
    heading: float = 0
    status: str = "active"
    destination: Optional[str] = None

class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle"""
    name: Optional[str] = None
    position_lat: Optional[float] = None
    position_lng: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    status: Optional[str] = None
    destination: Optional[str] = None