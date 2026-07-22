import { apiRequest } from "./client";
import type { User } from "../types";

export interface SignupPayload {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SignupResponse extends User {
  access_token: string;
  token_type: string;
}

export function signup(payload: SignupPayload) {
  return apiRequest<SignupResponse>("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function login(email: string, password: string) {
  return apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function logout() {
  return apiRequest<void>("/auth/logout", { method: "POST" });
}

export function getMe() {
  return apiRequest<User>("/auth/me");
}
