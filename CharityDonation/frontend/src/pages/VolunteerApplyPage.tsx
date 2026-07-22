import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { applyVolunteer } from "../api/volunteers";
import { ApiError } from "../api/client";
import { LocationPicker } from "../components/forms/LocationPicker";
import type { Location, TransportationType, VolunteerApplyPayload } from "../types";

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
    <div className="container">
      <h1>Become a Volunteer</h1>
      {status === "approved" && <p>You're already an approved volunteer.</p>}
      {status === "pending" && <p className="muted">Your application is pending approval.</p>}
      {status === "rejected" && <p className="error">Your application was rejected.</p>}
      {(status === "none" || (status === "rejected" && !applied)) && !applied && (
        <>
          <p className="muted">
            Apply to become a volunteer to help transport donations to receivers.
          </p>

          <label>
            Transportation type
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
          </label>

          <label>
            Maximum travel distance (km)
            <input
              type="number"
              min={1}
              required
              value={form.max_travel_distance_km}
              onChange={(e) =>
                setForm({ ...form, max_travel_distance_km: parseFloat(e.target.value) })
              }
            />
          </label>

          <label>
            Township
            <input
              required
              value={form.township}
              onChange={(e) => setForm({ ...form, township: e.target.value })}
            />
          </label>

          <label>
            Full address
            <input
              required
              value={form.full_address}
              onChange={(e) => setForm({ ...form, full_address: e.target.value })}
            />
          </label>

          <fieldset>
            <legend>Available days</legend>
            {DAYS.map((day) => (
              <label key={day} style={{ flexDirection: "row", alignItems: "center" }}>
                <input
                  type="checkbox"
                  checked={form.available_days.includes(day)}
                  onChange={() => toggleDay(day)}
                />
                {day}
              </label>
            ))}
          </fieldset>

          <label>
            Available from
            <input
              type="time"
              required
              value={form.available_start_time}
              onChange={(e) => setForm({ ...form, available_start_time: e.target.value })}
            />
          </label>

          <label>
            Available until
            <input
              type="time"
              required
              value={form.available_end_time}
              onChange={(e) => setForm({ ...form, available_end_time: e.target.value })}
            />
          </label>

          <fieldset>
            <legend>Preferred donation categories (optional)</legend>
            {CATEGORY_OPTIONS.map((category) => (
              <label key={category} style={{ flexDirection: "row", alignItems: "center" }}>
                <input
                  type="checkbox"
                  checked={form.preferred_categories.includes(category)}
                  onChange={() => toggleCategory(category)}
                />
                {category}
              </label>
            ))}
          </fieldset>

          <LocationPicker
            value={form.location}
            onChange={(location) => setForm({ ...form, location })}
          />

          {error && <div className="error">{error}</div>}
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !canSubmit}
          >
            {mutation.isPending ? "Applying..." : "Apply now"}
          </button>
        </>
      )}
      {applied && <p className="muted">Application submitted — awaiting approval.</p>}
    </div>
  );
}
