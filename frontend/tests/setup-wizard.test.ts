import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("setup is locked once an admin exists", async ({ page, request }) => {
  // Seed an admin so the install is already set up (needs_setup === false).
  await loginAs(page, request);

  await page.goto("/setup");

  // The layout gate must redirect away from /setup; it must not show the wizard.
  await expect(page).not.toHaveURL(/\/setup$/);
});
