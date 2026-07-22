import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listMatches } from "../api/deliveries";
import { useAuth } from "../hooks/useAuth";

export default function MatchesPage() {
  const { user } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ["matches"],
    queryFn: listMatches,
  });

  return (
    <div className="container">
      <h1>{user?.is_admin ? "All Matches" : "My Matches"}</h1>
      {isLoading && <p className="muted">Loading...</p>}
      {error && <p className="error">Failed to load matches.</p>}
      {data && data.length === 0 && <p className="muted">No matches yet.</p>}
      {data?.map((m) => (
        <div className="card" key={m.id}>
          <div className="row" style={{ justifyContent: "space-between" }}>
            <strong>{m.donation_item_name}</strong>
            <span className="badge">{m.status}</span>
          </div>
          <div className="muted">
            {new Date(m.created_at).toLocaleString()}
          </div>
          <div style={{ marginTop: "0.5rem" }}>
            <div>
              Donation: {m.donation_item_name} · {m.donor_name} · qty {m.donation_quantity}
            </div>
            <div>
              Request: {m.request_item_name ?? "—"} · {m.receiver_name}
              {m.request_quantity_needed != null && ` · qty ${m.request_quantity_needed}`}
            </div>
          </div>
          {m.gemini_reasoning && <p className="muted">{m.gemini_reasoning}</p>}
          {m.stage1_score != null && (
            <p className="muted">Match score: {m.stage1_score.toFixed(2)}</p>
          )}
          <p>
            <Link to={`/deliveries/${m.id}`}>View Details</Link>
          </p>
        </div>
      ))}
    </div>
  );
}
