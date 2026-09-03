"""
Vehicle service layer
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.models.vehicle import Vehicle, Position
from app.core.database import db
import logging

logger = logging.getLogger(__name__)

class VehicleService:
    """Service for vehicle operations"""
    
    def __init__(self):
        self.db = db
    
    def get_all_vehicles(self) -> List[Vehicle]:
        """Get all vehicles"""
        vehicles_data = self.db.get_vehicles()
        return [Vehicle(**v) for v in vehicles_data]
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Get vehicle by ID"""
        vehicle_data = self.db.get_vehicle(vehicle_id)
        if vehicle_data:
            return Vehicle(**vehicle_data)
        return None
    
    def update_position(self, vehicle_id: str, position_data: Dict[str, float]) -> Optional[Vehicle]:
        """Update vehicle position"""
        vehicle_data = self.db.get_vehicle(vehicle_id)
        if not vehicle_data:
            return None
        
        # Update position
        vehicle_data["position"] = position_data
        vehicle_data["last_updated"] = datetime.now().isoformat()
        
        updated = self.db.update_vehicle(vehicle_id, vehicle_data)
        if updated:
            return Vehicle(**updated)
        return None
    
    def update_status(self, vehicle_id: str, status: str) -> Optional[Vehicle]:
        """Update vehicle status"""
        vehicle_data = self.db.get_vehicle(vehicle_id)
        if not vehicle_data:
            return None
        
        vehicle_data["status"] = status
        vehicle_data["last_updated"] = datetime.now().isoformat()
        
        updated = self.db.update_vehicle(vehicle_id, vehicle_data)
        if updated:
            return Vehicle(**updated)
        return None
    
    def get_vehicle_route(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get vehicle's current route"""
        vehicle = self.get_vehicle(vehicle_id)
        if not vehicle or not vehicle.route_id:
            return None
        
        routes = self.db.get_routes()
        for route in routes:
            if route.get("id") == vehicle.route_id:
                return route
        return None
    
    def create_vehicle(self, vehicle_data: Dict[str, Any]) -> Vehicle:
        """Create a new vehicle"""
        if "id" not in vehicle_data:
            vehicle_data["id"] = f"V{str(uuid.uuid4())[:4].upper()}"
        
        vehicle = Vehicle(**vehicle_data)
        self.db.add_vehicle(vehicle.dict())
        return vehicle
    
    def calculate_eta(self, vehicle_id: str, destination: str) -> Optional[Dict[str, Any]]:
        """Calculate ETA for vehicle to destination"""
        vehicle = self.get_vehicle(vehicle_id)
        if not vehicle:
            return None
        
        # Get route service from app state
        # This is a placeholder - actual implementation uses RouteService
        return {
            "vehicle_id": vehicle_id,
            "destination": destination,
            "eta": datetime.now().isoformat(),
            "estimated_time_minutes": 45
        }