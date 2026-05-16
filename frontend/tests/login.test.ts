import { expect, test } from "@playwright/test";

test("login route renders form and rejects bad credentials", async ({ page }) => {
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.getByLabel(/email/i).fill("nobody@example.test");
  await page.getByLabel(/password/i).fill("wrong");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByText(/invalid credentials|too many/i)).toBeVisible();
});
