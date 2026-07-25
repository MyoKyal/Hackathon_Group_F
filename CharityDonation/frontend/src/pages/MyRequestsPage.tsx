import { useQuery } from "@tanstack/react-query";
import { listRequests } from "../api/requests";
import { Clock, Search, Filter, Package } from "lucide-react";

export default function MyRequestsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["requests"],
    queryFn: listRequests,
  });

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
        hour12: true,
      }).format(date);
    } catch {
      return "Unknown time";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "pending":
        return "badge-pending";
      case "fulfilled":
        return "badge-completed";
      default:
        return "badge-active";
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1200px' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.25rem' }}>My Requests</h1>
        <p className="muted" style={{ fontSize: '1.1rem' }}>Track and manage the items you have requested</p>
        
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
          <div className="input-wrapper" style={{ flex: 1, minWidth: '250px', maxWidth: '400px' }}>
            <Search className="input-icon" size={18} />
            <input placeholder="Search my requests..." style={{ borderRadius: '9999px', padding: '0.6rem 1rem 0.6rem 2.5rem' }} />
          </div>
          <button className="secondary" style={{ borderRadius: '9999px', padding: '0.6rem 1.25rem', background: 'white', color: '#334155', border: '1px solid var(--border)' }}>
            <Filter size={16} /> Filter
          </button>
        </div>
      </div>

      {isLoading && (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="muted">Loading your requests...</div>
        </div>
      )}
      {error && <div className="error">Failed to load requests. Please try again.</div>}
      {data && data.length === 0 && (
        <div style={{ textAlign: 'center', padding: '4rem', background: 'var(--card-bg)', borderRadius: '24px', border: '1px dashed var(--border)' }}>
          <Package size={48} color="#94a3b8" style={{ margin: '0 auto 1rem auto' }} />
          <h3 style={{ color: '#475569' }}>No requests yet</h3>
        </div>
      )}

      <div className="dashboard-grid">
        {data?.map((r) => (
          <div className="dashboard-card" key={r.id} style={{ padding: '1.25rem' }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: '1rem' }}>
              <strong style={{ fontSize: '1.15rem', color: '#0f172a', lineHeight: 1.3 }}>{r.item_name}</strong>
              <span className={`badge ${getStatusBadge(r.status)}`} style={{ textTransform: 'uppercase', fontSize: '0.7rem', padding: '0.2rem 0.6rem' }}>
                {r.status}
              </span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem' }}>
              <span className="badge badge-category">{r.item_category}</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#475569', background: '#f1f5f9', padding: '0.2rem 0.6rem', borderRadius: '6px' }}>
                Needed: {r.quantity_needed}
              </span>
            </div>

            <div className="timestamp-block">
              <Clock size={14} />
              {r.created_at ? formatTime(r.created_at) : "Just now"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
