import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("home renders the SetVault wordmark", async ({ page, request }) => {
  // Home is a protected route: a logged-out visit now redirects to /login
  // (see +layout.ts), so authenticate first. The SetVault wordmark in the
  // authenticated shell is the top-bar brand link.
  await loginAs(page, request);
  await page.goto("/");
  await expect(page.getByRole("link", { name: /setvault home/i })).toBeVisible();
});
