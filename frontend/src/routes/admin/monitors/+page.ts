import { listMonitors } from "$lib/api/monitors";
import type { PageLoad } from "./$types";

export const load: PageLoad = async () => {
  const monitors = await listMonitors();
  return { monitors };
};

// Runtime data via the browser API client (cookie-auth) — don't pre-render.
export const ssr = false;
