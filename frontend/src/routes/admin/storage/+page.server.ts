import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export interface MediaRootRow {
  id: string;
  name: string;
  host_path: string;
  enabled: boolean;
  default_for_ingest: boolean;
  max_bytes: number | null;
  naming_template: string | null;
  last_health_status: string | null;
}

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  if (!cookies.get("session")) {
    throw error(401, "Not authenticated");
  }
  const response = await fetch("/api/media-roots");
  if (!response.ok) {
    throw error(response.status, "Failed to load media roots");
  }
  const body = (await response.json()) as { items: MediaRootRow[] };
  return { roots: body.items };
};
