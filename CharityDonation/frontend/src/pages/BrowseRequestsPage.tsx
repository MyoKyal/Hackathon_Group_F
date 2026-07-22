import { useQuery } from "@tanstack/react-query";
import { listAllRequests } from "../api/requests";

export default function BrowseRequestsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["requests-all"],
    queryFn: listAllRequests,
  });

  return (
    <div className="container">
      <h1>Browse All Requests</h1>
      {isLoading && <p className="muted">Loading...</p>}
      {error && <p className="error">Failed to load requests.</p>}
      {data && data.length === 0 && <p className="muted">No requests yet.</p>}
      {data?.map((r) => (
        <div className="card" key={r.id}>
          <div className="row" style={{ justifyContent: "space-between" }}>
            <strong>{r.item_name}</strong>
            <span className="badge">{r.status}</span>
          </div>
          <div className="muted">
            {r.item_category} · needed {r.quantity_needed} · requested by {r.requester_name}
          </div>
        </div>
      ))}
    </div>
  );
}
