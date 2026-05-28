/**
 * Service-worker route → strategy selector.
 *
 * Extracted from `service-worker.ts` so the routing logic can be unit-tested
 * without spinning up an actual SW. The SW imports this and dispatches on
 * the strategy name.
 */

export type Strategy =
  | "static"        // cache-first; long-lived
  | "audio"         // cache-first with cap enforcement
  | "api"           // network-only (auth state must stay fresh)
  | "navigation"    // network-first, falls back to runtime cache
  | "bypass";       // don't touch this request

const AUDIO_RE = /^\/api\/sets\/[^/]+\/(stream|audio\.opus)(\?|$)/;

export function chooseStrategy(
  pathname: string,
  precacheUrls: ReadonlyArray<string> = [],
): Strategy {
  // Precached SvelteKit build chunks + static files.
  if (precacheUrls.includes(pathname)) return "static";
  if (pathname.startsWith("/_app/")) return "static";
  if (pathname.startsWith("/fonts/")) return "static";
  if (pathname.startsWith("/icons/")) return "static";
  if (pathname === "/manifest.webmanifest") return "static";

  // Audio stream is cache-first under an admin-configurable cap.
  if (AUDIO_RE.test(pathname)) return "audio";

  // Every other /api/ call (including waveform JSON, which carries auth-
  // gated content) is network-only so auth state doesn't go stale.
  if (pathname.startsWith("/api/")) return "api";

  // Anything else is a SvelteKit page navigation - network-first.
  return "navigation";
}
