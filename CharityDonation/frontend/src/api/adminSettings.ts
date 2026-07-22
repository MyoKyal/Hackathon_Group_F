import { apiRequest } from "./client";
import type { AppSettings } from "../types";

export function getSettings() {
  return apiRequest<AppSettings>("/admin/settings");
}

export function updateSettings(payload: AppSettings) {
  return apiRequest<AppSettings>("/admin/settings", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
