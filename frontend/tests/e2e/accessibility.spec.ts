import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('landing specimen reveals hidden instructions with keyboard', async ({ page }) => {
  await page.goto('/');
  const specimen = page.getByRole('img', { name: /synthetic northwind payroll email specimen/i });
  await specimen.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByText('3 hidden instructions found.')).toBeAttached();
});

test('landing and live test have no axe violations', async ({ page }) => {
  for (const path of ['/', '/test']) {
    await page.goto(path);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations, `${path} has accessibility violations`).toEqual([]);
  }
});

test('reduced motion starts the specimen revealed', async ({ browser }) => {
  const context = await browser.newContext({ reducedMotion: 'reduce' });
  const page = await context.newPage();
  await page.goto('/');
  await expect(page.getByText('3 hidden instructions found.')).toBeAttached();
  await context.close();
});
