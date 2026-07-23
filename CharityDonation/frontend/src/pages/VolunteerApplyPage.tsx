import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { applyVolunteer } from "../api/volunteers";
import { ApiError } from "../api/client";
import { LocationPicker } from "../components/forms/LocationPicker";
import type { Location, TransportationType, VolunteerApplyPayload } from "../types";
import { HeartHandshake, Car, Route, MapPin, Clock, List, Loader2 } from "lucide-react";

const TRANSPORT_OPTIONS: { value: TransportationType; label: string }[] = [
  { value: "walking", label: "Walking (up to 10 kg)" },
  { value: "bicycle", label: "Bicycle (up to 25 kg)" },
  { value: "motorbike", label: "Motorbike (up to 70 kg)" },
  { value: "car", label: "Car (up to 300 kg)" },
  { value: "truck", label: "Truck (unlimited)" },
];

const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];

const CATEGORY_OPTIONS = [
  "Food",
  "Medicine",
  "Clothing",
  "Books",
  "School Supplies",
  "Furniture",
  "Electronics",
];

interface FormState {
  location: Location;
  transportation_type: TransportationType;
  max_travel_distance_km: number;
  township: string;
  full_address: string;
  available_days: string[];
  available_start_time: string;
  available_end_time: string;
  preferred_categories: string[];
}

const INITIAL_STATE: FormState = {
  location: { lat: 0, lng: 0 },
  transportation_type: "motorbike",
  max_travel_distance_km: 10,
  township: "",
  full_address: "",
  available_days: [],
  available_start_time: "09:00",
  available_end_time: "18:00",
  preferred_categories: [],
};

export default function VolunteerApplyPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [applied, setApplied] = useState(false);
  const [form, setForm] = useState<FormState>(INITIAL_STATE);

  const mutation = useMutation({
    mutationFn: () => {
      const payload: VolunteerApplyPayload = {
        lat: form.location.lat,
        lng: form.location.lng,
        transportation_type: form.transportation_type,
        max_travel_distance_km: form.max_travel_distance_km,
        township: form.township,
        full_address: form.full_address,
        available_days: form.available_days,
        available_start_time: form.available_start_time,
        available_end_time: form.available_end_time,
        preferred_categories: form.preferred_categories,
      };
      return applyVolunteer(payload);
    },
    onSuccess: () => {
      setApplied(true);
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to apply"),
  });

  const status = user?.volunteer_status ?? "none";

  function toggleDay(day: string) {
    setForm((f) => ({
      ...f,
      available_days: f.available_days.includes(day)
        ? f.available_days.filter((d) => d !== day)
        : [...f.available_days, day],
    }));
  }

  function toggleCategory(category: string) {
    setForm((f) => ({
      ...f,
      preferred_categories: f.preferred_categories.includes(category)
        ? f.preferred_categories.filter((c) => c !== category)
        : [...f.preferred_categories, category],
    }));
  }

  const canSubmit =
    form.township.trim() !== "" &&
    form.full_address.trim() !== "" &&
    form.available_days.length > 0 &&
    form.max_travel_distance_km > 0;

  return (
    <div className="auth-page">
      <div className="auth-hero" style={{ padding: '0', background: 'transparent' }}>
        <div className="auth-form-container" style={{ width: '100%', maxWidth: '800px', margin: '0 auto', padding: '2rem 1rem' }}>
          <div className="auth-card" style={{ maxWidth: '100%' }}>
            
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
              <HeartHandshake size={48} color="var(--primary)" />
            </div>
            
            <h1 style={{ textAlign: 'center' }}>Become a Volunteer</h1>
            <p className="auth-subtitle" style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto 2rem auto' }}>
              Join our network of community heroes. Help transport donations to those who need them most.
            </p>

            {status === "approved" && <div className="error" style={{ background: '#dcfce7', color: '#166534', borderColor: '#bbf7d0', marginBottom: '2rem' }}>You're already an approved volunteer!</div>}
            {status === "pending" && <div className="error" style={{ background: '#fef3c7', color: '#92400e', borderColor: '#fde68a', marginBottom: '2rem' }}>Your application is pending approval.</div>}
            {status === "rejected" && <div className="error" style={{ marginBottom: '2rem' }}>Your application was rejected.</div>}
            
            {(status === "none" || (status === "rejected" && !applied)) && !applied && (
              <form onSubmit={(e) => e.preventDefault()}>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
                  <label>
                    Transportation type
                    <div className="input-wrapper">
                      <Car className="input-icon" size={20} />
                      <select
                        value={form.transportation_type}
                        onChange={(e) =>
                          setForm({ ...form, transportation_type: e.target.value as TransportationType })
                        }
                      >
                        {TRANSPORT_OPTIONS.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </label>

                  <label>
                    Maximum travel distance (km)
                    <div className="input-wrapper">
                      <Route className="input-icon" size={20} />
                      <input
                        type="number"
                        min={1}
                        required
                        value={form.max_travel_distance_km}
                        onChange={(e) =>
                          setForm({ ...form, max_travel_distance_km: parseFloat(e.target.value) })
                        }
                      />
                    </div>
                  </label>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
                  <label>
                    Township
                    <div className="input-wrapper">
                      <MapPin className="input-icon" size={20} />
                      <input
                        required
                        placeholder="E.g., Downtown"
                        value={form.township}
                        onChange={(e) => setForm({ ...form, township: e.target.value })}
                      />
                    </div>
                  </label>

                  <label>
                    Full address
                    <div className="input-wrapper">
                      <MapPin className="input-icon" size={20} />
                      <input
                        required
                        placeholder="123 Main Street"
                        value={form.full_address}
                        onChange={(e) => setForm({ ...form, full_address: e.target.value })}
                      />
                    </div>
                  </label>
                </div>

                <fieldset style={{ border: 'none', padding: 0, margin: '1rem 0' }}>
                  <legend style={{ fontWeight: 600, color: '#334155', marginBottom: '0.5rem' }}>Available days</legend>
                  <div className="pill-grid">
                    {DAYS.map((day) => (
                      <label key={day} className="pill-label">
                        <input
                          type="checkbox"
                          checked={form.available_days.includes(day)}
                          onChange={() => toggleDay(day)}
                        />
                        <span>{day}</span>
                      </label>
                    ))}
                  </div>
                </fieldset>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                  <label>
                    Available from
                    <div className="input-wrapper">
                      <Clock className="input-icon" size={20} />
                      <input
                        type="time"
                        required
                        value={form.available_start_time}
                        onChange={(e) => setForm({ ...form, available_start_time: e.target.value })}
                      />
                    </div>
                  </label>

                  <label>
                    Available until
                    <div className="input-wrapper">
                      <Clock className="input-icon" size={20} />
                      <input
                        type="time"
                        required
                        value={form.available_end_time}
                        onChange={(e) => setForm({ ...form, available_end_time: e.target.value })}
                      />
                    </div>
                  </label>
                </div>

                <fieldset style={{ border: 'none', padding: 0, margin: '1rem 0' }}>
                  <legend style={{ fontWeight: 600, color: '#334155', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <List size={18} /> Preferred donation categories (optional)
                  </legend>
                  <div className="pill-grid-auto">
                    {CATEGORY_OPTIONS.map((category) => (
                      <label key={category} className="pill-label">
                        <input
                          type="checkbox"
                          checked={form.preferred_categories.includes(category)}
                          onChange={() => toggleCategory(category)}
                        />
                        <span>{category}</span>
                      </label>
                    ))}
                  </div>
                </fieldset>

                <div style={{ margin: '1rem 0' }}>
                  <span style={{ fontWeight: 600, color: '#334155', marginBottom: '0.5rem', display: 'block' }}>Base Location</span>
                  <div style={{ borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border)' }}>
                    <LocationPicker
                      value={form.location}
                      onChange={(location) => setForm({ ...form, location })}
                    />
                  </div>
                </div>

                {error && <div className="error">{error}</div>}
                
                <button
                  onClick={() => mutation.mutate()}
                  disabled={mutation.isPending || !canSubmit}
                  style={{ width: '100%', marginTop: '1.5rem', padding: '1rem', fontSize: '1.1rem' }}
                >
                  {mutation.isPending ? (
                    <>
                      <Loader2 size={24} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                      Submitting Application...
                    </>
                  ) : (
                    "Submit Application"
                  )}
                </button>
              </form>
            )}
            
            {applied && (
              <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <HeartHandshake size={64} color="var(--primary)" style={{ margin: '0 auto 1rem auto' }} />
                <h2 style={{ color: '#0f172a' }}>Application Submitted!</h2>
                <p className="muted" style={{ fontSize: '1.1rem' }}>Thank you for volunteering. We are reviewing your application and will notify you once approved.</p>
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
}
