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
    <div className="container">
      <h1>Admin</h1>
      {error && <div className="error">{error}</div>}

      <div className="card">
        <label className="row" style={{ justifyContent: "space-between" }}>
          <span>Require approval for AI matches</span>
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

      <h2>Pending Matches</h2>
      {matchesLoading && <p className="muted">Loading...</p>}
      {pendingMatches?.length === 0 && <p className="muted">No matches awaiting review.</p>}
      {pendingMatches?.map((m) => (
        <div className="card" key={m.id}>
          <div>
            <strong>{m.donation.item_name}</strong>{" "}
            <span className="muted">to {m.receiver.full_name}</span>
          </div>
          {m.gemini_reasoning && <p className="muted">{m.gemini_reasoning}</p>}
          {m.stage1_score != null && <p className="muted">Score: {m.stage1_score.toFixed(2)}</p>}
          <div className="row" style={{ marginTop: "0.5rem" }}>
            <button
              onClick={() => approveMatchMutation.mutate(m.id)}
              disabled={approveMatchMutation.isPending}
            >
              Approve
            </button>
            <button
              className="danger"
              onClick={() => rejectMatchMutation.mutate(m.id)}
              disabled={rejectMatchMutation.isPending}
            >
              Reject
            </button>
          </div>
        </div>
      ))}

      <h2>Inventory</h2>
      {inventoryLoading && <p className="muted">Loading...</p>}
      {inventory &&
        Object.entries(groupByWarehouse(inventory)).map(([warehouseName, items]) => (
          <div className="card" key={warehouseName}>
            <strong>{warehouseName}</strong>
            <div className="row" style={{ flexWrap: "wrap", gap: "0.5rem", marginTop: "0.5rem" }}>
              {items.map((i) => (
                <span className="badge" key={i.category}>
                  {ITEM_CATEGORY_LABELS[i.category]}: {i.quantity}
                </span>
              ))}
            </div>
          </div>
        ))}

      <h2>Users</h2>
      {isLoading && <p className="muted">Loading...</p>}
      {users?.map((u) => (
        <div className="card" key={u.id}>
          <div className="row" style={{ justifyContent: "space-between" }}>
            <div>
              <strong>{u.full_name}</strong> <span className="muted">{u.email}</span>
            </div>
            <span className="badge">{u.volunteer_status}</span>
          </div>
          {u.transportation_type && (
            <div className="muted">
              {u.transportation_type} · capacity{" "}
              {u.max_carrying_capacity_kg == null ? "unlimited" : `${u.max_carrying_capacity_kg} kg`}{" "}
              · max {u.max_travel_distance_km} km · rating {u.reliability_rating.toFixed(1)} ·{" "}
              {u.completed_deliveries} completed, {u.active_deliveries} active
            </div>
          )}
          <div className="row" style={{ marginTop: "0.5rem" }}>
            {(u.volunteer_status === "pending" || u.volunteer_status === "rejected") && (
              <button onClick={() => approveMutation.mutate(u.id)} disabled={approveMutation.isPending}>
                Approve
              </button>
            )}
            {u.volunteer_status === "approved" && (
              <button
                className="danger"
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
  );
}
