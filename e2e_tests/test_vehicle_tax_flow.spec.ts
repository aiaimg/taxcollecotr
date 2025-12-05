import { test, expect, Page } from '@playwright/test';

/**
 * E2E Test: Complete Vehicle Tax Declaration Flow
 * 
 * This test covers the entire user journey:
 * 1. User registers an account
 * 2. Logs in
 * 3. Adds a vehicle
 * 4. Views calculated tax
 * 5. Proceeds to payment
 * 6. Downloads QR code and receipt
 */

// Test data
const testUser = {
    email: `test_${Date.now()}@example.com`,
    password: 'TestPass123!@#',
    firstName: 'Jean',
    lastName: 'Dupont',
};

const testVehicle = {
    licensePlate: `${Math.floor(1000 + Math.random() * 9000)} ABC`,
    fiscalPower: '5',
    engineSize: '1500',
    energySource: 'Essence',
    firstRegDate: '2020-01-15',
    category: 'Personnel',
    brand: 'Toyota',
    model: 'Corolla',
};

test.describe('Vehicle Tax Declaration Flow', () => {

    test('Complete flow: Register → Login → Add Vehicle → Pay Tax → Download QR Code', async ({ page }) => {
        // Step 1: Navigate to registration page
        await page.goto('/');
        await page.click('text=S\'inscrire');

        // Step 2: Fill registration form
        await page.fill('input[name="email"]', testUser.email);
        await page.fill('input[name="first_name"]', testUser.firstName);
        await page.fill('input[name="last_name"]', testUser.lastName);
        await page.fill('input[name="password1"]', testUser.password);
        await page.fill('input[name="password2"]', testUser.password);
        await page.selectOption('select[name="user_type"]', 'individual');

        // Submit registration
        await page.click('button[type="submit"]');

        // Verify registration success (should redirect to login or dashboard)
        await expect(page).toHaveURL(/\/(login|dashboard)/);

        // Step 3: Login (if not already logged in)
        if (page.url().includes('/login')) {
            await page.fill('input[name="login"]', testUser.email);
            await page.fill('input[name="password"]', testUser.password);
            await page.click('button[type="submit"]');
        }

        // Verify login success
        await expect(page).toHaveURL(/\/dashboard/);
        await expect(page.locator('text=Bienvenue')).toBeVisible();

        // Step 4: Navigate to Add Vehicle page
        await page.click('text=Ajouter un véhicule');
        await expect(page).toHaveURL(/\/vehicles\/add/);

        // Step 5: Fill vehicle form
        await page.fill('input[name="license_plate"]', testVehicle.licensePlate);
        await page.fill('input[name="fiscal_power_cv"]', testVehicle.fiscalPower);
        await page.fill('input[name="engine_size_cm3"]', testVehicle.engineSize);
        await page.selectOption('select[name="energy_source"]', testVehicle.energySource);
        await page.fill('input[name="first_registration_date"]', testVehicle.firstRegDate);
        await page.selectOption('select[name="categorie_vehicule"]', testVehicle.category);
        await page.selectOption('select[name="vehicle_type"]', 'Terrestre');
        await page.selectOption('select[name="terrestrial_subtype"]', 'voiture');

        // Submit vehicle form
        await page.click('button[type="submit"]');

        // Step 6: Verify vehicle added and tax calculated
        await expect(page.locator('text=Véhicule ajouté avec succès')).toBeVisible();

        // Navigate to vehicle details to see tax calculation
        await page.click(`text=${testVehicle.licensePlate}`);

        // Verify tax amount is displayed (should be > 0 for personal vehicle)
        const taxAmount = await page.locator('[data-testid="tax-amount"]').textContent();
        expect(taxAmount).toMatch(/\d+/);
        expect(parseInt(taxAmount!.replace(/\D/g, ''))).toBeGreaterThan(0);

        // Step 7: Proceed to payment
        await page.click('text=Payer maintenant');

        // Verify payment page loaded
        await expect(page).toHaveURL(/\/payments\//);
        await expect(page.locator('text=Montant à payer')).toBeVisible();

        // Select MVola as payment method
        await page.click('text=MVola');
        await page.fill('input[name="phone_number"]', '0340000000');

        // Submit payment (this will use test mode)
        await page.click('button[text="Confirmer le paiement"]');

        // Step 8: Verify payment success
        // Note: In test mode, payment should succeed immediately
        await page.waitForURL(/\/payments\/success/, { timeout: 30000 });
        await expect(page.locator('text=Paiement réussi')).toBeVisible();

        // Step 9: Download QR code
        const downloadPromise = page.waitForEvent('download');
        await page.click('text=Télécharger le QR Code');
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toMatch(/qr.*\.png/i);

        // Step 10: Download receipt
        const receiptDownloadPromise = page.waitForEvent('download');
        await page.click('text=Télécharger le reçu');
        const receiptDownload = await receiptDownloadPromise;
        expect(receiptDownload.suggestedFilename()).toMatch(/recu.*\.pdf/i);

        // Step 11: Verify QR code contains verification URL
        const qrUrl = await page.locator('[data-testid="qr-verification-url"]').textContent();
        expect(qrUrl).toContain('/verify/');

        // Step 12: Test QR verification in new page
        const verificationUrl = qrUrl!.trim();
        await page.goto(verificationUrl);

        // Verify QR page shows correct information (public page, no login required)
        await expect(page.locator('text=PAYÉ')).toBeVisible();
        await expect(page.locator(`text=${testVehicle.licensePlate}`)).toBeVisible();
        await expect(page.locator('text=2025')).toBeVisible(); // Current tax year
    });

    test('Exempt vehicle shows 0 tax', async ({ page }) => {
        // This test would be for public institution users registering exempt vehicles
        // Skipping full registration, assuming user already exists

        // Login as public institution user
        await page.goto('/login');
        await page.fill('input[name="login"]', 'public@example.com');
        await page.fill('input[name="password"]', 'TestPass123!');
        await page.click('button[type="submit"]');

        // Add ambulance vehicle
        await page.goto('/vehicles/add');
        await page.fill('input[name="license_plate"]', `${Math.floor(1000 + Math.random() * 9000)} AMB`);
        await page.selectOption('select[name="categorie_vehicule"]', 'Ambulance');
        await page.fill('input[name="fiscal_power_cv"]', '7');
        await page.fill('input[name="first_registration_date"]', '2022-06-01');

        // Submit
        await page.click('button[type="submit"]');

        // Verify tax is 0
        const taxAmount = await page.locator('[data-testid="tax-amount"]').textContent();
        expect(taxAmount).toContain('0');
        expect(page.locator('text=EXONÉRÉ')).toBeVisible();
    });
});
