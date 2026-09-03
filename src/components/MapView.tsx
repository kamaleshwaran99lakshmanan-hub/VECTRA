import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface RouteCoordinate {
  lat: number;
  lng: number;
}

interface RouteSegment {
  id: string;
  coordinates: RouteCoordinate[];
  risk_score: number;
  blocked: boolean;
}

interface MapViewProps {
  routeSegments?: RouteSegment[];
}

function FitRoute({ points }: { points: [number, number][] }) {
  const map = useMap();

  useEffect(() => {
    if (points.length > 1) {
      map.fitBounds(points, {
        padding: [40, 40],
        maxZoom: 12,
        animate: true,
      });
    }
  }, [map, points]);

  return null;
}

function MapView({ routeSegments = [] }: MapViewProps) {
  const routePoints: [number, number][] = routeSegments.flatMap((segment) =>
  segment.coordinates.map(
    (point) => [point.lat, point.lng] as [number, number]
  )
);

  return (
    <MapContainer
      center={[26.2, 92.9]}
      zoom={7}
      scrollWheelZoom={true}
      className="vectra-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <FitRoute points={routePoints} />

      {routePoints.length > 1 && (
        <Polyline
          positions={routePoints}
          pathOptions={{
            color: "#1687d4",
            weight: 6,
            opacity: 0.9,
          }}
        />
      )}

      {routePoints.length > 0 && (
        <>
          <Marker position={routePoints[0]}>
            <Popup>Route Start</Popup>
          </Marker>

          <Marker position={routePoints[routePoints.length - 1]}>
            <Popup>Route Destination</Popup>
          </Marker>
        </>
      )}
    </MapContainer>
  );
}

export default MapView;