import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

function MapView() {
  return (
    <MapContainer
      center={[26.2, 92.9]}
      zoom={6}
      scrollWheelZoom={true}
      className="vectra-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    </MapContainer>
  );
}

export default MapView;