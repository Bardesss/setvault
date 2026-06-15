import { redirect } from "@sveltejs/kit";
import type { LayoutServerLoad } from "./$types";

// Public routes that can never be the first-run target (no embeds/invites/
// resets exist on an empty install), so they skip the setup-status COUNT.
const SETUP_GATE_SKIP_PREFIXES = ["/embed/", "/invite/", "/reset/"];

export const load: LayoutServerLoad = async ({ fetch, cookies, url }) => {
  // First-run gate: with zero users, force the setup wizard; once setup is
  // done, keep /setup locked. Cheap COUNT query — skipped on public routes.
  if (!SETUP_GATE_SKIP_PREFIXES.some((p) => url.pathname.startsWith(p))) {
    const statusRes = await fetch("/api/setup/status");
    const needsSetup = statusRes.ok
      ? (await statusRes.json()).needs_setup === true
      : false;
    if (needsSetup && url.pathname !== "/setup") {
      throw redirect(303, "/setup");
    }
    if (!needsSetup && url.pathname === "/setup") {
      throw redirect(303, "/login");
    }
  }

  if (!cookies.get("session")) return { user: null };
  const response = await fetch("/api/auth/me");
  if (!response.ok) return { user: null };
  return { user: await response.json() };
};
