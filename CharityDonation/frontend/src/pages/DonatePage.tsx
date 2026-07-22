import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { DonationForm, type DonationFormValues } from "../components/forms/DonationForm";
import { createDonation } from "../api/donations";
import { ApiError } from "../api/client";

export default function DonatePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (values: DonationFormValues) =>
      createDonation({
        item_name: values.item_name,
        item_category: values.item_category,
        description: values.description || undefined,
        quantity: values.quantity,
        weight_kg: values.weight_kg,
        pickup_location: values.pickup_location,
        target_receiver_id: values.target_receiver_id,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["donations"] });
      navigate("/my-donations");
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to submit donation"),
  });

  return (
    <div className="container">
      <h1>Donate an item</h1>
      {error && <div className="error">{error}</div>}
      <DonationForm onSubmit={(v) => mutation.mutate(v)} submitting={mutation.isPending} />
    </div>
  );
}
