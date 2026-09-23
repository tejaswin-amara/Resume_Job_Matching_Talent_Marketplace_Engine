import { expect, test } from '@playwright/test';

test.describe('Talent Engine Matching Flow E2E', () => {
  test('landing page renders and navigates to Match Intelligence Studio', async ({ page }) => {
    await page.goto('/');

    // Verify Hero and branding
    await expect(page.getByRole('heading', { level: 1 })).toContainText(/Autonomous AI Resume/i);

    // Click CTA to evaluate candidate resume
    const ctaButton = page.getByRole('link', { name: /Evaluate Candidate Resume/i });
    await expect(ctaButton).toBeVisible();
    await ctaButton.click();

    // Verify we arrived at the candidate evaluation studio
    await expect(page).toHaveURL(/.*recruiter\/candidates/);
    await expect(page.getByRole('heading', { level: 1 })).toContainText(
      /Autonomous Candidate Calibration/i,
    );
  });

  test('simulates resume upload, resolves analysis, and asserts radial score meter', async ({
    page,
  }) => {
    await page.goto('/recruiter/candidates');

    // Wait for document ingestion pane
    const dropzoneInput = page.getByTestId('dropzone-input');
    await expect(dropzoneInput).toBeAttached();

    // Prepare simulated PDF buffer
    const buffer = Buffer.from('%PDF-1.4 Simulated Resume Content for E2E Testing');

    // Upload sample resume file
    await dropzoneInput.setInputFiles({
      name: 'candidate_alex_sample.pdf',
      mimeType: 'application/pdf',
      buffer,
    });

    // Verify live loading state or immediate resolution
    // Wait for Radial Score Meter to be visible
    const scoreMeter = page.getByTestId('radial-score-meter');
    await expect(scoreMeter).toBeVisible({ timeout: 10000 });

    // Assert visibility of affinity score percentage and label
    const scoreValue = page.getByTestId('radial-score-value');
    await expect(scoreValue).toBeVisible();
    await expect(scoreValue).toContainText('%');

    // Assert Skill Gap Visualizer and dual badges
    const skillGap = page.getByTestId('skill-gap-visualizer');
    await expect(skillGap).toBeVisible();
  });
});
