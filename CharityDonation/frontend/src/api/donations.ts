import { apiRequest } from "./client";
import type { Donation, DonationBrowseItem, Location, MatchPreview } from "../types";

export interface CreateDonationPayload {
  item_name: string;
  item_category: string;
  description?: string;
  quantity: number;
  weight_kg: number;
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

export function listAllDonations() {
  return apiRequest<DonationBrowseItem[]>("/donations/all");
}

export function previewMatches(params: {
  item_name: string;
  item_category: string;
  description?: string;
  quantity: number;
  lat: number;
  lng: number;
}) {
  const query = new URLSearchParams({
    item_name: params.item_name,
    item_category: params.item_category,
    quantity: String(params.quantity),
    lat: String(params.lat),
    lng: String(params.lng),
  });
  if (params.description) {
    query.set("description", params.description);
  }
  return apiRequest<MatchPreview[]>(`/donations/matches?${query.toString()}`);
}
