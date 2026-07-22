import { apiRequest } from "./client";
import type { InventoryItem } from "../types";

export function listInventory() {
  return apiRequest<InventoryItem[]>("/admin/inventory");
}
