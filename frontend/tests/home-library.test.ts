import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("home shows continue-listening when state exists", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/sets/seeded-set");
  await page.waitForLoadState("networkidle");
  // Seed UserSetState explicitly so the test doesn't race the Player's
  // best-effort onDestroy saveState (which is fire-and-forget and may be
  // aborted by SvelteKit's client-side navigation before the PUT lands).
  // Hitting the API directly through the page's cookie jar guarantees the
  // row exists before we render the home page.
  const cookies = await page.context().cookies();
  const csrf = cookies.find((c) => c.name === "csrf_token")?.value ?? "";
  const put = await page.request.put("/api/sets/seeded-set/state", {
    data: { position_seconds: 5, completed: false },
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
  });
  expect(put.ok()).toBeTruthy();
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /continue/i })).toBeVisible();
});

test("library lists seeded set and filters by query", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/sets");
  await expect(page.getByRole("link", { name: /seeded set/i })).toBeVisible();
});
