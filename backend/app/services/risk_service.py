"""
Risk service layer
"""

from typing import Optional, Dict, Any
from app.decision.risk_engine import RiskEngine
from app.core.database import db
import logging

logger = logging.getLogger(__name__)

class RiskService:
    """Service for risk operations"""
    
    def __init__(self):
        self.risk_engine = RiskEngine()
        self.db = db
    
    def calculate_risk(self, segment_id: str) -> Optional[float]:
        """Calculate risk for a segment"""
        return self.risk_engine.calculate_risk(segment_id)
    
    def classify_risk(self, risk_score: float) -> str:
        """Classify risk score"""
        return self.risk_engine.classify_risk(risk_score)
    
    def explain_risk(self, segment_id: str) -> Dict[str, Any]:
        """Explain risk calculation"""
        return self.risk_engine.explain_risk(segment_id)
    
    def update_risk(self, segment_id: str, updates: Dict[str, Any]) -> Optional[float]:
        """Update risk for a segment"""
        return self.risk_engine.update_risk(segment_id, updates)
    
    def get_segment_risk(self, segment_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive risk information for a segment"""
        risk_score = self.calculate_risk(segment_id)
        if risk_score is None:
            return None
        
        return {
            "segment_id": segment_id,
            "risk_score": risk_score,
            "classification": self.classify_risk(risk_score),
            "explanation": self.explain_risk(segment_id)
        }