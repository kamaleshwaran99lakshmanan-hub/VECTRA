"""
Route service layer
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.models.route import Route, RouteSegment
from app.core.database import db
from app.routing.route_optimizer import RouteOptimizer
from app.services.vehicle_service import VehicleService
import logging

logger = logging.getLogger(__name__)

class RouteService:
    """Service for route operations"""
    
    def __init__(self):
        self.db = db
        self.route_optimizer = RouteOptimizer()
        self.vehicle_service = VehicleService()
    
    def get_all_routes(self) -> List[Route]:
        """Get all routes"""
        routes_data = self.db.get_routes()
        return [Route(**r) for r in routes_data]
    
    def get_route(self, route_id: str) -> Optional[Route]:
        """Get route by ID"""
        route_data = self.db.get_route(route_id)
        if route_data:
            return Route(**route_data)
        return None
    
    def get_vehicle_route(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get vehicle's current route"""
        vehicle = self.vehicle_service.get_vehicle(vehicle_id)
        if not vehicle or not vehicle.route_id:
            return None
        
        route = self.get_route(vehicle.route_id)
        if route:
            return route.dict()
        return None
    
    def calculate_route(self, vehicle_id: str, destination: str) -> Optional[Dict[str, Any]]:
        """Calculate route for a vehicle"""
        vehicle = self.vehicle_service.get_vehicle(vehicle_id)
        if not vehicle:
            logger.error(f"Vehicle {vehicle_id} not found")
            return None
        
        # Get current position as origin
        origin = "A"  # Default starting point
        
        # Find route using optimizer
        route_result = self.route_optimizer.find_shortest_route(origin, destination)
        if not route_result:
            logger.error(f"No route found from {origin} to {destination}")
            return None
        
        # Create route object
        route_id = f"ROUTE{str(uuid.uuid4())[:6].upper()}"
        
        segments = []
        for seg in route_result['segments']:
            segments.append(RouteSegment(**seg))
        
        route = Route(
            id=route_id,
            vehicle_id=vehicle_id,
            segments=segments,
            total_distance=route_result['total_distance'],
            total_time=route_result['total_time'],
            total_risk=route_result['total_risk'],
            status="proposed"
        )
        
        # Save route
        self.db.add_route(route.dict())
        
        # Update vehicle with route
        self.db.update_vehicle(vehicle_id, {"route_id": route_id, "destination": destination})
        
        logger.info(f"Calculated route {route_id} for vehicle {vehicle_id}")
        return route.dict()
    
    def calculate_alternative_route(self, vehicle_id: str, destination: str, 
                                   exclude_segments: List[str] = None) -> Optional[Dict[str, Any]]:
        """Calculate alternative route avoiding specified segments"""
        vehicle = self.vehicle_service.get_vehicle(vehicle_id)
        if not vehicle:
            logger.error(f"Vehicle {vehicle_id} not found")
            return None
        
        origin = "A"  # Default starting point
        
        # Find alternative route
        route_result = self.route_optimizer.find_alternative_route(
            origin, destination, exclude_segments
        )
        if not route_result:
            logger.error(f"No alternative route found")
            return None
        
        # Create route object
        route_id = f"ROUTE{str(uuid.uuid4())[:6].upper()}"
        
        segments = []
        for seg in route_result['segments']:
            segments.append(RouteSegment(**seg))
        
        route = Route(
            id=route_id,
            vehicle_id=vehicle_id,
            segments=segments,
            total_distance=route_result['total_distance'],
            total_time=route_result['total_time'],
            total_risk=route_result['total_risk'],
            status="proposed",
            is_alternative=True
        )
        
        # Save route
        self.db.add_route(route.dict())
        
        logger.info(f"Calculated alternative route {route_id} for vehicle {vehicle_id}")
        return route.dict()
    
    def approve_route(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Approve a route"""
        route = self.get_route(route_id)
        if not route:
            return None
        
        # Update route status
        route.status = "approved"
        route.approved_at = datetime.now()
        
        self.db.update_route(route_id, route.dict())
        logger.info(f"Route {route_id} approved")
        return route.dict()
    
    def reject_route(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Reject a route"""
        route = self.get_route(route_id)
        if not route:
            return None
        
        # Update route status
        route.status = "rejected"
        
        self.db.update_route(route_id, route.dict())
        logger.info(f"Route {route_id} rejected")
        return route.dict()
    
    def activate_route(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Activate a route"""
        route = self.get_route(route_id)
        if not route:
            return None
        
        # Check if route is approved
        if route.status not in ["approved", "proposed"]:
            logger.error(f"Cannot activate route {route_id} with status {route.status}")
            return None
        
        # Update route status
        route.status = "active"
        
        self.db.update_route(route_id, route.dict())
        
        # Update vehicle with active route
        self.db.update_vehicle(route.vehicle_id, {"route_id": route_id})
        
        logger.info(f"Route {route_id} activated")
        return route.dict()