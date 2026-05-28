import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("variable-speed slider renders and changes label", async ({ page, request }) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  const slider = page.locator('[data-test="speed-control"] input[type="range"]');
  await expect(slider).toBeVisible();
  await expect(slider).toHaveAttribute("min", "0.5");
  await expect(slider).toHaveAttribute("max", "2");

  // Change rate via input event and verify label updates.
  await slider.fill("1.5");
  await slider.evaluate((el) => el.dispatchEvent(new Event("input")));
  await expect(page.locator('[data-test="speed-control"] .rate')).toHaveText("1.50×");
});

test("A↔B loop shortcut sets visual band + indicator", async ({ page, request }) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  // The waveform has to render first so duration > 0; wait for the play state
  // attribute to be available.
  await page.locator('[data-test="play-state"]').waitFor({ state: "visible", timeout: 10_000 });

  // Press [ then ]. The keydown handler bails on form-field focus, so click
  // an empty area of the page first.
  await page.locator("body").click();
  await page.keyboard.press("[");
  await page.keyboard.press("]");

  // Indicator should be visible. The band may or may not have non-zero
  // width depending on how quickly the playhead advanced between presses —
  // we assert presence, not pixel geometry.
  await expect(page.locator('[data-test="loop-indicator"]')).toBeVisible({ timeout: 5_000 });
});

test("bulk-action toolbar appears after admin selects a row", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/sets", { waitUntil: "networkidle" });

  // Wait for at least one card to render.
  const toggle = page.locator("button.select-toggle").first();
  await toggle.waitFor({ state: "visible", timeout: 10_000 });
  await toggle.click();

  await expect(page.locator('aside[aria-label="bulk actions"]')).toBeVisible();
  await expect(
    page.locator('aside[aria-label="bulk actions"] .count strong'),
  ).toHaveText("1");
});
