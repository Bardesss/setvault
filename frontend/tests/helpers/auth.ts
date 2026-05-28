import type { APIRequestContext, Page } from "@playwright/test";

const API_BASE = process.env.SETVAULT_API_BASE ?? "http://localhost:1970";

interface SeedResponse {
  admin: { email: string; password: string };
  set: { slug: string };
}

/**
 * Hits the dev-seed endpoint (gated by SETVAULT_DEV_SEED on the backend) to
 * idempotently provision an admin user + published LiveSet with slug
 * "seeded-set", then logs the Playwright page in as that admin so the page's
 * cookie jar has a valid session for the frontend.
 *
 * Returns the seed payload (slug, admin credentials) for any caller that
 * wants to assert on them.
 */
export async function loginAs(
  page: Page,
  request: APIRequestContext,
): Promise<SeedResponse> {
  const seedResponse = await request.post(`${API_BASE}/api/dev/seed-e2e`);
  if (!seedResponse.ok()) {
    throw new Error(
      `dev seed endpoint failed (${seedResponse.status()}): is the backend running with SETVAULT_DEV_SEED=1?`,
    );
  }
  const seed = (await seedResponse.json()) as SeedResponse;

  // Log in through the frontend dev server so cookies are scoped to the page origin.
  const loginResponse = await page.request.post("/api/auth/login", {
    data: { email: seed.admin.email, password: seed.admin.password },
    headers: { "Content-Type": "application/json" },
  });
  if (!loginResponse.ok()) {
    throw new Error(`login failed (${loginResponse.status()})`);
  }
  // Playwright stores Set-Cookie automatically; nothing else needed.
  return seed;
}
