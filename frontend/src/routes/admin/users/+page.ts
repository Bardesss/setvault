import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export interface AdminUser {
  id: string;
  email: string;
  username: string;
  display_name: string;
  role: string;
  disabled_at: string | null;
}

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch("/api/users");
  if (!response.ok) {
    throw error(response.status, "Failed to load users");
  }
  const body = (await response.json()) as { items: AdminUser[] };
  return { users: body.items };
};
