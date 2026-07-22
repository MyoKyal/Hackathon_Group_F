import { apiRequest } from "./client";
import type { Assignment, Delivery, User, VolunteerStatus } from "../types";

export function applyVolunteer() {
  return apiRequest<{ volunteer_status: VolunteerStatus }>("/volunteers/apply", {
    method: "POST",
  });
}

export function approveVolunteer(userId: string) {
  return apiRequest<User>(`/volunteers/${userId}/approve`, { method: "POST" });
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
