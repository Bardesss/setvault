// Routes reachable without a session. Everything else requires login; the
// root layout load bounces logged-out users from a protected route to /login.
const PUBLIC_EXACT = new Set(["/login", "/setup"]);
const PUBLIC_PREFIXES = ["/embed/", "/invite/", "/reset/"];

export function isPublicRoute(pathname: string): boolean {
  return (
    PUBLIC_EXACT.has(pathname) ||
    PUBLIC_PREFIXES.some((p) => pathname.startsWith(p))
  );
}
