// tests/e2e/specs/auth.spec.js
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display login form', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Sistema de Amortización');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.field-error')).toHaveCount(2);
    await expect(page.locator('.field-error').first()).toContainText('email es requerido');
  });

  test('should show error for invalid email format', async ({ page }) => {
    await page.fill('input[type="email"]', 'invalid-email');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.field-error')).toContainText('Formato de email inválido');
  });

  test('should toggle password visibility', async ({ page }) => {
    const passwordInput = page.locator('input[type="password"]');
    const toggleButton = page.locator('.password-toggle');
    
    await page.fill('input[type="password"]', 'testpassword');
    await expect(passwordInput).toHaveAttribute('type', 'password');
    
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'text');
    
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Mock API response
    await page.route('**/auth/login', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-token',
          token_type: 'bearer',
          user: {
            id: '1',
            email: 'test@example.com',
            full_name: 'Test User'
          }
        })
      });
    });

    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.locator('h2')).toContainText('Dashboard');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Mock API error response
    await page.route('**/auth/login', route => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Incorrect email or password'
        })
      });
    });

    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error-message')).toContainText('Email o contraseña incorrectos');
  });

  test('should open forgot password modal', async ({ page }) => {
    await page.click('text=¿Olvidaste tu contraseña?');
    
    await expect(page.locator('.modal-overlay')).toBeVisible();
    await expect(page.locator('h3')).toContainText('Recuperar Contraseña');
  });

  test('should open registration modal', async ({ page }) => {
    await page.click('text=Regístrate aquí');
    
    await expect(page.locator('.modal-overlay')).toBeVisible();
    await expect(page.locator('h3')).toContainText('Crear Cuenta');
  });
});
