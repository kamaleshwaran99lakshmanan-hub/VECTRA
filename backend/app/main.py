"""
NER-LOGIX Main Application Entry Point
AI-Powered Predictive Logistics and Emergency Routing System
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
import logging

from app.core.config import settings
from app.api.routes import vehicles, incidents, risk, routes, simulation, roads
from app.realtime.websocket import ConnectionManager
from app.services.vehicle_service import VehicleService
from app.services.incident_service import IncidentService
from app.services.route_service import RouteService
from app.decision.risk_engine import RiskEngine
from app.routing.route_optimizer import RouteOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("=" * 60)
    logger.info("Starting NER-LOGIX API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info("=" * 60)
    
    # Initialize services
    app.state.manager = ConnectionManager()
    app.state.vehicle_service = VehicleService()
    app.state.incident_service = IncidentService()
    app.state.route_service = RouteService()
    app.state.risk_engine = RiskEngine()
    app.state.route_optimizer = RouteOptimizer()
    
    # Simulation state
    app.state.simulation_running = False
    app.state.simulation_task = None
    app.state.active_vehicles = {}
    app.state.pending_alerts = []
    app.state.approval_required = False
    app.state.pending_route = None
    app.state.current_incident = None
    
    logger.info("All services initialized successfully")
    logger.info("NER-LOGIX API started successfully")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down NER-LOGIX API...")
    if app.state.simulation_task:
        app.state.simulation_task.cancel()
    await app.state.manager.close_all()
    logger.info("NER-LOGIX API shut down")

app = FastAPI(
    title="NER-LOGIX API",
    description="AI-Powered Predictive Logistics and Emergency Routing System for Northeast India",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(routes.router, prefix="/api/routes", tags=["routes"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(roads.router, prefix="/api/roads", tags=["roads"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "operational",
        "service": "NER-LOGIX API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "version": settings.APP_VERSION
    }

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    manager: ConnectionManager = app.state.manager
    await manager.connect(websocket)
    
    try:
        logger.info(f"WebSocket client connected")
        
        # Send initial data
        initial_data = {
            "type": "connection_established",
            "message": "Connected to NER-LOGIX real-time stream",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket.send_json(initial_data)
        
        # Send current system state
        current_state = {
            "type": "system_state",
            "simulation_running": app.state.simulation_running,
            "active_vehicles": len(app.state.active_vehicles),
            "pending_alerts": len(app.state.pending_alerts),
            "approval_required": app.state.approval_required,
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket.send_json(current_state)
        
        while True:
            # Receive and process messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "get_state":
                    await websocket.send_json(current_state)
                elif message.get("type") == "approve_route":
                    # Handle route approval
                    await app.state.route_service.approve_route(message.get("route_id"))
                    app.state.approval_required = False
                    await manager.broadcast(json.dumps({
                        "type": "route_approved",
                        "route_id": message.get("route_id"),
                        "message": "Route approved by operator"
                    }))
                elif message.get("type") == "reject_route":
                    # Handle route rejection
                    await app.state.route_service.reject_route(message.get("route_id"))
                    app.state.approval_required = False
                    await manager.broadcast(json.dumps({
                        "type": "route_rejected",
                        "route_id": message.get("route_id"),
                        "message": "Route rejected by operator"
                    }))
                else:
                    # Broadcast to all clients
                    await manager.broadcast(data)
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )