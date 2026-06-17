import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export interface SystemInfo {
  version: string;
  user_count: number;
  set_count: number;
  env: Record<string, string>;
}

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch("/api/admin/system");
  if (!response.ok) {
    throw error(response.status, "Failed to load system info");
  }
  const info = (await response.json()) as SystemInfo;
  return { info };
};
