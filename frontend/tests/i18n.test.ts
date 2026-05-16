import { expect, test } from "@playwright/test";

test("i18n initialises on layout load", async ({ page }) => {
  await page.goto("/login");
  await expect.poll(() =>
    page.evaluate(() => (window as any).__i18n_initialized__)
  ).toBe(true);
});
