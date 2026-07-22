import { apiRequest } from "./client";
import type { Delivery, DeliveryDetail } from "../types";

export function getDelivery(id: string) {
  return apiRequest<DeliveryDetail>(`/deliveries/${id}`);
}

export function confirmVolunteer(deliveryId: string) {
  return apiRequest<Delivery>(`/deliveries/${deliveryId}/confirm-volunteer`, {
    method: "POST",
  });
}

export function confirmReceiver(deliveryId: string) {
  return apiRequest<Delivery>(`/deliveries/${deliveryId}/confirm-receiver`, {
    method: "POST",
  });
}
