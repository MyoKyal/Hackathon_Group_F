import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import { MapContainer, Marker, TileLayer, useMapEvents } from "react-leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import type { Location } from "../../types";

// ponytail: Leaflet's default marker icon URLs break under Vite bundling —
// this is the documented workaround, done once at module scope.
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const FALLBACK_CENTER: Location = { lat: 20, lng: 0 };
const IS_UNSET = (loc: Location) => loc.lat === 0 && loc.lng === 0;

interface Props {
  value: Location;
  onChange: (loc: Location) => void;
}

function ClickHandler({ onPick }: { onPick: (loc: Location) => void }) {
  useMapEvents({
    click(e) {
      onPick({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
  });
  return null;
}

export function LocationPicker({ value, onChange }: Props) {
  const [status, setStatus] = useState<"locating" | "ready">(
    IS_UNSET(value) && navigator.geolocation ? "locating" : "ready",
  );
  const [geoError, setGeoError] = useState<string | null>(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    if (status !== "locating") return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        onChangeRef.current({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setStatus("ready");
      },
      () => {
        setGeoError("Couldn't detect your location — drag the pin or click the map to set it.");
        setStatus("ready");
      },
      { timeout: 8000 },
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once on mount only
  }, [status]);

  if (status === "locating") {
    return <p className="muted">Detecting your location...</p>;
  }

  const center = IS_UNSET(value) ? FALLBACK_CENTER : value;

  return (
    <div>
      {geoError && <p className="muted">{geoError}</p>}
      <MapContainer
        center={[center.lat, center.lng]}
        zoom={IS_UNSET(value) ? 2 : 13}
        style={{ height: 300 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker
          position={[center.lat, center.lng]}
          draggable
          eventHandlers={{
            dragend: (e) => {
              const marker = e.target as L.Marker;
              const pos = marker.getLatLng();
              onChange({ lat: pos.lat, lng: pos.lng });
            },
          }}
        />
        <ClickHandler onPick={onChange} />
      </MapContainer>
      <p className="muted">
        {center.lat.toFixed(5)}, {center.lng.toFixed(5)}
      </p>
    </div>
  );
}
