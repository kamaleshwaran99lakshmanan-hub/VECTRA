"""
Simulation API endpoints
"""

from fastapi import APIRouter, HTTPException, Request
import asyncio
import json
import logging
from app.services.incident_service import IncidentService
from app.services.vehicle_service import VehicleService
from app.services.route_service import RouteService
from app.decision.risk_engine import RiskEngine
from app.routing.route_optimizer import RouteOptimizer

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/start")
async def start_simulation(request: Request):
    """Start the simulation"""
    app = request.app
    
    if app.state.simulation_running:
        return {"status": "already_running", "message": "Simulation is already running"}
    
    app.state.simulation_running = True
    app.state.simulation_task = asyncio.create_task(run_simulation_loop(app))
    
    # Broadcast via WebSocket
    manager = app.state.manager
    await manager.broadcast_json({
        "type": "simulation_started",
        "message": "Simulation has been started",
        "timestamp": asyncio.get_event_loop().time()
    })
    
    return {"status": "started", "message": "Simulation started successfully"}

@router.post("/pause")
async def pause_simulation(request: Request):
    """Pause the simulation"""
    app = request.app
    
    if not app.state.simulation_running:
        return {"status": "not_running", "message": "Simulation is not running"}
    
    app.state.simulation_running = False
    if app.state.simulation_task:
        app.state.simulation_task.cancel()
    
    # Broadcast via WebSocket
    manager = app.state.manager
    await manager.broadcast_json({
        "type": "simulation_paused",
        "message": "Simulation has been paused",
        "timestamp": asyncio.get_event_loop().time()
    })
    
    return {"status": "paused", "message": "Simulation paused successfully"}

@router.post("/reset")
async def reset_simulation(request: Request):
    """Reset the simulation"""
    app = request.app
    
    app.state.simulation_running = False
    if app.state.simulation_task:
        app.state.simulation_task.cancel()
    
    # Reset vehicle positions
    vehicle_service: VehicleService = app.state.vehicle_service
    vehicles = vehicle_service.get_all_vehicles()
    for vehicle in vehicles:
        if vehicle.id == "V001":
            vehicle_service.update_position(vehicle.id, {"lat": 26.1445, "lng": 91.7362})
    
    # Reset route status
    route_service: RouteService = app.state.route_service
    routes = route_service.get_all_routes()
    for route in routes:
        route_service.reject_route(route.id)
    
    # Reset incidents
    incident_service: IncidentService = app.state.incident_service
    incidents = incident_service.get_all_incidents()
    for incident in incidents:
        if incident.active:
            incident_service.resolve_incident(incident.id)
    
    app.state.approval_required = False
    app.state.pending_route = None
    app.state.current_incident = None
    
    # Broadcast via WebSocket
    manager = app.state.manager
    await manager.broadcast_json({
        "type": "simulation_reset",
        "message": "Simulation has been reset",
        "timestamp": asyncio.get_event_loop().time()
    })
    
    return {"status": "reset", "message": "Simulation reset successfully"}

@router.post("/heavy-rain")
async def simulate_heavy_rain(request: Request):
    """Simulate heavy rain"""
    app = request.app
    incident_service: IncidentService = app.state.incident_service
    risk_engine: RiskEngine = app.state.risk_engine
    
    incident_data = {
        "type": "heavy_rain",
        "severity": "HIGH",
        "description": "Heavy rainfall causing flooding and reduced visibility",
        "location": {"lat": 26.1580, "lng": 91.7650},
        "affected_segments": ["C-D"],
        "risk_score": 75
    }
    
    incident = incident_service.create_incident(incident_data)
    app.state.current_incident = incident
    
    # Update risk for affected segments
    for segment_id in incident.affected_segments:
        risk_engine.update_risk(segment_id, {"condition": "hazardous"})
    
    # Check if route needs recalculation
    route_service: RouteService = app.state.route_service
    route_optimizer: RouteOptimizer = app.state.route_optimizer
    vehicle_service: VehicleService = app.state.vehicle_service
    
    # Get vehicle
    vehicle = vehicle_service.get_vehicle("V001")
    if vehicle and vehicle.destination:
        # Calculate alternative route
        origin = vehicle.position
        destination = vehicle.destination
        
        # Recalculate route
        route = route_service.calculate_route("V001", destination)
        if route:
            app.state.pending_route = route
            app.state.approval_required = True
            
            # Broadcast alert
            manager = app.state.manager
            await manager.broadcast_json({
                "type": "route_change_recommended",
                "incident": incident.dict(),
                "current_route": route_service.get_vehicle_route("V001"),
                "recommended_route": route,
                "approval_required": True,
                "message": "Route change recommended due to heavy rain",
                "timestamp": asyncio.get_event_loop().time()
            })
    
    # Broadcast via WebSocket
    manager = app.state.manager
    await manager.broadcast_json({
        "type": "heavy_rain_simulated",
        "incident": incident.dict(),
        "message": "Heavy rain simulation triggered",
        "timestamp": asyncio.get_event_loop().time()
    })
    
    return {"status": "success", "incident": incident.dict()}

@router.post("/road-block")
async def simulate_road_block(request: Request):
    """Simulate road block"""
    app = request.app
    incident_service: IncidentService = app.state.incident_service
    risk_engine: RiskEngine = app.state.risk_engine
    
    incident_data = {
        "type": "road_blockage",
        "severity": "CRITICAL",
        "description": "Road blockage on segment C-D due to fallen tree",
        "location": {"lat": 26.1620, "lng": 91.7750},
        "affected_segments": ["C-D"],
        "risk_score": 95
    }
    
    incident = incident_service.create_incident(incident_data)
    app.state.current_incident = incident
    
    # Update road status
    risk_engine.update_risk("C-D", {"blocked": True, "condition": "hazardous"})
    
    # Recalculate route
    route_service: RouteService = app.state.route_service
    vehicle_service: VehicleService = app.state.vehicle_service
    
    vehicle = vehicle_service.get_vehicle("V001")
    if vehicle and vehicle.destination:
        # Calculate alternative route
        route = route_service.calculate_alternative_route("V001", vehicle.destination, ["C-D"])
        if route:
            app.state.pending_route = route
            app.state.approval_required = True
            
            # Get current route for comparison
            current_route = route_service.get_vehicle_route("V001")
            
            # Broadcast alert
            manager = app.state.manager
            await manager.broadcast_json({
                "type": "route_change_recommended",
                "incident": incident.dict(),
                "current_route": current_route,
                "recommended_route": route,
                "approval_required": True,
                "message": "ROUTE CHANGE RECOMMENDED - Segment C-D is blocked",
                "timestamp": asyncio.get_event_loop().time()
            })
    
    # Broadcast via WebSocket
    manager = app.state.manager
    await manager.broadcast_json({
        "type": "road_block_simulated",
        "incident": incident.dict(),
        "message": "Road block simulation triggered",
        "timestamp": asyncio.get_event_loop().time()
    })
    
    return {"status": "success", "incident": incident.dict()}

@router.post("/road-degradation")
async def simulate_road_degradation(request: Request):
    """Simulate road degradation"""
    app = request.app
    incident_service: IncidentService = app.state.incident_service
    risk_engine: RiskEngine = app.state.risk_engine
    
    incident_data = {
        "type": "road_degradation",
        "severity": "MEDIUM",
        "description": "Road degradation on segment C-D due to heavy traffic",
        "location": {"lat": 26.1600, "lng": 91.7700},
        "affected_segments": ["C-D"],
        "risk_score": 65
    }
    
    incident = incident_service.create_incident(incident_data)
    app.state.current_incident = incident
    
    # Update road condition
    risk_engine.update_risk("C-D", {"condition": "degraded"})
    
    # Broadcast via WebSocket
    manager = app.state.manager
    await manager.broadcast_json({
        "type": "road_degradation_simulated",
        "incident": incident.dict(),
        "message": "Road degradation simulation triggered",
        "timestamp": asyncio.get_event_loop().time()
    })
    
    return {"status": "success", "incident": incident.dict()}

@router.post("/create-incident")
async def create_incident_simulation(request: Request, incident_data: dict):
    """Create custom incident"""
    app = request.app
    incident_service: IncidentService = app.state.incident_service
    risk_engine: RiskEngine = app.state.risk_engine
    
    incident = incident_service.create_incident(incident_data)
    app.state.current_incident = incident
    
    # Update affected segments
    for segment_id in incident.affected_segments:
        risk_engine.update_risk(segment_id, {"condition": incident_data.get("condition", "hazardous")})
    
    # Broadcast via WebSocket
    manager = app.state.manager
    await manager.broadcast_json({
        "type": "incident_created",
        "incident": incident.dict(),
        "message": "New incident created",
        "timestamp": asyncio.get_event_loop().time()
    })
    
    return {"status": "success", "incident": incident.dict()}

@router.get("/status")
async def get_simulation_status(request: Request):
    """Get simulation status"""
    app = request.app
    return {
        "running": app.state.simulation_running,
        "approval_required": app.state.approval_required,
        "active_vehicles": len(app.state.active_vehicles),
        "pending_alerts": len(app.state.pending_alerts),
        "current_incident": app.state.current_incident.dict() if app.state.current_incident else None,
        "timestamp": asyncio.get_event_loop().time()
    }

async def run_simulation_loop(app):
    """Background simulation loop"""
    logger.info("Simulation loop started")
    
    while app.state.simulation_running:
        try:
            # Update vehicle positions
            vehicle_service: VehicleService = app.state.vehicle_service
            vehicles = vehicle_service.get_all_vehicles()
            
            for vehicle in vehicles:
                if vehicle.id == "V001":
                    # Move vehicle along route
                    current_pos = vehicle.position
                    # Simple movement along route
                    new_lat = current_pos.lat + 0.0005
                    new_lng = current_pos.lng + 0.0005
                    
                    # Update position
                    updated = vehicle_service.update_position(
                        vehicle.id,
                        {"lat": new_lat, "lng": new_lng}
                    )
                    
                    # Broadcast position update
                    manager = app.state.manager
                    await manager.broadcast_json({
                        "type": "vehicle_update",
                        "vehicle_id": vehicle.id,
                        "position": {"lat": new_lat, "lng": new_lng},
                        "timestamp": asyncio.get_event_loop().time()
                    })
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
        except asyncio.CancelledError:
            logger.info("Simulation loop cancelled")
            break
        except Exception as e:
            logger.error(f"Simulation loop error: {str(e)}")
            await asyncio.sleep(1)
    
    logger.info("Simulation loop stopped")