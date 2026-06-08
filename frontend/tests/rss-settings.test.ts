import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("settings RSS section renders and creates a token", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/settings");
  await page.waitForLoadState("networkidle");

  // RSS feeds tab present, then open it
  await expect(page.getByRole("tab", { name: /^RSS feeds$/i })).toBeVisible();
  await page.getByRole("tab", { name: /^RSS feeds$/i }).click();

  // Fill the name and click Create
  await page.locator('input[placeholder="Podcast app"]').fill("e2e token");
  await page.getByRole("button", { name: /Create RSS token/i }).click();

  // The just-minted aside should show all three URLs
  await expect(page.getByText(/These URLs are shown once/i)).toBeVisible({ timeout: 5000 });
  await expect(page.locator("code").filter({ hasText: "/api/feed/favorites/" })).toBeVisible();
  await expect(page.locator("code").filter({ hasText: "/api/feed/recent/" })).toBeVisible();
  await expect(page.locator("code").filter({ hasText: "/api/feed/everything/" })).toBeVisible();
});
