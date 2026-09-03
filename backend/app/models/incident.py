"""
Incident domain models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class IncidentType(str, Enum):
    """Types of incidents"""
    ROAD_BLOCKAGE = "road_blockage"
    ACCIDENT = "accident"
    HEAVY_RAIN = "heavy_rain"
    ROAD_DEGRADATION = "road_degradation"
    WEATHER = "weather"
    FLOODING = "flooding"
    LANDSLIDE = "landslide"
    CONSTRUCTION = "construction"

class IncidentSeverity(str, Enum):
    """Severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Incident(BaseModel):
    """Incident model"""
    id: str = Field(..., description="Incident identifier")
    type: IncidentType = Field(..., description="Type of incident")
    severity: IncidentSeverity = Field(..., description="Severity level")
    description: str = Field(..., description="Incident description")
    location: dict = Field(..., description="Location coordinates {lat, lng}")
    affected_segments: List[str] = Field(default_factory=list, description="Affected road segments")
    timestamp: datetime = Field(default_factory=datetime.now)
    active: bool = Field(True, description="Whether incident is active")
    risk_score: Optional[float] = Field(None, ge=0, le=100, description="Calculated risk score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "INC001",
                "type": "road_blockage",
                "severity": "CRITICAL",
                "description": "Road blockage on segment C-D",
                "location": {"lat": 26.1500, "lng": 91.7400},
                "affected_segments": ["C-D"],
                "risk_score": 95.0
            }
        }