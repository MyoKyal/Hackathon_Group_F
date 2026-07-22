import type { ItemCategory } from "../constants/categories";

export type VolunteerStatus = "none" | "pending" | "approved" | "rejected";
export type TransportationType = "walking" | "bicycle" | "motorbike" | "car" | "truck";
export type { ItemCategory };

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string | null;
  is_volunteer: boolean;
  volunteer_status: VolunteerStatus;
  is_available: boolean;
  is_admin: boolean;
  transportation_type?: TransportationType | null;
  max_carrying_capacity_kg?: number | null;
  max_travel_distance_km?: number | null;
  township?: string | null;
  full_address?: string | null;
  available_days?: string[] | null;
  available_start_time?: string | null;
  available_end_time?: string | null;
  preferred_categories?: string[] | null;
  completed_deliveries: number;
  active_deliveries: number;
  reliability_rating: number;
  avg_delivery_time_minutes?: number | null;
}

export interface VolunteerApplyPayload {
  lat: number;
  lng: number;
  transportation_type: TransportationType;
  max_travel_distance_km: number;
  township: string;
  full_address: string;
  available_days: string[];
  available_start_time: string;
  available_end_time: string;
  preferred_categories: string[];
}

export interface Location {
  lat: number;
  lng: number;
}

export interface WarehouseSummary {
  id: string;
  name: string;
  lat: number;
  lng: number;
}

export interface InventoryItem {
  warehouse_id: string;
  warehouse_name: string;
  category: ItemCategory;
  quantity: number;
}

export interface Donation {
  id: string;
  donor_id: string;
  item_name: string;
  item_category: ItemCategory;
  description?: string | null;
  quantity: number;
  weight_kg: number;
  pickup_lat: number;
  pickup_lng: number;
  target_receiver_id?: string | null;
  status: string;
  warehouse: WarehouseSummary;
  pickup_status: string;
  pickup_volunteer_id?: string | null;
  pickup_stage1_score?: number | null;
  pickup_gemini_reasoning?: string | null;
  pickup_volunteer_confirmed: boolean;
  pickup_completed_at?: string | null;
  created_at: string;
  delivery?: Delivery | null;
}

export interface ReceiverRequest {
  id: string;
  requester_id: string;
  item_name: string;
  item_category: ItemCategory;
  description?: string | null;
  quantity_needed: number;
  lat: number;
  lng: number;
  status: string;
  created_at: string;
}

export interface DonationBrowseItem extends Donation {
  donor_name: string;
}

export interface RequestBrowseItem extends ReceiverRequest {
  requester_name: string;
}

export interface Delivery {
  id: string;
  donation_id: string;
  receiver_request_id?: string | null;
  receiver_id: string;
  volunteer_id?: string | null;
  stage1_score?: number | null;
  gemini_reasoning?: string | null;
  status: string;
  volunteer_confirmed: boolean;
  receiver_confirmed: boolean;
  created_at: string;
  completed_at?: string | null;
}

export interface MatchPreview {
  request_id: string;
  requester_name: string;
  item_name: string;
  quantity_needed: number;
  distance_km: number;
  score: number;
}

export interface Assignment {
  id: string;
  leg: "pickup" | "delivery";
  status: string;
  volunteer_id?: string | null;
  is_current_offer: boolean;
  donation: {
    id: string;
    item_name: string;
    item_category: ItemCategory;
    quantity: number;
    pickup_lat: number;
    pickup_lng: number;
  };
  receiver?: {
    id: string;
    full_name: string;
  } | null;
  warehouse?: WarehouseSummary | null;
  stage1_score?: number | null;
  gemini_reasoning?: string | null;
  volunteer_confirmed: boolean;
  receiver_confirmed?: boolean | null;
  created_at: string;
}

export interface DeliveryDetail extends Delivery {
  donation: Assignment["donation"];
  receiver: { id: string; full_name: string };
}

export interface MatchProposal {
  id: string;
  donation_id: string;
  receiver_request_id?: string | null;
  receiver_id: string;
  stage1_score?: number | null;
  gemini_reasoning?: string | null;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  donation: Assignment["donation"];
  receiver: { id: string; full_name: string };
}

export interface AppSettings {
  require_match_approval: boolean;
}

export interface MatchCard {
  id: string;
  status: string;
  created_at: string;
  stage1_score?: number | null;
  gemini_reasoning?: string | null;
  donation_item_name: string;
  donation_quantity: number;
  donor_name: string;
  request_item_name?: string | null;
  request_quantity_needed?: number | null;
  receiver_name: string;
}

export interface RoutePoint {
  lat: number;
  lng: number;
  label: string;
}

export interface RouteInfo {
  leg: "pickup" | "delivery";
  volunteer_id?: string | null;
  volunteer_name?: string | null;
  waypoints: RoutePoint[];
  geometry: [number, number][] | null;
  distance_km?: number | null;
  duration_min?: number | null;
  routed: boolean;
}
