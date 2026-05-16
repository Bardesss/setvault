import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, parent }) => {
  const layout = await parent();
  if (!layout.user) {
    return { user: null, continueListening: [], activity: [], recent: [] };
  }
  const [cont, act, recent] = await Promise.all([
    fetch("/api/me/continue-listening").then((r) => (r.ok ? r.json() : [])),
    fetch("/api/me/activity").then((r) => (r.ok ? r.json() : [])),
    fetch("/api/sets?limit=12").then((r) => (r.ok ? r.json() : { items: [] })),
  ]);
  return {
    user: layout.user,
    continueListening: cont,
    activity: act,
    recent: recent.items ?? [],
  };
};
