import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ fetch, cookies }) => {
  if (!cookies.get("session")) return { user: null };
  const response = await fetch("/api/auth/me");
  if (!response.ok) return { user: null };
  return { user: await response.json() };
};
