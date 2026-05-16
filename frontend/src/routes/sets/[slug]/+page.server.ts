import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import type { SetDetail } from "$lib/api/sets";

export const load: PageServerLoad = async ({ fetch, params, cookies }) => {
  if (!cookies.get("session")) {
    throw error(401, "Not authenticated");
  }
  const response = await fetch(`/api/sets/${params.slug}`);
  if (response.status === 404) {
    throw error(404, "Set not found");
  }
  if (!response.ok) {
    throw error(response.status, "Failed to load set");
  }
  const set: SetDetail = await response.json();
  return { set };
};
