import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { approveVolunteer, listAllUsers, revokeVolunteer } from "../api/volunteers";
import { approveMatch, listPendingMatches, rejectMatch } from "../api/adminMatches";
import { getSettings, updateSettings } from "../api/adminSettings";
import { listInventory } from "../api/warehouses";
import { ITEM_CATEGORY_LABELS } from "../constants/categories";
import type { InventoryItem } from "../types";
import { ApiError } from "../api/client";

function groupByWarehouse(items: InventoryItem[]): Record<string, InventoryItem[]> {
  const groups: Record<string, InventoryItem[]> = {};
  for (const item of items) {
    (groups[item.warehouse_name] ??= []).push(item);
  }
  return groups;
}

export default function AdminPage() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data: users, isLoading } = useQuery({
    queryKey: ["admin-users"],
    queryFn: listAllUsers,
  });

  const { data: settings } = useQuery({
    queryKey: ["admin-settings"],
    queryFn: getSettings,
  });

  const { data: pendingMatches, isLoading: matchesLoading } = useQuery({
    queryKey: ["admin-pending-matches"],
    queryFn: listPendingMatches,
  });

  const { data: inventory, isLoading: inventoryLoading } = useQuery({
    queryKey: ["admin-inventory"],
    queryFn: listInventory,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["admin-users"] });
  const invalidateMatches = () =>
    queryClient.invalidateQueries({ queryKey: ["admin-pending-matches"] });

  const approveMutation = useMutation({
    mutationFn: approveVolunteer,
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to approve"),
  });

  const revokeMutation = useMutation({
    mutationFn: revokeVolunteer,
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to revoke"),
  });

  const toggleSettingMutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-settings"] });
      invalidateMatches();
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to update settings"),
  });

  const approveMatchMutation = useMutation({
    mutationFn: approveMatch,
    onSuccess: invalidateMatches,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to approve match"),
  });

  const rejectMatchMutation = useMutation({
    mutationFn: rejectMatch,
    onSuccess: invalidateMatches,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to reject match"),
  });

  return (
    <div className="container" style={{ maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '2rem' }}>Admin Dashboard</h1>
      {error && <div className="error">{error}</div>}

      <div className="admin-dashboard-layout">
        
        {/* Top Full-Width Settings Block */}
        <section className="admin-settings-section">
          <div className="card" style={{ margin: 0 }}>
            <label className="row" style={{ justifyContent: "space-between", margin: 0 }}>
              <span style={{ fontWeight: 600 }}>Require approval for AI matches</span>
              <input
                type="checkbox"
                checked={settings?.require_match_approval ?? false}
                disabled={toggleSettingMutation.isPending}
                onChange={(e) =>
                  toggleSettingMutation.mutate({ require_match_approval: e.target.checked })
                }
              />
            </label>
          </div>
        </section>

        {/* Left Column Block (Spans 2 Rows) */}
        <section className="admin-matches-section">
          <div className="card" style={{ margin: 0, height: '100%', background: 'var(--bg)', border: '1px solid var(--border)', boxShadow: 'none' }}>
            <h2 style={{ marginTop: 0 }}>Pending Matches</h2>
            {matchesLoading && <p className="muted">Loading...</p>}
            {pendingMatches?.length === 0 && <p className="muted">No matches awaiting review.</p>}
            <div className="grid-responsive-4">
              {pendingMatches?.map((m) => (
                <div className="card" key={m.id} style={{ margin: 0, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ marginBottom: '1rem' }}>
                    <strong>{m.donation.item_name}</strong>{" "}
                    <span className="muted">to {m.receiver.full_name}</span>
                  </div>
                  {m.gemini_reasoning && <p className="muted" style={{ fontSize: '0.85rem' }}>{m.gemini_reasoning}</p>}
                  {m.stage1_score != null && <p className="muted" style={{ marginTop: 'auto', fontWeight: 600 }}>Score: {m.stage1_score.toFixed(2)}</p>}
                  
                  <div className="row" style={{ marginTop: "1rem" }}>
                    <button
                      className="btn-primary-navy"
                      style={{ flex: 1, padding: '0.5rem' }}
                      onClick={() => approveMatchMutation.mutate(m.id)}
                      disabled={approveMatchMutation.isPending}
                    >
                      Approve
                    </button>
                    <button
                      className="btn-coral"
                      style={{ flex: 1, padding: '0.5rem' }}
                      onClick={() => rejectMatchMutation.mutate(m.id)}
                      disabled={rejectMatchMutation.isPending}
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Right Top Block */}
        <section className="admin-inventory-section">
          <div className="card" style={{ margin: 0, height: '100%', background: 'var(--bg)', border: '1px solid var(--border)', boxShadow: 'none' }}>
            <h2 style={{ marginTop: 0 }}>Inventory</h2>
            {inventoryLoading && <p className="muted">Loading...</p>}
            <div className="grid-responsive-4">
              {inventory &&
                Object.entries(groupByWarehouse(inventory)).map(([warehouseName, items]) => (
                  <div className="card" key={warehouseName} style={{ margin: 0, display: 'flex', flexDirection: 'column' }}>
                    <strong style={{ fontSize: '1.2rem', marginBottom: '1rem', color: 'var(--navy)' }}>{warehouseName}</strong>
                    <div className="row" style={{ flexWrap: "wrap", gap: "0.5rem" }}>
                      {items.map((i) => (
                        <span className="badge" key={i.category} style={{ background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)' }}>
                          {ITEM_CATEGORY_LABELS[i.category]}: <strong>{i.quantity}</strong>
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </section>

        {/* Right Bottom Block */}
        <section className="admin-users-section">
          <div className="card" style={{ margin: 0, height: '100%', background: 'var(--bg)', border: '1px solid var(--border)', boxShadow: 'none' }}>
            <h2 style={{ marginTop: 0 }}>Users</h2>
            {isLoading && <p className="muted">Loading...</p>}
            <div className="grid-responsive-4">
              {users?.map((u) => (
                <div className="card" key={u.id} style={{ margin: 0, display: 'flex', flexDirection: 'column' }}>
                  <div className="row" style={{ justifyContent: "space-between", marginBottom: '0.5rem' }}>
                    <div>
                      <strong style={{ display: 'block', fontSize: '1.1rem' }}>{u.full_name}</strong> 
                      <span className="muted" style={{ fontSize: '0.85rem' }}>{u.email}</span>
                    </div>
                    <span className="badge" style={{ background: u.volunteer_status === 'approved' ? '#10b98120' : 'var(--bg)', color: u.volunteer_status === 'approved' ? '#10b981' : 'var(--text-muted)' }}>
                      {u.volunteer_status}
                    </span>
                  </div>
                  
                  {u.transportation_type && (
                    <div className="muted" style={{ fontSize: '0.85rem', marginBottom: '1rem', background: 'var(--bg)', padding: '0.75rem', borderRadius: '0.5rem' }}>
                      <div style={{ marginBottom: '0.25rem' }}><strong>Transport:</strong> {u.transportation_type}</div>
                      <div style={{ marginBottom: '0.25rem' }}><strong>Capacity:</strong> {u.max_carrying_capacity_kg == null ? "Unlimited" : `${u.max_carrying_capacity_kg} kg`}</div>
                      <div style={{ marginBottom: '0.25rem' }}><strong>Radius:</strong> {u.max_travel_distance_km} km</div>
                      <div style={{ marginBottom: '0.25rem' }}><strong>Rating:</strong> {u.reliability_rating.toFixed(1)} / 5</div>
                      <div><strong>Stats:</strong> {u.completed_deliveries} done, {u.active_deliveries} active</div>
                    </div>
                  )}
                  
                  <div className="row" style={{ marginTop: "auto", paddingTop: '1rem', gap: '0.5rem' }}>
                    {(u.volunteer_status === "pending" || u.volunteer_status === "rejected") && (
                      <button 
                        className="btn-primary-navy" 
                        style={{ flex: 1, padding: '0.5rem' }} 
                        onClick={() => approveMutation.mutate(u.id)} 
                        disabled={approveMutation.isPending}
                      >
                        Approve
                      </button>
                    )}
                    {u.volunteer_status === "approved" && (
                      <button
                        className="btn-coral"
                        style={{ flex: 1, padding: '0.5rem' }}
                        onClick={() => revokeMutation.mutate(u.id)}
                        disabled={revokeMutation.isPending}
                      >
                        Revoke
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
