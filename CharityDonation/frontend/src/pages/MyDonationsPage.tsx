import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listDonations } from "../api/donations";
import { Clock, Search, Filter, Heart, ArrowRight } from "lucide-react";

export default function MyDonationsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["donations"],
    queryFn: listDonations,
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
      case "completed":
      case "delivered":
        return "badge-completed";
      default:
        return "badge-active";
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1200px' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.25rem' }}>My Donations</h1>
        <p className="muted" style={{ fontSize: '1.1rem' }}>Track and manage your community contributions</p>
        
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
          <div className="input-wrapper" style={{ flex: 1, minWidth: '250px', maxWidth: '400px' }}>
            <Search className="input-icon" size={18} />
            <input placeholder="Search my donations..." style={{ borderRadius: '9999px', padding: '0.6rem 1rem 0.6rem 2.5rem' }} />
          </div>
          <button className="secondary" style={{ borderRadius: '9999px', padding: '0.6rem 1.25rem', background: 'white', color: '#334155', border: '1px solid var(--border)' }}>
            <Filter size={16} /> Filter
          </button>
        </div>
      </div>

      {isLoading && (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="muted">Loading your donations...</div>
        </div>
      )}
      {error && <div className="error">Failed to load donations. Please try again.</div>}
      {data && data.length === 0 && (
        <div style={{ textAlign: 'center', padding: '4rem', background: 'var(--card-bg)', borderRadius: '24px', border: '1px dashed var(--border)' }}>
          <Heart size={48} color="#94a3b8" style={{ margin: '0 auto 1rem auto' }} />
          <h3 style={{ color: '#475569' }}>No donations yet</h3>
        </div>
      )}

      <div className="dashboard-grid">
        {data?.map((d) => (
          <div className="dashboard-card" key={d.id} style={{ padding: '1.25rem' }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: '1rem' }}>
              <strong style={{ fontSize: '1.15rem', color: '#0f172a', lineHeight: 1.3 }}>{d.item_name}</strong>
              <span className={`badge ${getStatusBadge(d.status)}`} style={{ textTransform: 'uppercase', fontSize: '0.7rem', padding: '0.2rem 0.6rem' }}>
                {d.status}
              </span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem' }}>
              <span className="badge badge-category">{d.item_category}</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#475569', background: '#f1f5f9', padding: '0.2rem 0.6rem', borderRadius: '6px' }}>
                Qty: {d.quantity}
              </span>
            </div>

            {d.delivery && (
              <div style={{ marginTop: '0.5rem' }}>
                <Link to={`/deliveries/${d.delivery.id}`} style={{ textDecoration: 'none' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#2563eb', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    View Delivery Details <ArrowRight size={14} />
                  </span>
                </Link>
              </div>
            )}

            <div className="timestamp-block">
              <Clock size={14} />
              {d.created_at ? formatTime(d.created_at) : "Just now"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
