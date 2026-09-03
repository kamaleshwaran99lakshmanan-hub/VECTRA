"""
Route domain models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class RouteSegment(BaseModel):
    coordinates: List[Dict[str, float]] = Field(
    default_factory=list,
    description="Geographic coordinates for the road segment"
)
    """Individual route segment"""
    id: str = Field(..., description="Segment identifier")
    from_node: str = Field(..., description="Start node")
    to_node: str = Field(..., description="End node")
    distance: float = Field(..., ge=0, description="Distance in kilometers")
    travel_time: float = Field(..., ge=0, description="Travel time in minutes")
    risk_score: float = Field(0.0, ge=0, le=100, description="Risk score for segment")
    road_status: str = Field("normal", description="Road status")
    blocked: bool = Field(False, description="Whether segment is blocked")
    speed_limit: float = Field(60.0, ge=0, description="Speed limit in km/h")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "A-B",
                "from_node": "A",
                "to_node": "B",
                "distance": 15.5,
                "travel_time": 18.6,
                "risk_score": 15.0,
                "road_status": "good",
                "blocked": False,
                "speed_limit": 60.0
            }
        }

class Route(BaseModel):
    """Complete route model"""
    id: str = Field(..., description="Route identifier")
    vehicle_id: str = Field(..., description="Vehicle identifier")
    segments: List[RouteSegment] = Field(..., description="Route segments")
    total_distance: float = Field(..., ge=0, description="Total distance in kilometers")
    total_time: float = Field(..., ge=0, description="Total time in minutes")
    total_risk: float = Field(0.0, ge=0, le=100, description="Total risk score")
    status: str = Field("proposed", description="Route status: proposed, approved, active, rejected")
    created_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    is_alternative: bool = Field(False, description="Whether this is an alternative route")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ROUTE001",
                "vehicle_id": "V001",
                "segments": [],
                "total_distance": 45.2,
                "total_time": 54.5,
                "total_risk": 25.0,
                "status": "proposed"
            }
        }