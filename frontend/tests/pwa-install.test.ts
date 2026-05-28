import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("manifest.webmanifest is reachable and parseable", async ({ request }) => {
  const r = await request.get("/manifest.webmanifest");
  expect(r.status()).toBe(200);
  const m = await r.json();
  expect(m.name).toBe("SetVault");
  expect(m.start_url).toBe("/");
  expect(m.display).toBe("standalone");
  expect(Array.isArray(m.icons) && m.icons.length).toBeGreaterThan(0);
});

test("manifest icons are reachable", async ({ request }) => {
  for (const size of [192, 256, 512]) {
    const r = await request.get(`/icons/icon-${size}.png`);
    expect(r.status(), `icon-${size}.png`).toBe(200);
    expect(r.headers()["content-type"]).toMatch(/image\/png/);
  }
});

test("service worker registers on the root page", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/", { waitUntil: "networkidle" });
  // Give the deferred onMount registration a moment
  const sw = await page.waitForFunction(
    async () => {
      if (!("serviceWorker" in navigator)) return null;
      const reg = await navigator.serviceWorker.getRegistration();
      return reg ? { scope: reg.scope, active: !!reg.active } : null;
    },
    { timeout: 15_000 },
  ).then((h) => h.jsonValue() as Promise<{ scope: string; active: boolean } | null>);
  expect(sw).not.toBeNull();
  expect(sw!.scope).toMatch(/\/$/);
});
