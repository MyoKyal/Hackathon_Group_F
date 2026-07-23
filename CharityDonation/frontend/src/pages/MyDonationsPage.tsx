import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listDonations } from "../api/donations";
import type { VolunteerInfo } from "../types";
import { Package, MapPin, Activity, Heart, ArrowRight } from "lucide-react";

function volunteerLine(label: string, info: VolunteerInfo | null | undefined) {
  if (!info) return null;
  const statusText = info.status === "accepted" ? "Accepted" : "Pending";
  const statusColor = info.status === "accepted" ? "#10b981" : "#f59e0b";
  
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.75rem', padding: '0.75rem', background: '#f8fafc', borderRadius: '0.5rem' }}>
      <div>
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>{label}</div>
        <div style={{ fontWeight: 600, color: '#0f172a' }}>{info.full_name}</div>
      </div>
      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: statusColor, background: `${statusColor}20`, padding: '0.2rem 0.6rem', borderRadius: '9999px' }}>
        {statusText}
      </span>
    </div>
  );
}

export default function MyDonationsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["donations"],
    queryFn: listDonations,
  });

  // Helper for status badge inside dual-tone card
  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "pending":
        return { bg: "rgba(255, 255, 255, 0.2)", color: "#fff", border: "rgba(255, 255, 255, 0.4)" };
      case "completed":
      case "delivered":
        return { bg: "#10b981", color: "#fff", border: "transparent" };
      default:
        return { bg: "rgba(0, 0, 0, 0.2)", color: "#fff", border: "transparent" };
    }
  };

  const activeDonationsCount = data?.filter(d => d.status.toLowerCase() !== "delivered").length || 0;

  return (
    <div style={{ background: '#f8fafc', minHeight: 'calc(100vh - 64px)', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '1200px' }}>
        
        <div style={{ marginBottom: '2.5rem' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0f766e', marginBottom: '0.25rem', letterSpacing: '-0.02em' }}>My Donations</h1>
          <p className="muted" style={{ fontSize: '1.1rem' }}>Manage and track your community contributions.</p>
        </div>

        {/* Dashboard Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
          
          {/* Main Content: Donations Grid */}
          <div style={{ gridColumn: '1 / -1', '@media (min-width: 992px)': { gridColumn: '1 / 3' } } as any}>
            
            {isLoading && <p className="muted" style={{ padding: '2rem', textAlign: 'center' }}>Loading donations...</p>}
            {error && <p className="error">Failed to load donations.</p>}
            {data && data.length === 0 && (
              <div style={{ textAlign: 'center', padding: '4rem', background: 'white', borderRadius: '1rem', border: '1px dashed #cbd5e1' }}>
                <Heart size={48} color="#94a3b8" style={{ margin: '0 auto 1rem auto' }} />
                <h3 style={{ color: '#475569' }}>No donations yet</h3>
                <p className="muted">You haven't submitted any donations yet. Start giving today!</p>
              </div>
            )}
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
              {data?.map((d) => {
                const sBadge = getStatusBadge(d.status);
                return (
                  <div className="dual-tone-card" key={d.id}>
                    {/* Vivid Gradient Header */}
                    <div className="dual-tone-header">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                        <strong style={{ fontSize: '1.35rem', lineHeight: 1.2 }}>{d.item_name}</strong>
                        <span style={{ 
                          fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase',
                          background: sBadge.bg, color: sBadge.color, border: `1px solid ${sBadge.border}`,
                          padding: '0.2rem 0.75rem', borderRadius: '9999px' 
                        }}>
                          {d.status}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.9rem', opacity: 0.9 }}>
                        {d.item_category} &middot; Qty: {d.quantity}
                      </div>
                    </div>
                    
                    {/* Crisp White Body */}
                    <div className="dual-tone-body" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#475569', fontSize: '0.9rem', marginBottom: '1rem' }}>
                        <MapPin size={16} /> Target Warehouse: <strong style={{ color: '#0f766e' }}>{d.warehouse.name}</strong>
                      </div>
                      
                      {volunteerLine("Pickup Dispatch", d.pickup_volunteer)}
                      {volunteerLine("Delivery Dispatch", d.delivery?.volunteer)}
                      
                      {d.delivery && (
                        <div style={{ marginTop: 'auto', paddingTop: '1.5rem' }}>
                          <Link to={`/deliveries/${d.delivery.id}`} style={{ textDecoration: 'none' }}>
                            <button className="secondary" style={{ width: '100%', background: '#f8fafc', color: '#0f766e', border: '1px solid #ccfbf1', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                              View delivery details <ArrowRight size={16} />
                            </button>
                          </Link>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Sidebar: Widgets */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            <div className="widget-panel">
              <div className="widget-title"><Activity size={18} /> Donation Stats</div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: '#f8fafc', borderRadius: '0.75rem' }}>
                <div style={{ color: '#475569', fontWeight: 600 }}>Active Items</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f766e' }}>{activeDonationsCount}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: '#f8fafc', borderRadius: '0.75rem', marginTop: '0.75rem' }}>
                <div style={{ color: '#475569', fontWeight: 600 }}>Total Donated</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f59e0b' }}>{data?.length || 0}</div>
              </div>
            </div>

            <div className="widget-panel">
              <div className="widget-title"><Package size={18} /> Quick Filters</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                <span style={{ padding: '0.4rem 0.8rem', background: '#f1f5f9', color: '#475569', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}>All</span>
                <span style={{ padding: '0.4rem 0.8rem', background: '#ccfbf1', color: '#0f766e', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}>Pending</span>
                <span style={{ padding: '0.4rem 0.8rem', background: '#fef3c7', color: '#b45309', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}>In Transit</span>
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
