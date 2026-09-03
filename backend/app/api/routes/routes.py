"""
Route API endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from app.services.route_service import RouteService

router = APIRouter()

@router.get("/")
async def get_routes(request: Request):
    """Get all routes for the operations dashboard."""
    service: RouteService = request.app.state.route_service
    return service.get_all_routes()

@router.post("/calculate")
async def calculate_route(request_data: Dict[str, Any], request: Request):
    """Calculate route for a vehicle"""
    service: RouteService = request.app.state.route_service
    vehicle_id = request_data.get("vehicle_id")
    destination = request_data.get("destination")
    
    if not vehicle_id or not destination:
        raise HTTPException(status_code=400, detail="vehicle_id and destination required")
    
    route = service.calculate_route(vehicle_id, destination)
    if not route:
        raise HTTPException(status_code=400, detail="No route found")
    
    return route

@router.get("/{route_id}")
async def get_route(route_id: str, request: Request):
    """Get route by ID"""
    service: RouteService = request.app.state.route_service
    route = service.get_route(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

@router.post("/{route_id}/approve")
async def approve_route(route_id: str, request: Request):
    """Approve a route"""
    service: RouteService = request.app.state.route_service
    approved = service.approve_route(route_id)
    if not approved:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Broadcast via WebSocket
    manager = request.app.state.manager
    await manager.broadcast_json({
        "type": "route_approved",
        "route_id": route_id,
        "message": "Route has been approved by operator"
    })
    
    return {"status": "success", "route": approved}

@router.post("/{route_id}/reject")
async def reject_route(route_id: str, request: Request):
    """Reject a route"""
    service: RouteService = request.app.state.route_service
    rejected = service.reject_route(route_id)
    if not rejected:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Broadcast via WebSocket
    manager = request.app.state.manager
    await manager.broadcast_json({
        "type": "route_rejected",
        "route_id": route_id,
        "message": "Route has been rejected by operator"
    })
    
    return {"status": "success", "route": rejected}

@router.post("/{route_id}/activate")
async def activate_route(route_id: str, request: Request):
    """Activate a route (set as active)"""
    service: RouteService = request.app.state.route_service
    activated = service.activate_route(route_id)
    if not activated:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Broadcast via WebSocket
    manager = request.app.state.manager
    await manager.broadcast_json({
        "type": "route_activated",
        "route_id": route_id,
        "message": "Route has been activated"
    })
    
    return {"status": "success", "route": activated}