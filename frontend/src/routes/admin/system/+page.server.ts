import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export interface SystemInfo {
  version: string;
  user_count: number;
  set_count: number;
  env: Record<string, string>;
}

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  if (!cookies.get("session")) {
    throw error(401, "Not authenticated");
  }
  const response = await fetch("/api/admin/system");
  if (!response.ok) {
    throw error(response.status, "Failed to load system info");
  }
  const info = (await response.json()) as SystemInfo;
  return { info };
};
