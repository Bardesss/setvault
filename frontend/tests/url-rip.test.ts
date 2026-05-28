import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("URL tab renders and form submits a stubbed rip job", async ({ page, request }) => {
  await loginAs(page, request);

  // Stub the listing first — empty list so the form is visible.
  await page.route("**/api/me/rip-jobs**", (route) =>
    route.fulfill({ status: 200, body: JSON.stringify({ items: [] }) }),
  );

  // Stub the submit — return a canned RipJob for the URL the user types.
  await page.route("**/api/sets/url-rip", (route) =>
    route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        id: "00000000-0000-0000-0000-000000000001",
        live_set_id: null,
        live_set_slug: null,
        source_url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        source_external_id: "dQw4w9WgXcQ",
        source_platform: "youtube",
        status: "queued",
        progress_pct: 0,
        message: null,
        error_text: null,
        probed_metadata: { title: "Stub Title" },
        ytdlp_version: "2026.3.17",
        created_at: new Date().toISOString(),
        started_at: null,
        finished_at: null,
      }),
    }),
  );

  await page.goto("/sets/new");
  await page.waitForLoadState("networkidle");

  // Click the URL tab.
  await page.getByRole("tab", { name: "URL" }).click();

  // Fill the form and submit.
  await page.locator('input[type="url"]').fill(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  );
  await page.getByRole("button", { name: /^add$/i }).click();

  // The new rip job's stub title should now appear in the recent-rips list.
  await expect(page.getByText("Stub Title")).toBeVisible({ timeout: 5_000 });
  await expect(page.getByText("Queued")).toBeVisible();
});
