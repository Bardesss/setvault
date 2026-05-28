import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("set page is reachable offline after first load", async ({
  page,
  request,
  context,
}) => {
  const seed = await loginAs(page, request);

  // First load — registers the SW but the page that did the registration
  // isn't controlled by the SW yet (no `serviceWorker.controller`).
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  // Wait until the SW has activated.
  await page.waitForFunction(
    async () => {
      if (!("serviceWorker" in navigator)) return false;
      const reg = await navigator.serviceWorker.getRegistration();
      return !!reg?.active;
    },
    { timeout: 15_000 },
  );

  // Reload once ONLINE — this is the load that puts the document into the
  // SW's runtime cache AND brings the page under SW control. Without this,
  // the next reload would hit raw network because the page is still
  // uncontrolled from the very first goto().
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForFunction(
    () => navigator.serviceWorker?.controller !== null,
    { timeout: 15_000 },
  );

  // Now safe to go offline — the SW will serve the cached document.
  await context.setOffline(true);
  await page.reload({ waitUntil: "domcontentloaded" });

  await expect(page.locator("h1")).toContainText("seeded set", { timeout: 10_000 });
});
