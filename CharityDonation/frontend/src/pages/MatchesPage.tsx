import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listMatches } from "../api/deliveries";
import { useAuth } from "../hooks/useAuth";
import { Clock, Search, Filter, Sparkles, ArrowRight } from "lucide-react";

export default function MatchesPage() {
  const { user } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ["matches"],
    queryFn: listMatches,
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
        return "badge-completed";
      default:
        return "badge-active";
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1200px' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          fontWeight: 800, 
          background: 'linear-gradient(135deg, #F24361, #288BEF)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '0.25rem' 
        }}>
          {user?.is_admin ? "All AI Matches" : "My Matches"}
        </h1>
        <p className="muted" style={{ fontSize: '1.1rem' }}>Smart connections powered by Gemini</p>
        
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
          <div className="input-wrapper" style={{ flex: 1, minWidth: '250px', maxWidth: '400px' }}>
            <Search className="input-icon" size={18} />
            <input placeholder="Search matches..." style={{ borderRadius: '9999px', padding: '0.6rem 1rem 0.6rem 2.5rem' }} />
          </div>
          <button className="secondary" style={{ borderRadius: '9999px', padding: '0.6rem 1.25rem', background: 'white', color: '#334155', border: '1px solid var(--border)' }}>
            <Filter size={16} /> Filter
          </button>
        </div>
      </div>

      {isLoading && (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="muted">Loading AI matches...</div>
        </div>
      )}
      {error && <div className="error">Failed to load matches. Please try again.</div>}
      {data && data.length === 0 && (
        <div style={{ textAlign: 'center', padding: '4rem', background: 'var(--card-bg)', borderRadius: '24px', border: '1px dashed var(--border)' }}>
          <Sparkles size={48} color="#94a3b8" style={{ margin: '0 auto 1rem auto' }} />
          <h3 style={{ color: '#475569' }}>No matches found</h3>
        </div>
      )}

      <div className="dashboard-grid">
        {data?.map((m) => (
          <div className="dashboard-card" key={m.id} style={{ padding: '1.25rem', borderLeft: '4px solid #F24361' }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: '1rem' }}>
              <strong style={{ fontSize: '1.15rem', color: '#0f172a', lineHeight: 1.3 }}>{m.donation_item_name}</strong>
              <span className={`badge ${getStatusBadge(m.status)}`} style={{ textTransform: 'uppercase', fontSize: '0.7rem', padding: '0.2rem 0.6rem' }}>
                {m.status}
              </span>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.75rem', fontSize: '0.9rem', color: '#475569' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontWeight: 600, color: '#F24361' }}>Donation:</span> 
                {m.donation_item_name} (Qty: {m.donation_quantity})
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontWeight: 600, color: '#288BEF' }}>Request:</span> 
                {m.request_item_name ?? "—"} to {m.receiver_name} {m.request_quantity_needed != null && `(Qty: ${m.request_quantity_needed})`}
              </div>
            </div>

            {m.gemini_reasoning && (
              <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(40, 139, 239, 0.05)', borderRadius: '0.5rem', border: '1px dashed rgba(40, 139, 239, 0.3)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#288BEF', fontWeight: 700, fontSize: '0.75rem', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                  <Sparkles size={12} /> AI Insight
                </div>
                <p style={{ margin: 0, fontSize: '0.85rem', color: '#334155', fontStyle: 'italic' }}>{m.gemini_reasoning}</p>
                {m.stage1_score != null && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', fontWeight: 600, color: '#10b981' }}>
                    Match Confidence: {(m.stage1_score * 100).toFixed(0)}%
                  </div>
                )}
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
              <div className="timestamp-block" style={{ borderTop: 'none', margin: 0, padding: 0 }}>
                <Clock size={14} />
                {m.created_at ? formatTime(m.created_at) : "Just now"}
              </div>
              <Link to={`/deliveries/${m.id}`} style={{ textDecoration: 'none' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  View Details <ArrowRight size={14} />
                </span>
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
