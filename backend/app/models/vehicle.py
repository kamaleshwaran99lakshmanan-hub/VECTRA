"""
Vehicle domain models
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Position(BaseModel):
    """GPS position"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    
    class Config:
        json_schema_extra = {
            "example": {"lat": 26.1445, "lng": 91.7362}
        }

class Vehicle(BaseModel):
    """Vehicle model"""
    id: str = Field(..., description="Vehicle identifier")
    name: str = Field(..., description="Vehicle name")
    position: Position = Field(..., description="Current GPS position")
    speed: float = Field(0.0, ge=0, description="Current speed in km/h")
    heading: float = Field(0.0, ge=0, lt=360, description="Direction in degrees")
    status: str = Field("active", description="Vehicle status: active, idle, stopped")
    route_id: Optional[str] = Field(None, description="Current route ID")
    current_segment: Optional[str] = Field(None, description="Current road segment")
    destination: Optional[str] = Field(None, description="Destination node")
    eta: Optional[datetime] = Field(None, description="Estimated time of arrival")
    last_updated: datetime = Field(default_factory=datetime.now)
    fuel_level: float = Field(100.0, ge=0, le=100, description="Fuel level percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "V001",
                "name": "Truck-01",
                "position": {"lat": 26.1445, "lng": 91.7362},
                "speed": 60.0,
                "heading": 45.0,
                "status": "active",
                "route_id": "R001",
                "destination": "E",
                "fuel_level": 75.0
            }
        }