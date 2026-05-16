import { api } from "./client";

export interface CurrentUser {
  id: string;
  email: string;
  username: string;
  display_name: string;
  role: "admin" | "user";
}

export function login(email: string, password: string) {
  return api<{ user: CurrentUser }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function logout() {
  return api<void>("/api/auth/logout", { method: "POST" });
}

export function me() {
  return api<CurrentUser>("/api/auth/me");
}
