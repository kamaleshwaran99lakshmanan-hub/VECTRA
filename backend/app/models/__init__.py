"""
Domain models for NER-LOGIX
"""

from app.models.vehicle import Vehicle, Position
from app.models.incident import Incident, IncidentType, IncidentSeverity
from app.models.route import Route, RouteSegment

__all__ = [
    "Vehicle", "Position",
    "Incident", "IncidentType", "IncidentSeverity",
    "Route", "RouteSegment"
]