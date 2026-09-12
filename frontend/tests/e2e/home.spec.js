import { test, expect } from '@playwright/test';

test('has title and heading', async ({ page }) => {
  await page.goto('/');

  // Expect a heading with the text "Talent Engine Dashboard"
  await expect(page.getByRole('heading', { name: 'Talent Engine Dashboard' })).toBeVisible();

  // Verify main sections
  await expect(page.getByRole('heading', { name: 'Employers' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Candidates' })).toBeVisible();
});
