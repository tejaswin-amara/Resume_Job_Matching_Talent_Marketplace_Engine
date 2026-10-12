import { test, expect } from '@playwright/test';

test('Marketplace navigation and portals', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Talent Marketplace Engine')).toBeVisible();
  await expect(page.getByText('Candidate Portal')).toBeVisible();
  await expect(page.getByText('Recruiter Portal')).toBeVisible();
});

test('Candidate Portal renders upload dropzone and title', async ({ page }) => {
  await page.goto('/candidates');
  await expect(page.getByText('Candidate Portal')).toBeVisible();
  await expect(page.getByText('Upload Resume')).toBeVisible();
});

