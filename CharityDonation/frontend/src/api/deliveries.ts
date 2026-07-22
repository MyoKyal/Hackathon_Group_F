import { apiRequest, apiUpload } from "./client";
import type { Delivery, DeliveryDetail, MatchCard } from "../types";

export function listMatches() {
  return apiRequest<MatchCard[]>("/deliveries");
}

export function getDelivery(id: string) {
  return apiRequest<DeliveryDetail>(`/deliveries/${id}`);
}

export function confirmVolunteer(deliveryId: string) {
  return apiRequest<Delivery>(`/deliveries/${deliveryId}/confirm-volunteer`, {
    method: "POST",
  });
}

export function confirmReceiver(deliveryId: string, photo: File) {
  const formData = new FormData();
  formData.append("photo", photo);
  return apiUpload<Delivery>(`/deliveries/${deliveryId}/confirm-receiver`, formData);
}
