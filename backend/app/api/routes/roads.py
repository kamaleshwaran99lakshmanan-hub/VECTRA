"""Road network API endpoints for the operations dashboard."""

from fastapi import APIRouter, Request
from app.core.database import db

router = APIRouter()

@router.get("/")
async def get_roads(request: Request):
    """Return the demo road network including display coordinates."""
    return db.get_roads()
