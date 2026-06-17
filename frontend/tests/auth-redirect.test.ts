import { expect, test } from "@playwright/test";

// Service worker caches /api GETs, which would bypass the route stubs below.
test.use({ serviceWorkers: "block" });

test("a logged-out user on a protected route is redirected to /login", async ({ page }) => {
  // Setup is complete (a user exists) but there's no session.
  await page.route(/\/api\/setup\/status/, (r) =>
    r.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ needs_setup: false }),
    }),
  );
  await page.route(/\/api\/auth\/me/, (r) =>
    r.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "not authenticated" }),
    }),
  );

  await page.goto("/sets");
  await page.waitForURL("**/login");
  expect(page.url()).toContain("/login");
});
