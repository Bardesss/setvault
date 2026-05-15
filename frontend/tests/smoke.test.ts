import { expect, test } from "@playwright/test";

test("home renders the SetVault wordmark", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /setvault/i })).toBeVisible();
});
