import { useState } from "react";
import type { Location } from "../../types";
import { ITEM_CATEGORIES, ITEM_CATEGORY_LABELS, type ItemCategory } from "../../constants/categories";
import { LocationPicker } from "./LocationPicker";

export interface RequestFormValues {
  item_name: string;
  item_category: ItemCategory | "";
  description: string;
  quantity_needed: number;
  location: Location;
}

interface Props {
  onSubmit: (values: RequestFormValues) => void;
  submitting?: boolean;
}

export function RequestForm({ onSubmit, submitting }: Props) {
  const [values, setValues] = useState<RequestFormValues>({
    item_name: "",
    item_category: "",
    description: "",
    quantity_needed: 1,
    location: { lat: 0, lng: 0 },
  });

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
        Quantity needed
        <input
          type="number"
          min={1}
          required
          value={values.quantity_needed}
          onChange={(e) => setValues({ ...values, quantity_needed: parseInt(e.target.value, 10) })}
        />
      </label>
      <LocationPicker
        value={values.location}
        onChange={(location) => setValues({ ...values, location })}
      />
      <button type="submit" disabled={submitting}>
        {submitting ? "Submitting..." : "Submit request"}
      </button>
    </form>
  );
}
