"""
Route optimization using NetworkX graph
"""

import networkx as nx
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.core.database import db
from app.models.route import RouteSegment
from app.decision.risk_engine import RiskEngine

logger = logging.getLogger(__name__)

class RouteOptimizer:
    """
    Route optimization engine using graph-based routing
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.risk_engine = RiskEngine()
        self._build_graph()
    
    def _build_graph(self):
        """Build graph from road data"""
        roads = db.get_roads()
        
        for road in roads:
            segment_id = road.get("id")
            from_node = road.get("from")
            to_node = road.get("to")
            distance = road.get("distance", 0)
            travel_time = road.get("travel_time", 0)
            risk_score = road.get("risk_score", 0)
            blocked = road.get("blocked", False)
            
            # Add nodes if not exist
            if from_node:
                self.graph.add_node(from_node, label=from_node)
            if to_node:
                self.graph.add_node(to_node, label=to_node)
            
            # Add edge with attributes
            if from_node and to_node:
                self.graph.add_edge(
                    from_node, to_node,
                    segment_id=segment_id,
                    distance=distance,
                    travel_time=travel_time,
                    risk_score=risk_score,
                    blocked=blocked,
                    road_data=road
                )
        
        logger.info(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def find_shortest_route(self, origin: str, destination: str, 
                           avoid_high_risk: bool = True) -> Optional[Dict[str, Any]]:
        """
        Find shortest route considering risk
        
        Args:
            origin: Starting node
            destination: Ending node
            avoid_high_risk: Whether to avoid high risk segments
            
        Returns:
            Dict with route details or None
        """
        if origin not in self.graph or destination not in self.graph:
            logger.error(f"Node not found: {origin} -> {destination}")
            return None
        
        # Update graph with latest risk data
        self._update_graph_risks()
        
        # Function to calculate edge weight (cost)
        def get_edge_weight(u, v, edge_data):
            # Check if blocked
            if edge_data.get('blocked', False):
                return float('inf')
            
            # Base cost is travel time
            base_cost = edge_data.get('travel_time', 100)
            
            if avoid_high_risk:
                # Add risk penalty
                risk_score = edge_data.get('risk_score', 0)
                # Risk penalty: +50% for HIGH, +100% for CRITICAL
                if risk_score > 80:  # CRITICAL
                    risk_penalty = base_cost * 1.0
                elif risk_score > 60:  # HIGH
                    risk_penalty = base_cost * 0.5
                elif risk_score > 30:  # MEDIUM
                    risk_penalty = base_cost * 0.2
                else:  # LOW
                    risk_penalty = 0
                return base_cost + risk_penalty
            
            return base_cost
        
        try:
            # Find shortest path
            path = nx.shortest_path(
                self.graph,
                source=origin,
                target=destination,
                weight=lambda u, v, d: get_edge_weight(u, v, d)
            )
            
            # Convert path to route segments
            route_segments = []
            total_distance = 0
            total_time = 0
            total_risk = 0
            
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                edge_data = self.graph.get_edge_data(u, v, default={})
                
                if edge_data:
                    segment_id = edge_data.get('segment_id')
                    road_data = edge_data.get('road_data', {})
                    
                    segment = {
    'id': segment_id,
    'from_node': u,
    'to_node': v,
    'distance': road_data.get('distance', 0),
    'travel_time': road_data.get('travel_time', 0),
    'risk_score': road_data.get('risk_score', 0),
    'road_status': road_data.get('status', 'unknown'),
    'blocked': road_data.get('blocked', False),
    'coordinates': road_data.get('coordinates', [])
}
                    route_segments.append(segment)
                    total_distance += segment['distance']
                    total_time += segment['travel_time']
                    total_risk += segment['risk_score']
            
            if route_segments:
                avg_risk = total_risk / len(route_segments)
                return {
                    'segments': route_segments,
                    'total_distance': total_distance,
                    'total_time': total_time,
                    'total_risk': avg_risk,
                    'nodes': path
                }
            
            return None
            
        except nx.NetworkXNoPath:
            logger.error(f"No path found from {origin} to {destination}")
            return None
        except Exception as e:
            logger.error(f"Route calculation error: {str(e)}")
            return None
    
    def _update_graph_risks(self):
        """Update graph with latest risk scores"""
        roads = db.get_roads()
        
        for road in roads:
            segment_id = road.get('id')
            from_node = road.get('from')
            to_node = road.get('to')
            
            if from_node and to_node and segment_id:
                # Get updated risk
                risk_score = self.risk_engine.calculate_risk(segment_id)
                if risk_score is not None:
                    road['risk_score'] = risk_score
                    road['risk_level'] = self.risk_engine.classify_risk(risk_score)
                    
                    # Block if CRITICAL
                    if risk_score >= 90:
                        road['blocked'] = True
                    
                    # Update edge data
                    if self.graph.has_edge(from_node, to_node):
                        self.graph.edges[from_node, to_node]['risk_score'] = risk_score
                        self.graph.edges[from_node, to_node]['blocked'] = road.get('blocked', False)
                        self.graph.edges[from_node, to_node]['road_data'] = road
    
    def find_alternative_route(self, origin: str, destination: str,
                              exclude_segments: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find alternative route avoiding specified segments
        
        Args:
            origin: Starting node
            destination: Ending node
            exclude_segments: Segments to exclude
            
        Returns:
            Dict with route details or None
        """
        if exclude_segments is None:
            exclude_segments = []
        
        # Temporarily block excluded segments
        for segment_id in exclude_segments:
            road = db.get_road(segment_id)
            if road:
                self._temporarily_block_segment(segment_id)
        
        # Find route
        route = self.find_shortest_route(origin, destination)
        
        # Unblock excluded segments
        for segment_id in exclude_segments:
            self._unblock_segment(segment_id)
        
        return route
    
    def _temporarily_block_segment(self, segment_id: str):
        """Temporarily block a segment in the graph"""
        roads = db.get_roads()
        for road in roads:
            if road.get('id') == segment_id:
                from_node = road.get('from')
                to_node = road.get('to')
                if from_node and to_node and self.graph.has_edge(from_node, to_node):
                    self.graph.edges[from_node, to_node]['blocked'] = True
                break
    
    def _unblock_segment(self, segment_id: str):
        """Unblock a segment in the graph"""
        roads = db.get_roads()
        for road in roads:
            if road.get('id') == segment_id:
                from_node = road.get('from')
                to_node = road.get('to')
                if from_node and to_node and self.graph.has_edge(from_node, to_node):
                    self.graph.edges[from_node, to_node]['blocked'] = False
                break
    
    def refresh_graph(self):
        """Refresh the graph with latest data"""
        self.graph.clear()
        self._build_graph()
        self._update_graph_risks()