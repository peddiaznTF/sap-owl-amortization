// tests/e2e/specs/amortization.spec.js
import { test, expect } from '@playwright/test';

test.describe('Amortization Management', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'mock-token');
      localStorage.setItem('current_user', JSON.stringify({
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User'
      }));
    });

    // Mock API responses
    await page.route('**/companies', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          companies: [
            {
              id: 'COMP001',
              name: 'Test Company',
              currency: 'EUR'
            }
          ]
        })
      });
    });

    await page.goto('/');
  });

  test('should display company selector', async ({ page }) => {
    await expect(page.locator('.company-selector')).toBeVisible();
    await expect(page.locator('select')).toContainText('Test Company');
  });

  test('should navigate to amortization management', async ({ page }) => {
    // Select company first
    await page.selectOption('select', 'COMP001');
    
    // Navigate to amortization
    await page.click('text=Amortización Clientes');
    
    await expect(page.locator('h2')).toContainText('Gestión de Amortización - Clientes');
  });

  test('should open create amortization form', async ({ page }) => {
    await page.selectOption('select', 'COMP001');
    await page.click('text=Amortización Clientes');
    await page.click('text=Nueva Amortización');
    
    await expect(page.locator('.modal-overlay')).toBeVisible();
    await expect(page.locator('h3')).toContainText('Nueva Amortización');
  });

  test('should filter amortizations', async ({ page }) => {
    // Mock amortizations data
    await page.route('**/amortizations*', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: '1',
              reference: 'AMORT-001',
              entityName: 'Test Client',
              totalAmount: 10000,
              status: 'active'
            }
          ],
          total: 1
        })
      });
    });

    await page.selectOption('select', 'COMP001');
    await page.click('text=Amortización Clientes');
    
    // Apply status filter
    await page.selectOption('.filters-section select', 'active');
    
    await expect(page.locator('.amortization-card')).toHaveCount(1);
  });

  test('should create new amortization', async ({ page }) => {
    // Mock entities
    await page.route('**/sap/business-partners*', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'entity1',
            sap_card_code: 'C001',
            name: 'Test Client'
          }
        ])
      });
    });

    // Mock create response
    await page.route('**/amortizations', route => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'new-amort',
            reference: 'AMORT-NEW',
            status: 'active'
          })
        });
      }
    });

    await page.selectOption('select', 'COMP001');
    await page.click('text=Amortización Clientes');
    await page.click('text=Nueva Amortización');
    
    // Fill form
    await page.fill('input[id="reference"]', 'AMORT-TEST');
    await page.selectOption('select[id="entity"]', 'entity1');
    await page.fill('input[id="total_amount"]', '10000');
    await page.fill('input[id="total_installments"]', '12');
    await page.fill('input[id="start_date"]', '2024-01-01');
    
    await page.click('button[type="submit"]');
    
    // Should close modal and refresh list
    await expect(page.locator('.modal-overlay')).not.toBeVisible();
  });

  test('should display amortization table', async ({ page }) => {
    // Mock installments
    await page.route('**/amortizations/*/installments', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: '1',
            installment_number: 1,
            due_date: '2024-02-01',
            principal_amount: 800,
            interest_amount: 33.33,
            total_amount: 833.33,
            status: 'pending'
          }
        ])
      });
    });

    // Create and view amortization
    await page.selectOption('select', 'COMP001');
    await page.click('text=Amortización Clientes');
    
    // Assuming there's an amortization to view
    await page.click('text=Ver Detalle');
    
    await expect(page.locator('.amortization-table')).toBeVisible();
    await expect(page.locator('table thead')).toContainText('Fecha Venc.');
    await expect(page.locator('tbody tr')).toHaveCount(1);
  });
});
