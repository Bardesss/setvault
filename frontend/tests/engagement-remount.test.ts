import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("set page renders BookmarkButton + CommentThread + PrivateNotesPanel", async ({
  page,
  request,
}) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  await expect(page.locator("button.bookmark")).toBeVisible();
  await expect(page.locator("section.comments")).toBeVisible();
  await expect(page.locator("section.notes")).toBeVisible();
});

test("waveform comment markers render after a positioned comment is posted", async ({
  page,
  request,
}) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`, { waitUntil: "networkidle" });

  const cookies = await page.context().cookies();
  const csrf = cookies.find((c) => c.name === "csrf_token")?.value ?? "";

  // Post a positioned comment via the API (faster than driving the composer)
  const post = await page.request.post(
    `/api/sets/${seed.set.slug}/comments`,
    {
      data: { body: "test marker", position_seconds: 30 },
      headers: { "X-CSRF-Token": csrf },
    },
  );
  expect(post.ok()).toBeTruthy();

  await page.reload({ waitUntil: "networkidle" });
  await expect(page.locator(".markers .marker").first()).toBeVisible({
    timeout: 15_000,
  });
});
