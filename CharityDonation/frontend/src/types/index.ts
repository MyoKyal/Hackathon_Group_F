export type VolunteerStatus = "none" | "pending" | "approved" | "rejected";

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string | null;
  is_volunteer: boolean;
  volunteer_status: VolunteerStatus;
  is_available: boolean;
}

export interface Location {
  lat: number;
  lng: number;
}

export interface Donation {
  id: string;
  donor_id: string;
  item_name: string;
  item_category: string;
  description?: string | null;
  quantity: number;
  pickup_lat: number;
  pickup_lng: number;
  target_receiver_id?: string | null;
  status: string;
  created_at: string;
  delivery?: Delivery | null;
}

export interface ReceiverRequest {
  id: string;
  requester_id: string;
  item_name: string;
  item_category: string;
  description?: string | null;
  quantity_needed: number;
  lat: number;
  lng: number;
  status: string;
  created_at: string;
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
  distance_km: number;
  score: number;
}

export interface Assignment {
  id: string;
  status: string;
  volunteer_id?: string | null;
  is_current_offer: boolean;
  donation: {
    id: string;
    item_name: string;
    item_category: string;
    quantity: number;
    pickup_lat: number;
    pickup_lng: number;
  };
  receiver: {
    id: string;
    full_name: string;
  };
  stage1_score?: number | null;
  gemini_reasoning?: string | null;
  volunteer_confirmed: boolean;
  receiver_confirmed: boolean;
  created_at: string;
}

export interface DeliveryDetail extends Delivery {
  donation: Assignment["donation"];
  receiver: Assignment["receiver"];
}
