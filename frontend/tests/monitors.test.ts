import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";

test("monitors tab and discoveries inbox render", async ({ page, request }) => {
  await loginAs(page, request);

  await page.goto("/admin/monitors", { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: /monitors/i })).toBeVisible();

  await page.getByPlaceholder(/artist, party, or venue/i).fill("Bicep");
  await page.getByRole("button", { name: /add monitor/i }).click();
  await expect(page.getByText("Bicep")).toBeVisible();

  await page.goto("/discoveries", { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: /discoveries/i })).toBeVisible();
});
