import { apiRequest } from "./client";
import type { Donation, Location, MatchPreview } from "../types";

export interface CreateDonationPayload {
  item_name: string;
  item_category: string;
  description?: string;
  quantity: number;
  pickup_location: Location;
  target_receiver_id?: string | null;
}

export function createDonation(payload: CreateDonationPayload) {
  return apiRequest<Donation>("/donations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listDonations() {
  return apiRequest<Donation[]>("/donations");
}

export function getDonation(id: string) {
  return apiRequest<Donation>(`/donations/${id}`);
}

export function previewMatches(params: {
  item_name: string;
  item_category: string;
  description?: string;
  lat: number;
  lng: number;
}) {
  const query = new URLSearchParams({
    item_name: params.item_name,
    item_category: params.item_category,
    lat: String(params.lat),
    lng: String(params.lng),
  });
  if (params.description) {
    query.set("description", params.description);
  }
  return apiRequest<MatchPreview[]>(`/donations/matches?${query.toString()}`);
}
