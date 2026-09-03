"""
Incident service layer
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.models.incident import Incident, IncidentType, IncidentSeverity
from app.core.database import db
import logging

logger = logging.getLogger(__name__)

class IncidentService:
    """Service for incident operations"""
    
    def __init__(self):
        self.db = db
    
    def get_all_incidents(self) -> List[Incident]:
        """Get all incidents"""
        incidents_data = self.db.get_incidents()
        return [Incident(**i) for i in incidents_data]
    
    def get_active_incidents(self) -> List[Incident]:
        """Get active incidents"""
        incidents_data = self.db.get_active_incidents()
        return [Incident(**i) for i in incidents_data]
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID"""
        incidents = self.get_all_incidents()
        for incident in incidents:
            if incident.id == incident_id:
                return incident
        return None
    
    def create_incident(self, incident_data: Dict[str, Any]) -> Incident:
        """Create a new incident"""
        if "id" not in incident_data:
            incident_data["id"] = f"INC{str(uuid.uuid4())[:4].upper()}"
        
        incident = Incident(**incident_data)
        self.db.add_incident(incident.dict())
        logger.info(f"Created incident: {incident.id} - {incident.type}")
        return incident
    
    def resolve_incident(self, incident_id: str) -> Optional[Incident]:
        """Resolve an incident"""
        resolved_data = self.db.resolve_incident(incident_id)
        if resolved_data:
            logger.info(f"Resolved incident: {incident_id}")
            return Incident(**resolved_data)
        return None
    
    def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> Optional[Incident]:
        """Update an incident"""
        incident = self.get_incident(incident_id)
        if not incident:
            return None
        
        # Update incident
        incident_dict = incident.dict()
        incident_dict.update(updates)
        incident_dict["timestamp"] = datetime.now().isoformat()
        
        # Save back to database
        incidents = self.db.get_incidents()
        for i, inc in enumerate(incidents):
            if inc.get("id") == incident_id:
                incidents[i] = incident_dict
                break
        
        self.db.save_incidents(incidents)
        return Incident(**incident_dict)
    
    def get_incidents_by_segment(self, segment_id: str) -> List[Incident]:
        """Get incidents affecting a specific segment"""
        incidents = self.get_all_incidents()
        return [inc for inc in incidents if segment_id in inc.affected_segments]