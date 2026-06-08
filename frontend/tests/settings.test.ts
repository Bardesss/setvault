import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("settings change password works end-to-end", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/settings");
  await page.waitForLoadState("networkidle");
  await page.getByRole("tab", { name: /^Security$/i }).click();
  await page.getByLabel(/current password/i).fill("hunter2hunter2");
  await page.getByLabel(/new password/i).fill("brand-new-password-77");
  await page.getByRole("button", { name: /change password/i }).click();
  await page.waitForLoadState("networkidle");
  await expect(page.getByText(/password updated/i)).toBeVisible();
});
