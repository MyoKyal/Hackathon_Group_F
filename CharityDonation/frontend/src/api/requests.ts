import { apiRequest } from "./client";
import type { Location, ReceiverRequest, RequestBrowseItem } from "../types";

export interface CreateRequestPayload {
  item_name: string;
  item_category: string;
  description?: string;
  quantity_needed: number;
  location: Location;
}

export function createRequest(payload: CreateRequestPayload) {
  return apiRequest<ReceiverRequest>("/requests", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listRequests() {
  return apiRequest<ReceiverRequest[]>("/requests");
}

export function getRequest(id: string) {
  return apiRequest<ReceiverRequest>(`/requests/${id}`);
}

export function listAllRequests() {
  return apiRequest<RequestBrowseItem[]>("/requests/all");
}

export function updateRequest(
  id: string,
  payload: Partial<{ description: string; quantity_needed: number; status: string }>,
) {
  return apiRequest<ReceiverRequest>(`/requests/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
