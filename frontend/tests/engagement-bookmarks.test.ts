import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("/me/bookmarks page renders heading", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/me/bookmarks");
  await expect(page.locator("h1")).toContainText(/bookmarks/i);
});

test("set-level bookmark toggles via button", async ({ page, request }) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`);

  const btn = page.locator("button.bookmark");
  await btn.waitFor({ state: "visible", timeout: 15_000 });

  // Initial state is unstarred
  const initial = await btn.getAttribute("aria-pressed");
  await btn.click();

  // aria-pressed should flip to "true"
  await expect(btn).toHaveAttribute("aria-pressed", initial === "true" ? "false" : "true");
});
