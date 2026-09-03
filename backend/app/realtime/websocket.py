"""
WebSocket connection manager for real-time updates
"""

from fastapi import WebSocket
from typing import Set, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_data[websocket] = {
            "connected_at": websocket.client,
            "messages_received": 0,
            "messages_sent": 0
        }
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")
    
    async def send_message(self, websocket: WebSocket, message: str):
        """Send a message to a specific connection"""
        try:
            await websocket.send_text(message)
            if websocket in self.connection_data:
                self.connection_data[websocket]["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            self.disconnect(websocket)
    
    async def send_json(self, websocket: WebSocket, data: Dict[str, Any]):
        """Send JSON data to a specific connection"""
        try:
            await websocket.send_json(data)
            if websocket in self.connection_data:
                self.connection_data[websocket]["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Error sending JSON: {str(e)}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connections"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                if connection in self.connection_data:
                    self.connection_data[connection]["messages_sent"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting: {str(e)}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: Dict[str, Any]):
        """Broadcast JSON data to all connections"""
        message = json.dumps(data)
        await self.broadcast(message)
    
    async def close_all(self):
        """Close all connections"""
        for connection in list(self.active_connections):
            try:
                await connection.close()
            except Exception:
                pass
        self.active_connections.clear()
        self.connection_data.clear()
        logger.info("All WebSocket connections closed")
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            "active_connections": self.get_connection_count(),
            "connections": [
                {
                    "client": data.get("connected_at"),
                    "messages_received": data.get("messages_received", 0),
                    "messages_sent": data.get("messages_sent", 0)
                }
                for data in self.connection_data.values()
            ]
        }