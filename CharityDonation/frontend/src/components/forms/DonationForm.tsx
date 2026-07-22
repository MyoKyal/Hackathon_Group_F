import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { Location, MatchPreview } from "../../types";
import { ITEM_CATEGORIES, ITEM_CATEGORY_LABELS, type ItemCategory } from "../../constants/categories";
import { previewMatches } from "../../api/donations";
import { LocationPicker } from "./LocationPicker";

export interface DonationFormValues {
  item_name: string;
  item_category: ItemCategory | "";
  description: string;
  quantity: number;
  weight_kg: number;
  pickup_location: Location;
  target_receiver_id: string | null;
}

interface Props {
  onSubmit: (values: DonationFormValues) => void;
  submitting?: boolean;
}

function useDebounced<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export function DonationForm({ onSubmit, submitting }: Props) {
  const [values, setValues] = useState<DonationFormValues>({
    item_name: "",
    item_category: "",
    description: "",
    quantity: 1,
    weight_kg: 1,
    pickup_location: { lat: 0, lng: 0 },
    target_receiver_id: null,
  });
  const [targetReceiver, setTargetReceiver] = useState(false);
  const [selected, setSelected] = useState<MatchPreview | null>(null);

  const debounced = useDebounced(values, 500);

  const canPreview =
    targetReceiver &&
    !!debounced.item_name &&
    !!debounced.item_category &&
    !!debounced.pickup_location.lat &&
    !!debounced.pickup_location.lng;

  const { data: matches, isFetching } = useQuery({
    queryKey: ["donation-matches", debounced],
    queryFn: () =>
      previewMatches({
        item_name: debounced.item_name,
        item_category: debounced.item_category,
        description: debounced.description || undefined,
        quantity: debounced.quantity,
        lat: debounced.pickup_location.lat,
        lng: debounced.pickup_location.lng,
      }),
    enabled: canPreview,
  });

  function selectMatch(m: MatchPreview) {
    setSelected(m);
    setValues({ ...values, target_receiver_id: m.request_id });
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(values);
      }}
    >
      <label>
        Item name
        <input
          required
          value={values.item_name}
          onChange={(e) => setValues({ ...values, item_name: e.target.value })}
        />
      </label>
      <label>
        Category
        <select
          required
          value={values.item_category}
          onChange={(e) => setValues({ ...values, item_category: e.target.value as ItemCategory })}
        >
          <option value="" disabled>
            Select a category
          </option>
          {ITEM_CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {ITEM_CATEGORY_LABELS[c]}
            </option>
          ))}
        </select>
      </label>
      <label>
        Description
        <textarea
          value={values.description}
          onChange={(e) => setValues({ ...values, description: e.target.value })}
        />
      </label>
      <label>
        Quantity
        <input
          type="number"
          min={1}
          required
          value={values.quantity}
          onChange={(e) => setValues({ ...values, quantity: parseInt(e.target.value, 10) })}
        />
      </label>
      <label>
        Weight (kg)
        <input
          type="number"
          min={0.1}
          step={0.1}
          required
          value={values.weight_kg}
          onChange={(e) => setValues({ ...values, weight_kg: parseFloat(e.target.value) })}
        />
      </label>
      <LocationPicker
        value={values.pickup_location}
        onChange={(pickup_location) => setValues({ ...values, pickup_location })}
      />
      <label style={{ flexDirection: "row", alignItems: "center" }}>
        <input
          type="checkbox"
          checked={targetReceiver}
          onChange={(e) => {
            setTargetReceiver(e.target.checked);
            if (!e.target.checked) {
              setSelected(null);
              setValues({ ...values, target_receiver_id: null });
            }
          }}
        />
        Target a specific receiver
      </label>

      {targetReceiver && (
        <div>
          {isFetching && <p className="muted">Searching for matches...</p>}
          {matches && matches.length === 0 && (
            <p className="muted">No matching requests found — this donation will enter the general pool.</p>
          )}
          {matches && matches.length > 0 && (
            <div>
              <p className="muted">Select a matching request:</p>
              {matches.map((m) => (
                <div
                  key={m.request_id}
                  className={`card selectable ${selected?.request_id === m.request_id ? "selected" : ""}`}
                  onClick={() => selectMatch(m)}
                >
                  <strong>{m.item_name}</strong> — requested by {m.requester_name}
                  <div className="muted">
                    needs {m.quantity_needed} · {m.distance_km.toFixed(1)} km away · score {m.score.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <button type="submit" disabled={submitting}>
        {submitting ? "Submitting..." : "Submit donation"}
      </button>
    </form>
  );
}
