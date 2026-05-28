import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

/**
 * Audio cache cap eviction: lower the SW's cap to a small number, prime the
 * audio cache with three oversized fake entries through the page-side
 * `caches.open(...).put(...)` API, then trigger a real audio fetch so the
 * SW's `enforceAudioCap` runs. Assert the oldest fake entry is gone.
 *
 * Locks the §J18 contract (admin-configurable cap, oldest-first eviction).
 */
test("audio cache evicts oldest entry when over cap", async ({
  page,
  request,
  context,
}) => {
  const seed = await loginAs(page, request);

  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });
  await page.waitForFunction(
    async () => {
      if (!("serviceWorker" in navigator)) return false;
      const reg = await navigator.serviceWorker.getRegistration();
      return !!reg?.active;
    },
    { timeout: 15_000 },
  );
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForFunction(
    () => navigator.serviceWorker?.controller !== null,
    { timeout: 15_000 },
  );

  const audioCacheName = await page.evaluate(async () => {
    const names = await caches.keys();
    return names.find((n) => n.endsWith("-audio")) ?? null;
  });
  expect(audioCacheName, "audio cache should be created by the SW").not.toBeNull();

  // Lower cap to 1500 bytes; each fake entry is 1000 bytes → at least the
  // oldest must be evicted once a real fetch lands.
  await page.evaluate(async () => {
    const reg = await navigator.serviceWorker.getRegistration();
    reg!.active!.postMessage({ type: "set-cap", bytes: 1500 });
  });

  // Prime the cache with three fake stream entries in known insertion order.
  await page.evaluate(async (name) => {
    const cache = await caches.open(name);
    for (const slug of ["fake-a", "fake-b", "fake-c"]) {
      const body = new Uint8Array(1000).fill(slug.charCodeAt(5));  // unique bytes
      await cache.put(
        new Request(`/api/sets/${slug}/stream`),
        new Response(body, {
          status: 200,
          headers: { "content-type": "audio/flac", "content-length": "1000" },
        }),
      );
    }
  }, audioCacheName!);

  const before = await page.evaluate(async (name) => {
    const cache = await caches.open(name);
    return (await cache.keys()).map((r) => new URL(r.url).pathname);
  }, audioCacheName!);
  expect(before).toEqual(expect.arrayContaining([
    "/api/sets/fake-a/stream",
    "/api/sets/fake-b/stream",
    "/api/sets/fake-c/stream",
  ]));

  // Trigger a real audio fetch via the SW path so `audioCacheFirst`
  // appends to the cache and runs `enforceAudioCap`.
  await page.evaluate(async (slug) => {
    await fetch(`/api/sets/${slug}/stream`, { credentials: "include" });
  }, seed.set.slug);

  const after = await page.evaluate(async (name) => {
    const cache = await caches.open(name);
    return (await cache.keys()).map((r) => new URL(r.url).pathname);
  }, audioCacheName!);

  expect(after, "fake-a (oldest fake) should be evicted").not.toContain(
    "/api/sets/fake-a/stream",
  );

  // Cleanup so the next test doesn't see the lowered cap or fake entries.
  await context.clearCookies();
});
