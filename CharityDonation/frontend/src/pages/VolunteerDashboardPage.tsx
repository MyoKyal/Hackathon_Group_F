import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  acceptAssignment,
  acceptPickup,
  confirmPickup,
  declineAssignment,
  declinePickup,
  listAssignments,
} from "../api/volunteers";
import { getDeliveryRoute, getPickupRoute } from "../api/routes";
import { ApiError } from "../api/client";
import { useState } from "react";
import type { Assignment } from "../types";
import { RouteMap } from "../components/RouteMap";

function RouteToggle({ assignment }: { assignment: Assignment }) {
  const [expanded, setExpanded] = useState(false);

  const { data: route, isFetching } = useQuery({
    queryKey: ["route", assignment.leg, assignment.id],
    queryFn: () =>
      assignment.leg === "pickup" ? getPickupRoute(assignment.id) : getDeliveryRoute(assignment.id),
    enabled: expanded,
    retry: false,
  });

  return (
    <div style={{ marginTop: "0.5rem" }}>
      <button className="secondary" onClick={() => setExpanded((e) => !e)}>
        {expanded ? "Hide route" : "View route"}
      </button>
      {expanded && isFetching && <p className="muted">Loading route...</p>}
      {expanded && route && (
        <div style={{ marginTop: "0.5rem" }}>
          <RouteMap route={route} height={260} />
        </div>
      )}
    </div>
  );
}

export default function VolunteerDashboardPage() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data: assignments, isLoading } = useQuery({
    queryKey: ["assignments"],
    queryFn: listAssignments,
    refetchInterval: 15000,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["assignments"] });

  const acceptMutation = useMutation({
    mutationFn: acceptAssignment,
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to accept"),
  });

  const declineMutation = useMutation({
    mutationFn: declineAssignment,
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to decline"),
  });

  const acceptPickupMutation = useMutation({
    mutationFn: acceptPickup,
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to accept"),
  });

  const declinePickupMutation = useMutation({
    mutationFn: declinePickup,
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to decline"),
  });

  const confirmPickupMutation = useMutation({
    mutationFn: confirmPickup,
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to confirm"),
  });

  const offers = assignments?.filter((a) => a.is_current_offer && a.status === "awaiting_volunteer") ?? [];
  const active = assignments?.filter((a) => a.status === "in_transit") ?? [];
  const completed = assignments?.filter((a) => a.status === "completed") ?? [];

  function offerDestination(a: Assignment) {
    return a.leg === "pickup" ? `Deliver to warehouse: ${a.warehouse?.name}` : `For ${a.receiver?.full_name}`;
  }

  return (
    <div className="container">
      <h1>Volunteer Dashboard</h1>
      {isLoading && <p className="muted">Loading...</p>}
      {error && <div className="error">{error}</div>}

      <h2>Current offer</h2>
      {offers.length === 0 && <p className="muted">No pending offers right now.</p>}
      {offers.map((a) => (
        <div className="card" key={`${a.leg}-${a.id}`}>
          <strong>{a.donation.item_name}</strong> (qty {a.donation.quantity})
          <div className="muted">{offerDestination(a)}</div>
          {a.gemini_reasoning && <div className="muted">{a.gemini_reasoning}</div>}
          <div className="row" style={{ marginTop: "0.5rem" }}>
            {a.leg === "pickup" ? (
              <>
                <button
                  onClick={() => acceptPickupMutation.mutate(a.id)}
                  disabled={acceptPickupMutation.isPending}
                >
                  Accept
                </button>
                <button
                  className="danger"
                  onClick={() => declinePickupMutation.mutate(a.id)}
                  disabled={declinePickupMutation.isPending}
                >
                  Decline
                </button>
              </>
            ) : (
              <>
                <button onClick={() => acceptMutation.mutate(a.id)} disabled={acceptMutation.isPending}>
                  Accept
                </button>
                <button
                  className="danger"
                  onClick={() => declineMutation.mutate(a.id)}
                  disabled={declineMutation.isPending}
                >
                  Decline
                </button>
              </>
            )}
          </div>
          <RouteToggle assignment={a} />
        </div>
      ))}

      <h2>Active assignment</h2>
      {active.length === 0 && <p className="muted">No active deliveries.</p>}
      {active.map((a) => (
        <div className="card" key={`${a.leg}-${a.id}`}>
          <strong>{a.donation.item_name}</strong>
          <div className="muted">{offerDestination(a)}</div>
          {a.leg === "pickup" ? (
            <p>
              <button
                onClick={() => confirmPickupMutation.mutate(a.id)}
                disabled={confirmPickupMutation.isPending}
              >
                Mark delivered to warehouse
              </button>
            </p>
          ) : (
            <p>
              <Link to={`/deliveries/${a.id}`}>
                <button>Mark delivered</button>
              </Link>
            </p>
          )}
          <RouteToggle assignment={a} />
        </div>
      ))}

      {completed.length > 0 && (
        <>
          <h2>Completed</h2>
          {completed.map((a) => (
            <div className="card" key={`${a.leg}-${a.id}`}>
              <strong>{a.donation.item_name}</strong> —{" "}
              {a.leg === "pickup"
                ? `delivered to ${a.warehouse?.name}`
                : `delivered to ${a.receiver?.full_name}`}
            </div>
          ))}
        </>
      )}
    </div>
  );
}
