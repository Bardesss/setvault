import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("upload page shows tus drop zone", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/sets/new");
  await page.waitForLoadState("networkidle");
  await expect(page.getByText(/drop audio|choose file/i)).toBeVisible();
});
