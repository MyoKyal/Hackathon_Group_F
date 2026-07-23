import { useEffect } from "react";
import L from "leaflet";
import { MapContainer, Marker, Polyline, TileLayer, Tooltip, useMap } from "react-leaflet";
import type { RouteInfo } from "../types";

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
    <div>
      <MapContainer center={waypointPositions[0]} zoom={12} style={{ height }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline
          positions={linePositions}
          pathOptions={{
            color: "#2563eb",
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
      <p className="muted" style={{ marginTop: "0.4rem" }}>
        {route.routed
          ? `${route.distance_km?.toFixed(1)} km · ${Math.round(route.duration_min ?? 0)} min by road`
          : "Showing a straight-line preview — street routing is unavailable."}
      </p>
    </div>
  );
}
