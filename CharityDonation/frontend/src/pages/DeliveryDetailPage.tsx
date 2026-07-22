import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { confirmReceiver, confirmVolunteer, getDelivery } from "../api/deliveries";
import { getDeliveryRoute } from "../api/routes";
import { useAuth } from "../hooks/useAuth";
import { API_URL, ApiError } from "../api/client";
import { RouteMap } from "../components/RouteMap";

export default function DeliveryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreviewUrl, setPhotoPreviewUrl] = useState<string | null>(null);

  const { data: delivery, isLoading } = useQuery({
    queryKey: ["delivery", id],
    queryFn: () => getDelivery(id!),
    enabled: !!id,
  });

  const { data: route } = useQuery({
    queryKey: ["delivery-route", id],
    queryFn: () => getDeliveryRoute(id!),
    enabled: !!id,
    retry: false,
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["delivery", id] });
    queryClient.invalidateQueries({ queryKey: ["assignments"] });
  };

  const volunteerConfirm = useMutation({
    mutationFn: () => confirmVolunteer(id!),
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to confirm"),
  });

  const receiverConfirm = useMutation({
    mutationFn: (photo: File) => confirmReceiver(id!, photo),
    onSuccess: () => {
      setPhotoFile(null);
      setPhotoPreviewUrl(null);
      invalidate();
    },
    onError: (err) => {
      if (err instanceof ApiError && err.code === "photo_mismatch") {
        setError(`${err.message} Please take a new photo and try again.`);
        setPhotoFile(null);
        setPhotoPreviewUrl(null);
      } else {
        setError(err instanceof ApiError ? err.message : "Failed to confirm");
      }
    },
  });

  function handlePhotoSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;
    setPhotoFile(file);
    setPhotoPreviewUrl(file ? URL.createObjectURL(file) : null);
  }

  if (isLoading) return <div className="container">Loading...</div>;
  if (!delivery) return <div className="container">Delivery not found.</div>;

  const isVolunteer = delivery.volunteer_id === user?.id;
  const isReceiver = delivery.receiver_id === user?.id;

  return (
    <div className="container">
      <h1>Delivery detail</h1>
      {error && <div className="error">{error}</div>}
      <div className="card">
        <strong>{delivery.donation.item_name}</strong> (qty {delivery.donation.quantity})
        <div className="muted">Receiver: {delivery.receiver.full_name}</div>
        <div>
          Status: <span className="badge">{delivery.status}</span>
        </div>
        {delivery.gemini_reasoning && <p className="muted">{delivery.gemini_reasoning}</p>}
        <div className="row" style={{ marginTop: "0.5rem" }}>
          <span className="badge">
            Volunteer confirmed: {delivery.volunteer_confirmed ? "yes" : "no"}
          </span>
          <span className="badge">
            Receiver confirmed: {delivery.receiver_confirmed ? "yes" : "no"}
          </span>
        </div>

        {isVolunteer && !delivery.volunteer_confirmed && delivery.status === "in_transit" && (
          <button
            style={{ marginTop: "0.75rem" }}
            onClick={() => volunteerConfirm.mutate()}
            disabled={volunteerConfirm.isPending}
          >
            Mark delivered (volunteer)
          </button>
        )}

        {isReceiver && !delivery.receiver_confirmed && delivery.status === "in_transit" && (
          <div style={{ marginTop: "0.75rem" }}>
            <label>
              Photo of what you received
              <input type="file" accept="image/jpeg,image/png,image/webp" onChange={handlePhotoSelected} />
            </label>
            {photoPreviewUrl && (
              <img
                src={photoPreviewUrl}
                alt="Preview of received item"
                style={{ maxWidth: 240, borderRadius: 8, marginTop: "0.5rem", display: "block" }}
              />
            )}
            <button
              style={{ marginTop: "0.5rem" }}
              onClick={() => photoFile && receiverConfirm.mutate(photoFile)}
              disabled={!photoFile || receiverConfirm.isPending}
            >
              {receiverConfirm.isPending ? "Confirming..." : "Confirm received"}
            </button>
          </div>
        )}

        {delivery.receiver_photo_path && (
          <div style={{ marginTop: "0.75rem" }}>
            <div className="muted">Photo submitted by receiver:</div>
            <img
              src={`${API_URL}/uploads/${delivery.receiver_photo_path}`}
              alt="Item received by recipient"
              style={{ maxWidth: 240, borderRadius: 8, marginTop: "0.5rem", display: "block" }}
            />
            {delivery.photo_match !== null && delivery.photo_match !== undefined && (
              <div className="row" style={{ marginTop: "0.5rem", alignItems: "center" }}>
                <span
                  className="badge"
                  style={!delivery.photo_match ? { background: "#fee2e2", color: "#dc2626" } : undefined}
                >
                  AI check: {delivery.photo_match ? "verified match" : "flagged mismatch"}
                </span>
              </div>
            )}
            {(delivery.photo_match === null || delivery.photo_match === undefined) && (
              <p className="muted" style={{ marginTop: "0.35rem" }}>
                AI verification was unavailable when this was submitted.
              </p>
            )}
            {delivery.photo_verification_reasoning && (
              <p className="muted" style={{ marginTop: "0.35rem" }}>
                {delivery.photo_verification_reasoning}
              </p>
            )}
          </div>
        )}
      </div>

      {route && (
        <div className="card">
          <strong>Route: warehouse &rarr; receiver</strong>
          <div style={{ marginTop: "0.5rem" }}>
            <RouteMap route={route} />
          </div>
        </div>
      )}
    </div>
  );
}
