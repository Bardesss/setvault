import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test.describe("enrichment", () => {
  test("resolve popover opens with mode tabs", async ({ page, request }) => {
    await loginAs(page, request);
    await page.goto("/sets/seeded-set");
    await page.waitForSelector("aside.tracklist");
    // The set page fetches its data in two passes; wait for it to settle.
    await page.waitForLoadState("networkidle");

    // Add a raw entry so a Resolve button exists, then close the edit drawer.
    await page.locator("aside.tracklist h3").click();
    await page.keyboard.press("m");
    await page.keyboard.press("Escape");

    await page.locator("aside.tracklist button.resolve").first().click();
    await expect(page.locator("section.popover")).toBeVisible();
    await expect(
      page.locator("section.popover .modes button.active"),
    ).toContainText(/metadata/i);
  });
});
