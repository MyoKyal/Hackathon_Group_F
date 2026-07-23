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
import { MapPin, Info, CheckCircle } from "lucide-react";

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
    <div style={{ marginTop: "1rem" }}>
      <button className="btn-dark-glass" onClick={() => setExpanded((e) => !e)}>
        {expanded ? "Hide route preview" : "View route map"}
      </button>
      {expanded && isFetching && <p className="muted" style={{ marginTop: '0.5rem' }}>Loading route...</p>}
      {expanded && route && <RouteMap route={route} height={260} />}
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
    <div className="container" style={{ maxWidth: '900px' }}>
      
      {/* Dashboard Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em', margin: 0 }}>
          Volunteer Dashboard
        </h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#ecfdf5', padding: '0.25rem 0.75rem', borderRadius: '9999px', border: '1px solid #d1fae5' }}>
          <div className="status-dot"></div>
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#059669' }}>Active Dispatch Mode</span>
        </div>
      </div>

      {isLoading && <p className="muted">Loading dispatch assignments...</p>}
      {error && <div className="error">{error}</div>}

      {/* Offers Section */}
      <h2 style={{ fontSize: '1.5rem', color: '#1e293b', marginBottom: '1rem' }}>Current offer</h2>
      {offers.length === 0 && (
        <div className="alert-neutral">
          <Info size={20} />
          No pending offers right now. We'll alert you when a pickup is requested.
        </div>
      )}
      {offers.map((a) => (
        <div className="dashboard-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }} key={`${a.leg}-${a.id}`}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <strong style={{ fontSize: '1.25rem', color: '#0f172a' }}>{a.donation.item_name}</strong>
            <span className="qty-badge">qty {a.donation.quantity}</span>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.75rem', color: '#334155', fontWeight: 500 }}>
            <MapPin size={18} color="#64748b" />
            {offerDestination(a)}
          </div>
          
          {a.gemini_reasoning && (
            <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.9rem', color: '#475569', marginTop: '1rem', borderLeft: '3px solid #cbd5e1' }}>
              <strong>AI Match Note:</strong> {a.gemini_reasoning}
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
            {a.leg === "pickup" ? (
              <>
                <button
                  className="btn-emerald"
                  onClick={() => acceptPickupMutation.mutate(a.id)}
                  disabled={acceptPickupMutation.isPending}
                >
                  Accept Dispatch
                </button>
                <button
                  className="btn-rose"
                  onClick={() => declinePickupMutation.mutate(a.id)}
                  disabled={declinePickupMutation.isPending}
                >
                  Decline
                </button>
              </>
            ) : (
              <>
                <button 
                  className="btn-emerald"
                  onClick={() => acceptMutation.mutate(a.id)} 
                  disabled={acceptMutation.isPending}
                >
                  Accept Dispatch
                </button>
                <button
                  className="btn-rose"
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

      {/* Active Assignment Section */}
      <h2 style={{ fontSize: '1.5rem', color: '#1e293b', marginTop: '3rem', marginBottom: '1rem' }}>Active assignment</h2>
      {active.length === 0 && (
        <div className="alert-neutral">
          <Info size={20} />
          No active deliveries. Accept an offer above to begin.
        </div>
      )}
      {active.map((a) => (
        <div className="dashboard-card" style={{ padding: '1.5rem', marginBottom: '1.5rem', border: '1px solid #c7d2fe' }} key={`${a.leg}-${a.id}`}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <strong style={{ fontSize: '1.25rem', color: '#0f172a' }}>{a.donation.item_name}</strong>
            <span className="qty-badge">qty {a.donation.quantity}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.75rem', color: '#334155', fontWeight: 500 }}>
            <MapPin size={18} color="#64748b" />
            {offerDestination(a)}
          </div>

          <div style={{ marginTop: '1.5rem' }}>
            {a.leg === "pickup" ? (
              <button
                className="btn-indigo"
                onClick={() => confirmPickupMutation.mutate(a.id)}
                disabled={confirmPickupMutation.isPending}
              >
                Mark delivered to warehouse
              </button>
            ) : (
              <Link to={`/deliveries/${a.id}`} style={{ textDecoration: 'none' }}>
                <button className="btn-indigo">Complete Delivery Handover</button>
              </Link>
            )}
          </div>
          <RouteToggle assignment={a} />
        </div>
      ))}

      {/* Completed Section */}
      {completed.length > 0 && (
        <div style={{ marginTop: '4rem' }}>
          <h2 style={{ fontSize: '1.5rem', color: '#1e293b', marginBottom: '1rem' }}>Completed History</h2>
          <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
            {completed.map((a) => (
              <div className="dashboard-card" style={{ padding: '1rem' }} key={`${a.leg}-${a.id}`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#10b981', marginBottom: '0.5rem' }}>
                  <CheckCircle size={16} /> <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>COMPLETED</span>
                </div>
                <strong style={{ display: 'block', color: '#0f172a' }}>{a.donation.item_name}</strong>
                <span className="muted" style={{ fontSize: '0.9rem' }}>
                  {a.leg === "pickup"
                    ? `Delivered to ${a.warehouse?.name}`
                    : `Delivered to ${a.receiver?.full_name}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
