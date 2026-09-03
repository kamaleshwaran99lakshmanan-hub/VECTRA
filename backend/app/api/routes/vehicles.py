"""
Vehicle API endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List
from app.models.vehicle import Vehicle, Position
from app.services.vehicle_service import VehicleService

router = APIRouter()

@router.get("/", response_model=List[Vehicle])
async def get_vehicles(request: Request):
    """Get all vehicles"""
    service: VehicleService = request.app.state.vehicle_service
    return service.get_all_vehicles()

@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str, request: Request):
    """Get vehicle by ID"""
    service: VehicleService = request.app.state.vehicle_service
    vehicle = service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.put("/{vehicle_id}/position")
async def update_vehicle_position(vehicle_id: str, position: Position, request: Request):
    """Update vehicle position"""
    service: VehicleService = request.app.state.vehicle_service
    vehicle = service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    updated = service.update_position(vehicle_id, position.dict())
    return {"status": "success", "vehicle": updated}

@router.put("/{vehicle_id}/status")
async def update_vehicle_status(vehicle_id: str, status: str, request: Request):
    """Update vehicle status"""
    service: VehicleService = request.app.state.vehicle_service
    vehicle = service.update_status(vehicle_id, status)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"status": "success", "vehicle": vehicle}

@router.get("/{vehicle_id}/route")
async def get_vehicle_route(vehicle_id: str, request: Request):
    """Get vehicle's current route"""
    service: VehicleService = request.app.state.vehicle_service
    route = service.get_vehicle_route(vehicle_id)
    if not route:
        raise HTTPException(status_code=404, detail="No route found for vehicle")
    return route