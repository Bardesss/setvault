import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("admin users tab lists the seeded admin", async ({ page, request }) => {
  await loginAs(page, request);
  await page.goto("/admin/users");
  await expect(page.getByText("admin@example.test")).toBeVisible();
});
