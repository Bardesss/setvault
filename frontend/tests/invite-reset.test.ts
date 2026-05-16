import { expect, test } from "@playwright/test";

test("/invite/<bad-token> shows an error", async ({ page }) => {
  await page.goto("/invite/this-token-does-not-exist");
  await page.waitForLoadState("networkidle");
  await page.getByLabel(/username/i).fill("tester");
  await page.getByLabel(/display name/i).fill("Tester");
  await page.getByLabel(/password/i).fill("correct-horse-battery-staple");
  await page.getByRole("button", { name: /accept invite/i }).click();
  await expect(page.getByText(/invite invalid or expired/i)).toBeVisible();
});
