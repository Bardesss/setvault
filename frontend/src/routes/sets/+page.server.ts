import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import type { SetSummary } from "$lib/api/sets";

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  if (!cookies.get("session")) {
    throw error(401, "Not authenticated");
  }
  const response = await fetch("/api/sets");
  if (!response.ok) {
    throw error(response.status, "Failed to load library");
  }
  const body = (await response.json()) as { items: SetSummary[] };
  return { sets: body.items };
};
