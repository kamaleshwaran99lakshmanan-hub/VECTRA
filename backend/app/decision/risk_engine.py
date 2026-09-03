"""
Risk Calculation Engine
Weighted scoring model - replaceable with ML model later
"""

import logging
from typing import Dict, Any, List, Optional
from app.models.incident import IncidentSeverity
from app.core.database import db
from app.models.incident import IncidentType

logger = logging.getLogger(__name__)

class RiskEngine:
    """
    Weighted scoring model for risk calculation
    Architecture allows replacement with XGBoost/LightGBM
    """
    
    # Weight configuration - these can be tuned
    WEIGHTS = {
        "weather": 0.25,
        "road_condition": 0.30,
        "incident": 0.30,
        "historical": 0.15
    }
    
    # Weather risk mapping
    WEATHER_RISK = {
        "clear": 0,
        "cloudy": 10,
        "light_rain": 25,
        "moderate_rain": 50,
        "heavy_rain": 75,
        "storm": 90,
        "flood": 100
    }
    
    # Road condition risk mapping
    ROAD_RISK = {
        "excellent": 0,
        "good": 10,
        "fair": 25,
        "poor": 50,
        "degraded": 75,
        "hazardous": 100
    }
    
    # Incident risk base values
    INCIDENT_RISK = {
        IncidentType.ROAD_BLOCKAGE.value: 85,
        IncidentType.ACCIDENT.value: 90,
        IncidentType.HEAVY_RAIN.value: 70,
        IncidentType.ROAD_DEGRADATION.value: 65,
        IncidentType.WEATHER.value: 60,
        IncidentType.FLOODING.value: 95,
        IncidentType.LANDSLIDE.value: 90,
        IncidentType.CONSTRUCTION.value: 50
    }
    
    def __init__(self):
        self.cache: Dict[str, float] = {}
    
    def calculate_risk(self, segment_id: str) -> Optional[float]:
        """
        Calculate comprehensive risk for a road segment
        
        Returns:
            Risk score 0-100 or None if segment not found
        """
        road = db.get_road(segment_id)
        if not road:
            logger.warning(f"Segment {segment_id} not found")
            return None
        
        # Calculate individual risk components
        weather_risk = self._calculate_weather_risk(segment_id)
        road_condition_risk = self._calculate_road_condition_risk(road)
        incident_risk = self._calculate_incident_risk(segment_id)
        historical_risk = self._calculate_historical_risk(segment_id)
        
        # Weighted sum
        total_risk = (
            weather_risk * self.WEIGHTS["weather"] +
            road_condition_risk * self.WEIGHTS["road_condition"] +
            incident_risk * self.WEIGHTS["incident"] +
            historical_risk * self.WEIGHTS["historical"]
        )
        
        # Normalize to 0-100
        total_risk = max(0, min(100, total_risk))
        
        # Cache result
        self.cache[segment_id] = total_risk
        
        logger.debug(f"Risk for {segment_id}: {total_risk:.2f}")
        return total_risk
    
    def _calculate_weather_risk(self, segment_id: str) -> float:
        """Calculate weather risk component"""
        weather_data = db.get_weather()
        if weather_data:
            total = 0
            count = 0
            for w in weather_data:
                condition = w.get("condition", "clear").lower().replace(" ", "_")
                if condition in self.WEATHER_RISK:
                    total += self.WEATHER_RISK[condition]
                    count += 1
            if count > 0:
                return total / count
        return 0
    
    def _calculate_road_condition_risk(self, road: Dict[str, Any]) -> float:
        """Calculate road condition risk component"""
        condition = road.get("condition", "good").lower()
        if condition in self.ROAD_RISK:
            return self.ROAD_RISK[condition]
        return 0
    
    def _calculate_incident_risk(self, segment_id: str) -> float:
        """Calculate incident risk component"""
        incidents = db.get_incidents()
        max_risk = 0
        
        for incident in incidents:
            if not incident.get("active", False):
                continue
            
            affected = incident.get("affected_segments", [])
            if segment_id in affected:
                risk = incident.get("risk_score", 0)
                if risk == 0:
                    incident_type = incident.get("type", "unknown")
                    risk = self.INCIDENT_RISK.get(incident_type, 50)
                
                if risk > max_risk:
                    max_risk = risk
        
        return max_risk
    
    def _calculate_historical_risk(self, segment_id: str) -> float:
        """Calculate historical risk component"""
        road = db.get_road(segment_id)
        if road:
            historical_data = road.get("historical_incidents", 0)
            return min(100, historical_data * 10)
        return 0
    
    def classify_risk(self, risk_score: float) -> str:
        """
        Classify risk score into severity levels
        
        Args:
            risk_score: Score 0-100
            
        Returns:
            Severity level string
        """
        if risk_score <= 30:
            return "LOW"
        elif risk_score <= 60:
            return "MEDIUM"
        elif risk_score <= 80:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def update_risk(self, segment_id: str, updates: Dict[str, Any]) -> Optional[float]:
        """
        Update risk calculation based on changed conditions
        
        Args:
            segment_id: Road segment identifier
            updates: Dictionary of updated values
            
        Returns:
            Updated risk score
        """
        # Update road data
        road_updates = {}
        if "condition" in updates:
            road_updates["condition"] = updates["condition"]
        if "blocked" in updates:
            road_updates["blocked"] = updates["blocked"]
        
        if road_updates:
            db.update_road(segment_id, road_updates)
        
        # Recalculate risk
        risk_score = self.calculate_risk(segment_id)
        if risk_score is not None:
            db.update_road(segment_id, {
                "risk_score": risk_score,
                "risk_level": self.classify_risk(risk_score)
            })
        
        return risk_score
    
    def explain_risk(self, segment_id: str) -> Dict[str, Any]:
        """Get explanation of risk calculation"""
        risk_score = self.calculate_risk(segment_id)
        if risk_score is None:
            return {"error": "Segment not found"}
        
        road = db.get_road(segment_id)
        if not road:
            return {"error": "Road data not available"}
        
        # Calculate individual components
        weather_risk = self._calculate_weather_risk(segment_id)
        road_condition_risk = self._calculate_road_condition_risk(road)
        incident_risk = self._calculate_incident_risk(segment_id)
        historical_risk = self._calculate_historical_risk(segment_id)
        
        return {
            "segment_id": segment_id,
            "risk_score": risk_score,
            "classification": self.classify_risk(risk_score),
            "components": {
                "weather": {
                    "value": weather_risk,
                    "weight": self.WEIGHTS["weather"],
                    "weighted_value": weather_risk * self.WEIGHTS["weather"]
                },
                "road_condition": {
                    "value": road_condition_risk,
                    "weight": self.WEIGHTS["road_condition"],
                    "weighted_value": road_condition_risk * self.WEIGHTS["road_condition"]
                },
                "incident": {
                    "value": incident_risk,
                    "weight": self.WEIGHTS["incident"],
                    "weighted_value": incident_risk * self.WEIGHTS["incident"]
                },
                "historical": {
                    "value": historical_risk,
                    "weight": self.WEIGHTS["historical"],
                    "weighted_value": historical_risk * self.WEIGHTS["historical"]
                }
            },
            "formula": "weather * 0.25 + road_condition * 0.30 + incident * 0.30 + historical * 0.15",
            "road_details": {
                "id": road.get("id"),
                "condition": road.get("condition", "unknown"),
                "status": road.get("status", "unknown"),
                "blocked": road.get("blocked", False)
            }
        }