import { useEffect } from "react";
import L from "leaflet";
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from "react-leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import type { RouteInfo } from "../types";
import { Navigation, Clock } from "lucide-react";

delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

interface Props {
  route: RouteInfo;
  height?: number;
}

function FitToWaypoints({ positions }: { positions: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length === 0) return;
    map.fitBounds(L.latLngBounds(positions), { padding: [24, 24] });
  }, [map, positions]);
  return null;
}

export function RouteMap({ route, height = 320 }: Props) {
  const waypointPositions: [number, number][] = route.waypoints.map((w) => [w.lat, w.lng]);
  const linePositions = route.geometry ?? waypointPositions;

  if (waypointPositions.length === 0) {
    return <p className="muted">No route available yet.</p>;
  }

  return (
    <div style={{ position: 'relative', marginTop: '0.75rem' }}>
      <div style={{ borderRadius: '0.75rem', overflow: 'hidden', border: '1px solid #e2e8f0', boxShadow: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)', zIndex: 1, position: 'relative' }}>
        <MapContainer center={waypointPositions[0]} zoom={12} style={{ height, zIndex: 1 }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Polyline
            positions={linePositions}
            pathOptions={{
              color: "#4f46e5", // Indigo
              weight: 4,
              dashArray: route.routed ? undefined : "6 8",
            }}
          />
          {route.waypoints.map((w, i) => (
            <Marker key={i} position={[w.lat, w.lng]}>
              <Popup>{w.label}</Popup>
            </Marker>
          ))}
          <FitToWaypoints positions={waypointPositions} />
        </MapContainer>
      </div>
      
      {/* Floating Telemetry Pill overlaying the map */}
      <div className="floating-telemetry">
        {route.routed ? (
          <>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Navigation size={15} color="#475569" /> {route.distance_km?.toFixed(1)} km
            </span>
            <span style={{ color: '#cbd5e1' }}>|</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Clock size={15} color="#475569" /> {Math.round(route.duration_min ?? 0)} min ETA
            </span>
          </>
        ) : (
          <span className="muted" style={{ fontWeight: 'normal' }}>
            Straight-line preview
          </span>
        )}
      </div>
    </div>
  );
}
