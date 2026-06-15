import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("source search lists candidates and ingest fires a rip", async ({ page, request }) => {
  await loginAs(page, request);

  // Stub the source search — return one not-in-library candidate.
  await page.route("**/api/ingest-sources/search", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            source_kind: "youtube",
            external_id: "vid1",
            title: "Stub Set",
            uploader: "DJ X",
            duration_seconds: 3600,
            thumbnail_url: null,
            webpage_url: "https://www.youtube.com/watch?v=vid1",
            already_in_library: false,
          },
        ],
      }),
    }),
  );

  // Stub the rip submit — return a canned RipJob matching submitUrl's shape.
  let ripCalled = false;
  await page.route("**/api/sets/url-rip", (route) => {
    ripCalled = true;
    return route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        id: "00000000-0000-0000-0000-000000000001",
        live_set_id: null,
        live_set_slug: null,
        source_url: "https://www.youtube.com/watch?v=vid1",
        source_external_id: "vid1",
        source_platform: "youtube",
        status: "queued",
        progress_pct: 0,
        message: null,
        error_text: null,
        probed_metadata: {},
        ytdlp_version: "2026.3.17",
        created_at: new Date().toISOString(),
        started_at: null,
        finished_at: null,
      }),
    });
  });

  await page.goto("/search");
  await page.waitForLoadState("networkidle");

  // Switch to the Sources tab (wait for hydration so the click registers).
  const sourcesTab = page.getByRole("tab", { name: /^Sources$/i });
  await expect(sourcesTab).toBeVisible();
  await sourcesTab.click();

  // Fill the source-search box and submit (submit button is "Search").
  const sourceInput = page.getByPlaceholder(/Search YouTube/i);
  await expect(sourceInput).toBeVisible({ timeout: 5_000 });
  await sourceInput.fill("best set");
  await page.getByRole("button", { name: /^Search$/i }).click();

  // The stubbed candidate should appear.
  await expect(page.getByText("Stub Set")).toBeVisible({ timeout: 5_000 });

  // Click the candidate's Ingest button and assert it flips to "In library".
  await page.getByRole("button", { name: /^Ingest$/i }).click();
  await expect(page.getByText(/^In library$/i)).toBeVisible({ timeout: 5_000 });
  expect(ripCalled).toBe(true);
});
