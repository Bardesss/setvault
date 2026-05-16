import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ fetch, request }) => {
  const cookie = request.headers.get("cookie") ?? "";
  if (!cookie.includes("session=")) return { user: null };
  const response = await fetch("/api/auth/me");
  if (!response.ok) return { user: null };
  return { user: await response.json() };
};
