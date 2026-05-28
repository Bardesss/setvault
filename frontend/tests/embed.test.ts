import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("embed page is 404 by default, 200 after admin enables", async ({ page, request }) => {
  const seed = await loginAs(page, request);

  // Get the CSRF token from cookies (set by login) so PATCH passes the
  // CsrfMiddleware. The fetch helpers on `request` reuse the page cookie jar.
  const cookies = await page.context().cookies();
  const csrf = cookies.find((c) => c.name === "csrf_token")?.value ?? "";

  // Initially: embed disabled — expect 4xx or "not found" body.
  await page.goto(`/embed/${seed.set.slug}`, { waitUntil: "networkidle" });
  // SvelteKit's error.svelte typically renders "Not found" text for a 404.
  await expect(page.locator("body")).toContainText(/not found|404/i);

  // Enable embed via the admin endpoint.
  const patch = await page.request.patch(`/api/sets/${seed.set.slug}/embed`, {
    data: { allowed: true },
    headers: { "X-CSRF-Token": csrf },
  });
  expect(patch.ok()).toBeTruthy();

  await page.goto(`/embed/${seed.set.slug}`, { waitUntil: "networkidle" });
  await expect(page.locator("h1")).toContainText("seeded set");
});
