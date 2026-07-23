import { useEffect } from "react";
import L from "leaflet";
import { MapContainer, Marker, Polyline, TileLayer, Tooltip, useMap } from "react-leaflet";
import type { RouteInfo } from "../types";
import { Navigation, Clock } from "lucide-react";

interface Props {
  route: RouteInfo;
  height?: number;
}

const ROLE_STYLES: Record<string, { color: string; tag: string }> = {
  volunteer: { color: "#16a34a", tag: "Volunteer" },
  pickup: { color: "#f97316", tag: "Pickup" },
  warehouse: { color: "#2563eb", tag: "Warehouse" },
  receiver: { color: "#9333ea", tag: "Receiver" },
};

function classifyWaypoint(label: string): { color: string; tag: string } {
  if (label.startsWith("Volunteer")) return ROLE_STYLES.volunteer;
  if (label.startsWith("Pickup")) return ROLE_STYLES.pickup;
  if (label.startsWith("Warehouse")) return ROLE_STYLES.warehouse;
  return ROLE_STYLES.receiver;
}

function makeDivIcon(color: string): L.DivIcon {
  return L.divIcon({
    className: "role-marker",
    html: `<span class="role-marker-pin" style="background:${color}"></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
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
          {route.waypoints.map((w, i) => {
            const { color, tag } = classifyWaypoint(w.label);
            const detail = w.label.includes(": ") ? w.label.split(": ")[1] : null;
            return (
              <Marker key={i} position={[w.lat, w.lng]} icon={makeDivIcon(color)}>
                <Tooltip permanent direction="top" offset={[0, -10]} className="role-marker-tooltip">
                  <strong>{tag}</strong>
                  {detail && <div>{detail}</div>}
                </Tooltip>
              </Marker>
            );
          })}
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
            Showing a straight-line preview — street routing is unavailable.
          </span>
        )}
      </div>
    </div>
  );
}
