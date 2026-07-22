import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { confirmReceiver, confirmVolunteer, getDelivery } from "../api/deliveries";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../api/client";

export default function DeliveryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data: delivery, isLoading } = useQuery({
    queryKey: ["delivery", id],
    queryFn: () => getDelivery(id!),
    enabled: !!id,
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
    mutationFn: () => confirmReceiver(id!),
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to confirm"),
  });

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
          <button
            style={{ marginTop: "0.75rem" }}
            onClick={() => receiverConfirm.mutate()}
            disabled={receiverConfirm.isPending}
          >
            Confirm received
          </button>
        )}
      </div>
    </div>
  );
}
