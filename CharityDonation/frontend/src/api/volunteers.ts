import { apiRequest } from "./client";
import type {
  Assignment,
  Delivery,
  Donation,
  User,
  VolunteerApplyPayload,
  VolunteerStatus,
} from "../types";

export function applyVolunteer(payload: VolunteerApplyPayload) {
  const { lat, lng, ...rest } = payload;
  return apiRequest<{ volunteer_status: VolunteerStatus }>("/volunteers/apply", {
    method: "POST",
    body: JSON.stringify({ location: { lat, lng }, ...rest }),
  });
}

export function approveVolunteer(userId: string) {
  return apiRequest<User>(`/volunteers/${userId}/approve`, { method: "POST" });
}

export function revokeVolunteer(userId: string) {
  return apiRequest<User>(`/volunteers/${userId}/revoke`, { method: "POST" });
}

export function listAllUsers() {
  return apiRequest<User[]>("/volunteers/users");
}

export function listAssignments() {
  return apiRequest<Assignment[]>("/volunteers/assignments");
}

export function acceptAssignment(deliveryId: string) {
  return apiRequest<Delivery>(`/volunteers/assignments/${deliveryId}/accept`, {
    method: "POST",
  });
}

export function declineAssignment(deliveryId: string) {
  return apiRequest<Delivery>(`/volunteers/assignments/${deliveryId}/decline`, {
    method: "POST",
  });
}

export function acceptPickup(donationId: string) {
  return apiRequest<Donation>(`/volunteers/pickups/${donationId}/accept`, {
    method: "POST",
  });
}

export function declinePickup(donationId: string) {
  return apiRequest<Donation>(`/volunteers/pickups/${donationId}/decline`, {
    method: "POST",
  });
}

export function confirmPickup(donationId: string) {
  return apiRequest<Donation>(`/volunteers/pickups/${donationId}/confirm`, {
    method: "POST",
  });
}
