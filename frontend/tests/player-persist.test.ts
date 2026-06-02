import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("playback persists across navigation; mini-player + full-screen work", async ({ page, request }) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  // start playback from the set-page transport
  await page.locator('[data-test="play-state"]').click();
  await expect(page.locator('[data-test="play-state"]')).toHaveAttribute("data-state", "playing", { timeout: 15_000 });

  // navigate away — mini-player must remain and keep the playing state
  await page.goto("/sets", { waitUntil: "networkidle" });
  const mini = page.locator('[data-test="mini-play-state"]');
  await expect(mini).toBeVisible();
  await expect(mini).toHaveAttribute("data-state", "playing");

  // open full-screen and confirm its transport is present
  await page.locator(".m-sheet-meta").click();
  await expect(page.locator('[data-test="fs-play-state"]')).toBeVisible();
});
