import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("set detail renders title + waveform region", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/sets/seeded-set");
  await expect(page.getByRole("heading", { name: /seeded set/i })).toBeVisible();
  await expect(page.locator("[data-test=wavesurfer-canvas] canvas")).toBeVisible();
});

test("space toggles playback", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/sets/seeded-set");
  await page.locator("[data-test=wavesurfer-canvas] canvas").click();
  await page.keyboard.press("Space");
  await expect(page.locator("[data-test=play-state]")).toHaveAttribute("data-state", "playing");
});
