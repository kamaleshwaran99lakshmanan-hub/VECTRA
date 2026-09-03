"""
Pydantic schemas for NER-LOGIX
"""

from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.schemas.route import RouteCreate, RouteUpdate

__all__ = [
    "VehicleCreate", "VehicleUpdate",
    "IncidentCreate", "IncidentUpdate",
    "RouteCreate", "RouteUpdate"
]