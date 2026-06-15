import { error } from "@sveltejs/kit";
import type { SourceState } from "$lib/api/ingest_sources";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  if (!cookies.get("session")) {
    throw error(401, "Not authenticated");
  }
  const response = await fetch("/api/admin/ingest-sources");
  if (!response.ok) {
    throw error(response.status, "Failed to load sources");
  }
  const body = (await response.json()) as { items: SourceState[] };
  return { sources: body.items };
};
