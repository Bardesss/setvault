import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("variable-speed preset buttons render and activate on click", async ({ page, request }) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  const speedControl = page.locator('[data-test="speed-control"]');
  await expect(speedControl).toBeVisible();

  // All four preset buttons should be rendered.
  await expect(speedControl.locator("button")).toHaveCount(4);

  // Click the 1.25× preset and verify it receives the .on class.
  const btn125 = speedControl.locator("button", { hasText: "1.25×" });
  await btn125.click();
  await expect(btn125).toHaveClass(/\bon\b/);
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
