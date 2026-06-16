import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

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

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch("/api/media-roots");
  if (!response.ok) {
    throw error(response.status, "Failed to load media roots");
  }
  const body = (await response.json()) as { items: MediaRootRow[] };
  return { roots: body.items };
};
