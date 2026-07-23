import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { confirmReceiver, confirmVolunteer, getDelivery } from "../api/deliveries";
import { getDeliveryRoute } from "../api/routes";
import { useAuth } from "../hooks/useAuth";
import { API_URL, ApiError } from "../api/client";
import { RouteMap } from "../components/RouteMap";
import { CheckCircle, XCircle, Map, User, Package, Image as ImageIcon } from "lucide-react";

export default function DeliveryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreviewUrl, setPhotoPreviewUrl] = useState<string | null>(null);

  const { data: delivery, isLoading } = useQuery({
    queryKey: ["delivery", id],
    queryFn: () => getDelivery(id!),
    enabled: !!id,
  });

  const { data: route } = useQuery({
    queryKey: ["delivery-route", id],
    queryFn: () => getDeliveryRoute(id!),
    enabled: !!id,
    retry: false,
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["delivery", id] });
    queryClient.invalidateQueries({ queryKey: ["assignments"] });
  };

  const volunteerConfirm = useMutation({
    mutationFn: () => confirmVolunteer(id!),
    onSuccess: invalidate,
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to confirm"),
  });

  const receiverConfirm = useMutation({
    mutationFn: (photo: File) => confirmReceiver(id!, photo),
    onSuccess: () => {
      setPhotoFile(null);
      setPhotoPreviewUrl(null);
      invalidate();
    },
    onError: (err) => {
      if (err instanceof ApiError && err.code === "photo_mismatch") {
        setError(`${err.message} Please take a new photo and try again.`);
        setPhotoFile(null);
        setPhotoPreviewUrl(null);
      } else {
        setError(err instanceof ApiError ? err.message : "Failed to confirm");
      }
    },
  });

  function handlePhotoSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;
    setPhotoFile(file);
    setPhotoPreviewUrl(file ? URL.createObjectURL(file) : null);
  }

  // Helper for status badge
  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "in_transit":
      case "pending":
        return "badge-pending";
      case "completed":
      case "delivered":
        return "badge-completed";
      default:
        return "badge-active";
    }
  };

  if (isLoading) return <div className="container" style={{ textAlign: 'center', padding: '3rem' }}><div className="muted">Loading delivery details...</div></div>;
  if (!delivery) return <div className="container" style={{ textAlign: 'center', padding: '3rem' }}>Delivery not found.</div>;

  const isVolunteer = delivery.volunteer_id === user?.id;
  const isReceiver = delivery.receiver_id === user?.id;

  return (
    <div style={{ background: '#f8fafc', minHeight: 'calc(100vh - 64px)', padding: '2rem 1rem' }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em', marginBottom: '1.5rem' }}>
          Delivery detail
        </h1>
        
        {error && <div className="error">{error}</div>}
        
        {/* Summary Card */}
        <div className="dashboard-card" style={{ padding: '1.5rem', marginBottom: '1.5rem', border: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
                <strong style={{ fontSize: '1.25rem', color: '#0f172a' }}>{delivery.donation.item_name}</strong>
                <span className="qty-badge">qty {delivery.donation.quantity}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#64748b' }}>
                <User size={16} /> Receiver: <strong style={{ color: '#334155' }}>{delivery.receiver.full_name}</strong>
              </div>
            </div>
            
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '0.25rem' }}>Status</div>
              <span className={`badge ${getStatusBadge(delivery.status)}`} style={{ textTransform: 'uppercase' }}>
                {delivery.status.replace("_", " ")}
              </span>
            </div>
          </div>
          
          <hr style={{ border: 'none', borderTop: '1px solid #f1f5f9', margin: '1.25rem 0' }} />
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {delivery.donation.pickup_volunteer && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#475569', fontSize: '0.95rem' }}>
                <Package size={16} color="#94a3b8" />
                Picked up from donor by: <strong>{delivery.donation.pickup_volunteer.full_name}</strong> 
                <span className="muted">({delivery.donation.pickup_volunteer.status === "accepted" ? "accepted" : "pending"})</span>
              </div>
            )}
            
            {delivery.volunteer && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#475569', fontSize: '0.95rem' }}>
                <Package size={16} color="#94a3b8" />
                Delivering to receiver: <strong>{delivery.volunteer.full_name}</strong>
                <span className="muted">({delivery.volunteer.status === "accepted" ? "accepted" : "pending"})</span>
              </div>
            )}
          </div>

          {delivery.gemini_reasoning && (
            <div style={{ background: '#f8fafc', padding: '0.75rem 1rem', borderRadius: '0.5rem', fontSize: '0.9rem', color: '#475569', marginTop: '1.25rem', borderLeft: '3px solid #cbd5e1' }}>
              {delivery.gemini_reasoning}
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: '#f1f5f9', padding: '0.4rem 0.8rem', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600, color: '#475569' }}>
              {delivery.volunteer_confirmed ? <CheckCircle size={14} color="#10b981" /> : <XCircle size={14} color="#94a3b8" />}
              VOLUNTEER CONFIRMED: {delivery.volunteer_confirmed ? "YES" : "NO"}
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: '#f1f5f9', padding: '0.4rem 0.8rem', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600, color: '#475569' }}>
              {delivery.receiver_confirmed ? <CheckCircle size={14} color="#10b981" /> : <XCircle size={14} color="#94a3b8" />}
              RECEIVER CONFIRMED: {delivery.receiver_confirmed ? "YES" : "NO"}
            </span>
          </div>

          {isVolunteer && !delivery.volunteer_confirmed && delivery.status === "in_transit" && (
            <div style={{ marginTop: "1.5rem" }}>
              <button
                className="btn-indigo"
                onClick={() => volunteerConfirm.mutate()}
                disabled={volunteerConfirm.isPending}
              >
                Mark delivered (volunteer)
              </button>
            </div>
          )}

          {isReceiver && !delivery.receiver_confirmed && delivery.status === "in_transit" && (
            <div style={{ marginTop: "1.5rem", background: '#f8fafc', padding: '1.5rem', borderRadius: '1rem', border: '1px dashed #cbd5e1' }}>
              <label style={{ display: 'block', fontWeight: 600, color: '#334155', marginBottom: '0.75rem' }}>
                <ImageIcon size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'text-bottom' }} />
                Photo of what you received
              </label>
              
              <div className="input-wrapper" style={{ display: 'block' }}>
                <input 
                  type="file" 
                  accept="image/jpeg,image/png,image/webp" 
                  onChange={handlePhotoSelected} 
                  style={{ width: '100%', padding: '0.75rem', background: 'white', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}
                />
              </div>

              {photoPreviewUrl && (
                <div style={{ marginTop: '1rem' }}>
                  <img
                    src={photoPreviewUrl}
                    alt="Preview of received item"
                    style={{ width: '100%', maxWidth: '300px', borderRadius: '0.75rem', display: "block", boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                  />
                </div>
              )}
              
              <button
                className="btn-emerald"
                style={{ marginTop: "1.25rem" }}
                onClick={() => photoFile && receiverConfirm.mutate(photoFile)}
                disabled={!photoFile || receiverConfirm.isPending}
              >
                {receiverConfirm.isPending ? "Confirming..." : "Confirm received"}
              </button>
            </div>
          )}

          {delivery.receiver_photo_path && (
            <div style={{ marginTop: "1.5rem", padding: '1rem', background: '#f8fafc', borderRadius: '1rem' }}>
              <div style={{ fontWeight: 600, color: '#475569', marginBottom: '0.75rem' }}>Photo submitted by receiver:</div>
              <img
                src={`${API_URL}/uploads/${delivery.receiver_photo_path}`}
                alt="Item received by recipient"
                style={{ width: '100%', maxWidth: '300px', borderRadius: '0.75rem', display: "block", boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
              />
              
              {delivery.photo_match !== null && delivery.photo_match !== undefined && (
                <div style={{ marginTop: "1rem" }}>
                  <span
                    style={{ 
                      display: 'inline-flex', alignItems: 'center', gap: '0.35rem',
                      background: delivery.photo_match ? '#dcfce7' : '#fee2e2', 
                      color: delivery.photo_match ? '#166534' : '#dc2626',
                      padding: '0.4rem 0.8rem', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600 
                    }}
                  >
                    {delivery.photo_match ? <CheckCircle size={14} /> : <XCircle size={14} />}
                    AI check: {delivery.photo_match ? "verified match" : "flagged mismatch"}
                  </span>
                </div>
              )}
              
              {(delivery.photo_match === null || delivery.photo_match === undefined) && (
                <p className="muted" style={{ marginTop: "0.75rem", fontSize: '0.9rem' }}>
                  AI verification was unavailable when this was submitted.
                </p>
              )}
              
              {delivery.photo_verification_reasoning && (
                <div style={{ background: 'white', padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.9rem', color: '#475569', marginTop: '0.75rem', border: '1px solid #e2e8f0' }}>
                  {delivery.photo_verification_reasoning}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Route Map Card */}
        {route && (
          <div className="dashboard-card" style={{ padding: '1.5rem', border: '1px solid #f1f5f9' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <Map size={20} color="#0f172a" />
              <strong style={{ fontSize: '1.15rem', color: '#0f172a' }}>Route: warehouse &rarr; receiver</strong>
            </div>
            
            <div style={{ marginTop: "0.5rem" }}>
              <RouteMap route={route} />
            </div>
          </div>
        )}
        
      </div>
    </div>
  );
}
