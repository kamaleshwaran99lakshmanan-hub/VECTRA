"""
Incident API endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List
from app.models.incident import Incident
from app.services.incident_service import IncidentService

router = APIRouter()

@router.get("/", response_model=List[Incident])
async def get_incidents(request: Request):
    """Get all incidents"""
    service: IncidentService = request.app.state.incident_service
    return service.get_all_incidents()

@router.get("/active", response_model=List[Incident])
async def get_active_incidents(request: Request):
    """Get active incidents"""
    service: IncidentService = request.app.state.incident_service
    return service.get_active_incidents()

@router.post("/", response_model=Incident)
async def create_incident(incident: Incident, request: Request):
    """Create a new incident"""
    service: IncidentService = request.app.state.incident_service
    created = service.create_incident(incident.dict())
    if not created:
        raise HTTPException(status_code=400, detail="Failed to create incident")
    return created

@router.put("/{incident_id}/resolve")
async def resolve_incident(incident_id: str, request: Request):
    """Resolve an incident"""
    service: IncidentService = request.app.state.incident_service
    resolved = service.resolve_incident(incident_id)
    if not resolved:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"status": "success", "incident": resolved}

@router.get("/{incident_id}")
async def get_incident(incident_id: str, request: Request):
    """Get incident by ID"""
    service: IncidentService = request.app.state.incident_service
    incident = service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident