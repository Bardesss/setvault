import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("set page is reachable offline after first load", async ({
  page,
  request,
  context,
}) => {
  const seed = await loginAs(page, request);

  // First load — primes the SW caches.
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  // Wait until the SW has activated so the navigation cache picked up the doc.
  await page.waitForFunction(
    async () => {
      if (!("serviceWorker" in navigator)) return false;
      const reg = await navigator.serviceWorker.getRegistration();
      return !!reg?.active;
    },
    { timeout: 15_000 },
  );

  // Network-first reads `runtime` on success then falls back when offline.
  await context.setOffline(true);
  await page.reload({ waitUntil: "domcontentloaded" });

  // The set title should still render from the cached document.
  await expect(page.locator("h1")).toContainText("seeded set", { timeout: 10_000 });
});
