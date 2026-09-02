import { expect, test } from "@playwright/test";

test("research demo completes the safe review flow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Research prototype.").first()).toBeVisible();
  await page.getByRole("radio", { name: /Progressive instability/ }).check();
  await page.getByRole("button", { name: /Start replay/ }).click();
  await expect(
    page.getByRole("heading", { name: "Confirm research subject context" }),
  ).toBeVisible();
  await page.getByRole("button", { name: /Begin 180-second baseline calibration/ }).click();
  await expect(
    page.getByRole("heading", { name: "Establishing a stable reference" }),
  ).toBeVisible();
  await expect(page.getByText(/LIVE REPLAY/)).toBeVisible({ timeout: 12_000 });
  await expect(page.getByText("ELEVATED").first()).toBeVisible({ timeout: 10_000 });
  await page.getByRole("button", { name: /Open structured explanation/ }).click();
  await expect(
    page.getByRole("heading", { name: "What changed the research index?" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Evidence" }).click();
  await expect(page.getByText("EVD-T21S-UI-0003")).toBeVisible();
  await page.getByRole("button", { name: "Case review" }).click();
  await expect(page.getByText("Research summary — not a patient-care report")).toBeVisible();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export anonymized JSON" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("t21-safe-research-session.json");
});
