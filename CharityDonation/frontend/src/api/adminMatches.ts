import { apiRequest } from "./client";
import type { MatchProposal } from "../types";

export function listPendingMatches() {
  return apiRequest<MatchProposal[]>("/admin/matches/pending");
}

export function approveMatch(proposalId: string) {
  return apiRequest<MatchProposal>(`/admin/matches/${proposalId}/approve`, {
    method: "POST",
  });
}

export function rejectMatch(proposalId: string) {
  return apiRequest<MatchProposal>(`/admin/matches/${proposalId}/reject`, {
    method: "POST",
  });
}
