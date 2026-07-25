import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { RequestForm, type RequestFormValues } from "../components/forms/RequestForm";
import { createRequest } from "../api/requests";
import { ApiError } from "../api/client";
import { useState } from "react";

export default function RequestPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (values: RequestFormValues) =>
      createRequest({
        item_name: values.item_name,
        item_category: values.item_category,
        description: values.description || undefined,
        quantity_needed: values.quantity_needed,
        location: values.location,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["requests"] });
      navigate("/requests/me");
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to submit request"),
  });

  return (
    <div className="container">
      <h1>Request an item</h1>
      {error && <div className="error">{error}</div>}
      <RequestForm onSubmit={(v) => mutation.mutate(v)} submitting={mutation.isPending} />
    </div>
  );
}
