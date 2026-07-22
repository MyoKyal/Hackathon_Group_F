import { apiRequest } from "./client";
import type { RouteInfo } from "../types";

export function getPickupRoute(donationId: string) {
  return apiRequest<RouteInfo>(`/donations/${donationId}/route`);
}

export function getDeliveryRoute(deliveryId: string) {
  return apiRequest<RouteInfo>(`/deliveries/${deliveryId}/route`);
}
