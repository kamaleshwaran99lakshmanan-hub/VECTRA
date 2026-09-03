"""
Decision Engine for route recommendations and alerts
"""

import logging
from typing import Dict, Any, List, Optional
from app.models.incident import Incident
from app.models.route import Route
from app.decision.risk_engine import RiskEngine
from app.services.vehicle_service import VehicleService
from app.services.route_service import RouteService

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Decision engine for evaluating situations and making recommendations
    """
    
    def __init__(self):
        self.risk_engine = RiskEngine()
        self.vehicle_service = VehicleService()
        self.route_service = RouteService()
    
    def evaluate_incident(self, incident: Incident) -> Dict[str, Any]:
        """
        Evaluate an incident and determine appropriate action
        
        Returns:
            Decision with recommendation
        """
        decision = {
            "incident_id": incident.id,
            "severity": incident.severity,
            "requires_action": False,
            "recommendation": None,
            "action": None
        }
        
        # Check severity
        if incident.severity == "CRITICAL":
            decision["requires_action"] = True
            decision["recommendation"] = "Route change required"
            decision["action"] = "route_change"
            
            # Check affected vehicles
            vehicles = self.vehicle_service.get_all_vehicles()
            affected_vehicles = []
            
            for vehicle in vehicles:
                if vehicle.route_id:
                    route = self.route_service.get_route(vehicle.route_id)
                    if route and any(seg.id in incident.affected_segments for seg in route.segments):
                        affected_vehicles.append(vehicle.id)
            
            decision["affected_vehicles"] = affected_vehicles
            
        elif incident.severity == "HIGH":
            decision["requires_action"] = True
            decision["recommendation"] = "Monitor situation"
            decision["action"] = "monitor"
            
        elif incident.severity == "MEDIUM":
            decision["requires_action"] = False
            decision["recommendation"] = "Inform operator"
            decision["action"] = "inform"
            
        else:
            decision["requires_action"] = False
            decision["recommendation"] = "Log incident"
            decision["action"] = "log"
        
        return decision
    
    def recommend_route_change(self, vehicle_id: str, incident: Incident) -> Optional[Dict[str, Any]]:
        """
        Recommend a route change based on an incident
        """
        vehicle = self.vehicle_service.get_vehicle(vehicle_id)
        if not vehicle:
            return None
        
        # Calculate alternative route
        alternative = self.route_service.calculate_alternative_route(
            vehicle_id, 
            vehicle.destination,
            incident.affected_segments
        )
        
        if alternative:
            return {
                "vehicle_id": vehicle_id,
                "incident_id": incident.id,
                "current_route": vehicle.route_id,
                "recommended_route": alternative,
                "reason": f"Incident {incident.type} affecting segments: {', '.join(incident.affected_segments)}",
                "eta_change": self._calculate_eta_change(vehicle_id, alternative)
            }
        
        return None
    
    def _calculate_eta_change(self, vehicle_id: str, new_route: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate ETA change between current and new route"""
        vehicle = self.vehicle_service.get_vehicle(vehicle_id)
        if not vehicle:
            return {}
        
        current_route = self.route_service.get_vehicle_route(vehicle_id)
        
        if current_route:
            current_time = current_route.get("total_time", 0)
            new_time = new_route.get("total_time", 0)
            
            return {
                "current_eta_minutes": current_time,
                "new_eta_minutes": new_time,
                "difference_minutes": new_time - current_time,
                "percentage_change": ((new_time - current_time) / current_time * 100) if current_time > 0 else 0
            }
        
        return {}