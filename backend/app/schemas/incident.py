"""
Incident Pydantic schemas for API validation
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.incident import IncidentType, IncidentSeverity

class IncidentCreate(BaseModel):
    """Schema for creating an incident"""
    type: IncidentType
    severity: IncidentSeverity
    description: str
    location_lat: float
    location_lng: float
    affected_segments: List[str]
    risk_score: Optional[float] = None

class IncidentUpdate(BaseModel):
    """Schema for updating an incident"""
    severity: Optional[IncidentSeverity] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    risk_score: Optional[float] = None