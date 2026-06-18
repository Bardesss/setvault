// frontend/tests/catalog-admin.test.ts
import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

// SW caches /api GETs; block so route stubs apply.
test.use({ serviceWorkers: "block" });

test("admin catalog tab shows duplicates and merges a cluster", async ({ page, request }) => {
  await loginAs(page, request);

  await page.route(/\/api\/admin\/catalog\/artists\/duplicates/, (r) =>
    r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({
      clusters: [[
        { id: "11111111-0000-0000-0000-000000000001", name: "DJ X", slug: "dj-x", ref_count: 3 },
        { id: "22222222-0000-0000-0000-000000000002", name: "dj x", slug: "dj-x-2", ref_count: 1 },
      ]],
    }) }),
  );
  await page.route(/\/api\/admin\/catalog\/artists$/, (r) =>
    r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) }),
  );
  let merged = false;
  await page.route(/\/api\/catalog\/artists\/[^/]+\/merge/, (r) => {
    merged = true;
    return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "x", name: "DJ X", slug: "dj-x", country: null, bio: null, aliases: [], image_url: null }) });
  });
  page.on("dialog", (d) => d.accept());

  await page.goto("/admin/catalog?kind=artists");
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("DJ X")).toBeVisible();
  await page.getByRole("button", { name: /merge into first/i }).click();
  await expect.poll(() => merged).toBe(true);
});
