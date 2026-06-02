import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("playback persists across navigation; mini-player + full-screen work", async ({ page, request }) => {
  page.on("console", (m) => console.log("PAGE>", m.type(), m.text()));
  page.on("pageerror", (e) => console.log("PAGEERROR>", e.message));
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  // start playback from the set-page transport
  await page.locator('[data-test="play-state"]').click();
  // TEMP DIAGNOSTIC: dump the engine <audio> state + play() outcome
  const diag = await page.evaluate(async () => {
    const els = Array.from(document.querySelectorAll("audio"));
    const a = els[0] as HTMLAudioElement | undefined;
    if (!a) return { audioCount: els.length, found: false };
    let playErr: string | null = null;
    try { await a.play(); } catch (e) { playErr = String(e); }
    return {
      audioCount: els.length, found: true, paused: a.paused,
      readyState: a.readyState, networkState: a.networkState,
      errorCode: a.error?.code ?? null, currentSrc: a.currentSrc,
      duration: a.duration, muted: a.muted, playErr,
    };
  });
  console.log("DIAG>", JSON.stringify(diag));
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
