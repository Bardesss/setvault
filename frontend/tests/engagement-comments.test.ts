import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("post and view a comment", async ({ page, request }) => {
  const seed = await loginAs(page, request);
  await page.goto(`/sets/${seed.set.slug}`);
  // Wait for the initial listComments fetch + any other in-flight hydration
  // to settle so the composer is fully wired before we type into it.
  await page.waitForLoadState("networkidle");

  // Comments is the default SidePanel tab, but click it explicitly so the
  // test is robust to the default tab changing.
  await page.getByRole("tab", { name: "Comments" }).click();

  const composer = page.locator("section.comments textarea");
  await composer.waitFor({ state: "visible", timeout: 15_000 });
  // Focus the textarea before filling so the `input` event lands on a
  // hydrated Svelte component (bind:value listener attached).
  await composer.click();
  await composer.fill("This is a **bold** test comment");

  // The send button is `disabled={busy || !body.trim()}` — explicitly wait
  // for the disabled state to clear so we surface the real cause if
  // bind:value didn't propagate (rather than timing out inside .click()).
  const sendBtn = page.locator("section.comments form.composer button[type='submit']");
  await expect(sendBtn).toBeEnabled({ timeout: 10_000 });
  await sendBtn.click();

  // The rendered HTML wraps bold in <strong>; allow time for the POST
  // round-trip + reactive list update.
  const firstItem = page.locator("section.comments > ul > li").first();
  await expect(firstItem.locator("strong")).toContainText("bold", { timeout: 10_000 });
});
