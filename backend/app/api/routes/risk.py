"""
Risk API endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from app.services.risk_service import RiskService
from app.decision.risk_engine import RiskEngine

router = APIRouter()

@router.get("/{segment_id}")
async def get_risk(segment_id: str, request: Request):
    """Get risk score for a segment"""
    engine: RiskEngine = request.app.state.risk_engine
    risk_score = engine.calculate_risk(segment_id)
    if risk_score is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    classification = engine.classify_risk(risk_score)
    explanation = engine.explain_risk(segment_id)
    
    return {
        "segment_id": segment_id,
        "risk_score": risk_score,
        "classification": classification,
        "explanation": explanation
    }

@router.post("/segment/{segment_id}/update")
async def update_risk(segment_id: str, risk_data: dict, request: Request):
    """Update risk for a segment"""
    engine: RiskEngine = request.app.state.risk_engine
    updated_score = engine.update_risk(segment_id, risk_data)
    if updated_score is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    return {
        "segment_id": segment_id,
        "risk_score": updated_score,
        "classification": engine.classify_risk(updated_score)
    }

@router.get("/{segment_id}/explain")
async def explain_risk(segment_id: str, request: Request):
    """Get explanation of risk calculation"""
    engine: RiskEngine = request.app.state.risk_engine
    explanation = engine.explain_risk(segment_id)
    if "error" in explanation:
        raise HTTPException(status_code=404, detail=explanation["error"])
    return explanation