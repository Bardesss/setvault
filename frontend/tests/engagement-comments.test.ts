import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("post and view a comment", async ({ page, request }) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`);

  const composer = page.locator("section.comments textarea");
  await composer.waitFor({ state: "visible", timeout: 15_000 });
  await composer.fill("This is a **bold** test comment");

  await page.locator("section.comments button", { hasText: /send/i }).click();

  // The rendered HTML wraps bold in <strong>
  const firstItem = page.locator("section.comments ul > li").first();
  await expect(firstItem.locator("strong")).toContainText("bold");
});
