"""
Database abstraction layer for NER-LOGIX
Supports both JSON (development) and PostgreSQL (production)
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class JSONRepository:
    """JSON-based repository for development and testing"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data"
        self.data_dir = data_dir
        self._cache: Dict[str, Any] = {}
        self._ensure_data_directory()
        self._load_or_create_default_data()
        self._initialize_sample_data()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file with caching"""
        if filename not in self._cache:
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self._cache[filename] = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"Error loading {filename}: {e}")
                    self._cache[filename] = {}
            else:
                logger.warning(f"Data file not found: {filename}")
                self._cache[filename] = {}
        return self._cache[filename]
    
    def _save_json(self, filename: str, data: Dict[str, Any]):
        """Save data to JSON file"""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self._cache[filename] = data
            logger.debug(f"Saved data to {filename}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
    
    def _load_or_create_default_data(self):
        """Load or create default data files"""
        default_files = [
            "vehicles.json",
            "roads.json",
            "deliveries.json",
            "weather.json",
            "incidents.json",
            "routes.json"
        ]
        
        for filename in default_files:
            file_path = self.data_dir / filename
            if not file_path.exists():
                # Create default empty file
                self._save_json(filename, {})
                logger.info(f"Created default data file: {filename}")
    
    def _initialize_sample_data(self):
        """Initialize sample data if empty"""
        # Initialize vehicles
        if not self.get_vehicles():
            vehicles = [
                {
                    "id": "V001",
                    "name": "Truck-01",
                    "position": {"lat": 26.1445, "lng": 91.7362},
                    "speed": 0,
                    "heading": 45,
                    "status": "active",
                    "route_id": "R001",
                    "current_segment": "A-B",
                    "destination": "E",
                    "fuel_level": 85,
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "id": "V002",
                    "name": "Truck-02",
                    "position": {"lat": 26.1200, "lng": 91.7000},
                    "speed": 0,
                    "heading": 90,
                    "status": "idle",
                    "route_id": None,
                    "current_segment": None,
                    "destination": None,
                    "fuel_level": 92,
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "id": "V003",
                    "name": "Truck-03",
                    "position": {"lat": 26.1600, "lng": 91.7800},
                    "speed": 0,
                    "heading": 180,
                    "status": "idle",
                    "route_id": None,
                    "current_segment": None,
                    "destination": None,
                    "fuel_level": 78,
                    "last_updated": datetime.now().isoformat()
                }
            ]
            self.save_vehicles(vehicles)
        
        # Initialize roads
        if not self.get_roads():
            roads = [
                {
                    "id": "A-B",
                    "from": "A",
                    "to": "B",
                    "distance": 15.5,
                    "travel_time": 18.6,
                    "condition": "good",
                    "status": "normal",
                    "blocked": False,
                    "risk_score": 15,
                    "risk_level": "LOW",
                    "speed_limit": 60,
                    "historical_incidents": 0,
                    "coordinates": [
                        {"lat": 26.1445, "lng": 91.7362},
                        {"lat": 26.1480, "lng": 91.7450},
                        {"lat": 26.1520, "lng": 91.7500}
                    ]
                },
                {
                    "id": "B-C",
                    "from": "B",
                    "to": "C",
                    "distance": 12.8,
                    "travel_time": 15.4,
                    "condition": "good",
                    "status": "normal",
                    "blocked": False,
                    "risk_score": 20,
                    "risk_level": "LOW",
                    "speed_limit": 60,
                    "historical_incidents": 1,
                    "coordinates": [
                        {"lat": 26.1520, "lng": 91.7500},
                        {"lat": 26.1550, "lng": 91.7580},
                        {"lat": 26.1580, "lng": 91.7650}
                    ]
                },
                {
                    "id": "C-D",
                    "from": "C",
                    "to": "D",
                    "distance": 18.2,
                    "travel_time": 21.8,
                    "condition": "fair",
                    "status": "normal",
                    "blocked": False,
                    "risk_score": 35,
                    "risk_level": "MEDIUM",
                    "speed_limit": 50,
                    "historical_incidents": 2,
                    "coordinates": [
                        {"lat": 26.1580, "lng": 91.7650},
                        {"lat": 26.1620, "lng": 91.7750},
                        {"lat": 26.1660, "lng": 91.7850}
                    ]
                },
                {
                    "id": "D-E",
                    "from": "D",
                    "to": "E",
                    "distance": 10.5,
                    "travel_time": 12.6,
                    "condition": "good",
                    "status": "normal",
                    "blocked": False,
                    "risk_score": 10,
                    "risk_level": "LOW",
                    "speed_limit": 60,
                    "historical_incidents": 0,
                    "coordinates": [
                        {"lat": 26.1660, "lng": 91.7850},
                        {"lat": 26.1700, "lng": 91.7950},
                        {"lat": 26.1730, "lng": 91.8000}
                    ]
                },
                {
                    "id": "B-Y",
                    "from": "B",
                    "to": "Y",
                    "distance": 20.5,
                    "travel_time": 24.6,
                    "condition": "fair",
                    "status": "normal",
                    "blocked": False,
                    "risk_score": 40,
                    "risk_level": "MEDIUM",
                    "speed_limit": 50,
                    "historical_incidents": 3,
                    "coordinates": [
                        {"lat": 26.1520, "lng": 91.7500},
                        {"lat": 26.1450, "lng": 91.7600},
                        {"lat": 26.1400, "lng": 91.7700}
                    ]
                },
                {
                    "id": "Y-Z",
                    "from": "Y",
                    "to": "Z",
                    "distance": 14.2,
                    "travel_time": 17.0,
                    "condition": "fair",
                    "status": "normal",
                    "blocked": False,
                    "risk_score": 45,
                    "risk_level": "MEDIUM",
                    "speed_limit": 50,
                    "historical_incidents": 2,
                    "coordinates": [
                        {"lat": 26.1400, "lng": 91.7700},
                        {"lat": 26.1450, "lng": 91.7850},
                        {"lat": 26.1500, "lng": 91.7950}
                    ]
                },
                {
                    "id": "Z-D",
                    "from": "Z",
                    "to": "D",
                    "distance": 8.5,
                    "travel_time": 10.2,
                    "condition": "good",
                    "status": "normal",
                    "blocked": False,
                    "risk_score": 25,
                    "risk_level": "LOW",
                    "speed_limit": 60,
                    "historical_incidents": 0,
                    "coordinates": [
                        {"lat": 26.1500, "lng": 91.7950},
                        {"lat": 26.1580, "lng": 91.7900},
                        {"lat": 26.1660, "lng": 91.7850}
                    ]
                }
            ]
            self.save_roads(roads)
        
        # Initialize weather
        if not self.get_weather():
            weather = [
                {
                    "id": "W001",
                    "area": "Route A-E",
                    "condition": "clear",
                    "temperature": 28,
                    "humidity": 65,
                    "wind_speed": 10,
                    "visibility": 10,
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": "W002",
                    "area": "Alternative Route",
                    "condition": "cloudy",
                    "temperature": 26,
                    "humidity": 70,
                    "wind_speed": 15,
                    "visibility": 8,
                    "timestamp": datetime.now().isoformat()
                }
            ]
            self.update_weather(weather)
        
        # Initialize deliveries
        if not self.get_deliveries():
            deliveries = [
                {
                    "id": "D001",
                    "vehicle_id": "V001",
                    "origin": "A",
                    "destination": "E",
                    "priority": "HIGH",
                    "status": "in_progress",
                    "cargo_type": "Medical Supplies",
                    "weight": 2500,
                    "created_at": datetime.now().isoformat(),
                    "estimated_delivery": "2026-09-02T18:00:00"
                },
                {
                    "id": "D002",
                    "vehicle_id": "V002",
                    "origin": "A",
                    "destination": "C",
                    "priority": "MEDIUM",
                    "status": "pending",
                    "cargo_type": "Food Items",
                    "weight": 3000,
                    "created_at": datetime.now().isoformat(),
                    "estimated_delivery": "2026-09-02T20:00:00"
                }
            ]
            self._save_json("deliveries.json", {"deliveries": deliveries})
    
    # Vehicle methods
    def get_vehicles(self) -> List[Dict[str, Any]]:
        """Get all vehicles"""
        data = self._load_json("vehicles.json")
        return data.get("vehicles", [])
    
    def save_vehicles(self, vehicles: List[Dict[str, Any]]):
        """Save vehicles"""
        self._save_json("vehicles.json", {"vehicles": vehicles, "updated_at": datetime.now().isoformat()})
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get vehicle by ID"""
        vehicles = self.get_vehicles()
        for vehicle in vehicles:
            if vehicle.get("id") == vehicle_id:
                return vehicle
        return None
    
    def update_vehicle(self, vehicle_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update vehicle"""
        vehicles = self.get_vehicles()
        for i, vehicle in enumerate(vehicles):
            if vehicle.get("id") == vehicle_id:
                vehicles[i].update(updates)
                vehicles[i]["last_updated"] = datetime.now().isoformat()
                self.save_vehicles(vehicles)
                return vehicles[i]
        return None
    
    # Road methods
    def get_roads(self) -> List[Dict[str, Any]]:
        """Get all roads"""
        data = self._load_json("roads.json")
        return data.get("roads", [])
    
    def save_roads(self, roads: List[Dict[str, Any]]):
        """Save roads"""
        self._save_json("roads.json", {"roads": roads, "updated_at": datetime.now().isoformat()})
    
    def get_road(self, road_id: str) -> Optional[Dict[str, Any]]:
        """Get road by ID"""
        roads = self.get_roads()
        for road in roads:
            if road.get("id") == road_id:
                return road
        return None
    
    def update_road(self, road_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update road"""
        roads = self.get_roads()
        for i, road in enumerate(roads):
            if road.get("id") == road_id:
                roads[i].update(updates)
                self.save_roads(roads)
                return roads[i]
        return None
    
    # Incident methods
    def get_incidents(self) -> List[Dict[str, Any]]:
        """Get all incidents"""
        data = self._load_json("incidents.json")
        return data.get("incidents", [])
    
    def save_incidents(self, incidents: List[Dict[str, Any]]):
        """Save incidents"""
        self._save_json("incidents.json", {"incidents": incidents, "updated_at": datetime.now().isoformat()})
    
    def add_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Add new incident"""
        incidents = self.get_incidents()
        incidents.append(incident)
        self.save_incidents(incidents)
        return incident
    
    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """Get active incidents"""
        incidents = self.get_incidents()
        return [i for i in incidents if i.get("active", False)]
    
    def resolve_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Resolve an incident"""
        incidents = self.get_incidents()
        for i, incident in enumerate(incidents):
            if incident.get("id") == incident_id:
                incidents[i]["active"] = False
                incidents[i]["resolved_at"] = datetime.now().isoformat()
                self.save_incidents(incidents)
                return incidents[i]
        return None
    
    # Delivery methods
    def get_deliveries(self) -> List[Dict[str, Any]]:
        """Get all deliveries"""
        data = self._load_json("deliveries.json")
        return data.get("deliveries", [])
    
    # Weather methods
    def get_weather(self) -> List[Dict[str, Any]]:
        """Get weather data"""
        data = self._load_json("weather.json")
        return data.get("weather", [])
    
    def update_weather(self, weather_updates: List[Dict[str, Any]]):
        """Update weather data"""
        self._save_json("weather.json", {"weather": weather_updates, "updated_at": datetime.now().isoformat()})
    
    # Route methods
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all routes"""
        data = self._load_json("routes.json")
        return data.get("routes", [])
    
    def save_routes(self, routes: List[Dict[str, Any]]):
        """Save routes"""
        self._save_json("routes.json", {"routes": routes, "updated_at": datetime.now().isoformat()})
    
    def add_route(self, route: Dict[str, Any]) -> Dict[str, Any]:
        """Add new route"""
        routes = self.get_routes()
        routes.append(route)
        self.save_routes(routes)
        return route
    
    def get_route(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Get route by ID"""
        routes = self.get_routes()
        for route in routes:
            if route.get("id") == route_id:
                return route
        return None
    
    def update_route(self, route_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update route"""
        routes = self.get_routes()
        for i, route in enumerate(routes):
            if route.get("id") == route_id:
                routes[i].update(updates)
                self.save_routes(routes)
                return routes[i]
        return None

# Singleton instance
db = JSONRepository()