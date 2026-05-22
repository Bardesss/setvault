import { error } from "@sveltejs/kit";
import type { ProviderConfig } from "$lib/api/providers";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  if (!cookies.get("session")) {
    throw error(401, "Not authenticated");
  }
  const response = await fetch("/api/admin/providers");
  if (!response.ok) {
    throw error(response.status, "Failed to load providers");
  }
  const body = (await response.json()) as { items: ProviderConfig[] };
  return { providers: body.items };
};
