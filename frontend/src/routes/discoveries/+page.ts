import { listDiscoveries } from "$lib/api/monitors";
import type { PageLoad } from "./$types";

export const ssr = false;

export const load: PageLoad = async () => {
  const discoveries = await listDiscoveries();
  return { discoveries };
};
