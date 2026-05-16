import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export interface AdminUser {
  id: string;
  email: string;
  username: string;
  display_name: string;
  role: string;
  disabled_at: string | null;
}

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  if (!cookies.get("session")) {
    throw error(401, "Not authenticated");
  }
  const response = await fetch("/api/users");
  if (!response.ok) {
    throw error(response.status, "Failed to load users");
  }
  const body = (await response.json()) as { items: AdminUser[] };
  return { users: body.items };
};
