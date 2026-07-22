import { useEffect } from "react";
import L from "leaflet";
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from "react-leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import type { RouteInfo } from "../types";

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
        {route.waypoints.map((w, i) => (
          <Marker key={i} position={[w.lat, w.lng]}>
            <Popup>{w.label}</Popup>
          </Marker>
        ))}
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
