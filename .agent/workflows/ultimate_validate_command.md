---
description: Generate comprehensive validation workflow for the TaxCollector project
---

# Generate Ultimate Validation Command

This workflow analyzes the Madagascar Tax Collector codebase and generates a comprehensive `validate.md` workflow tailored to this Django application.

## Step 0: Discover Real User Workflows

**Review application documentation to understand what users actually do:**

1. **Read key documentation files:**
   - `mvp0.md` - Vehicle tax platform requirements and user stories
   - `madagascar_contravention_app_base.md` - Contravention management flows
   - `ORGANISATION_PLAN_USER_TYPES_AND_EXEMPTIONS.md` - User types and exemption rules

2. **Identify core user journeys:**
   
   **For Individual Citizens:**
   - Register account → Add vehicle → View tax calculation → Pay tax → Download QR code
   - View contraventions → Pay fine → Receive receipt
   
   **For Companies/Fleet Managers:**
   - Register company account → Add multiple vehicles → Bulk tax payment → Manage fleet
   
   **For Public Institutions:**
   - Register institution → Add vehicles (ambulance, administrative, etc.) → Verify exemption status
   
   **For Police Officers:**
   - Create contravention → Record vehicle details → Generate QR code → Track payment
   
   **For Admins:**
   - Monitor tax collection → Search vehicles → Generate reports → Manage exemptions
   
   **For Law Enforcement (Verification):**
   - Scan QR code → Verify tax payment status → Check vehicle information

3. **External integrations to test:**
   - MVola payment API (mobile money in Madagascar)
   - Email notifications (registration, payment confirmations, reminders)
   - SMS notifications (payment reminders, contravention alerts)
   - QR code generation and public verification endpoints
   - OCR for vehicle documents (carte grise)

## Step 1: Deep Codebase Analysis

**Analyze the existing validation and testing infrastructure:**

### Check for existing validation tools:

**Linting:** Look for `.flake8`, `.pylintrc`, `ruff.toml`, or similar configs
**Type checking:** Look for `mypy.ini`, `pyproject.toml` with mypy config
**Style/formatting:** Look for `.editorconfig`, `pyproject.toml` with black/isort config
**Unit tests:** Check Django test files (`test_*.py`, `*/tests.py`)
**Package dependencies:** Review `requirements.txt` and `package.json`

### Understand the application architecture:

**Django Apps:**
- `vehicles/` - Vehicle registration and tax calculation
- `payments/` - Payment processing (MVola integration)
- `contraventions/` - Traffic violations management
- `notifications/` - Notification system
- `administration/` - Admin functionalities
- `core/` - User authentication and profiles
- `cms/` - Content management
- `api/` - REST API endpoints

**Database:**
- PostgreSQL with vehicle, payment, user, contravention tables
- Tax rate grids based on fiscal power, age, energy source
- Exemption categories (ambulance, administrative, international conventions)

**Frontend:**
- Django templates with Velzon admin theme
- Playwright already installed for E2E testing
- Bootstrap 5, jQuery, ApexCharts

### Review existing testing:

**Unit Tests Found:**
- `payments/tests/` - MVola API, callbacks, validators
- `api/tests/` - API endpoint tests
- `vehicles/tests.py` - Vehicle model tests
- `contraventions/tests.py` - Contravention tests
- `cms/tests/` - CMS context processor tests

**Current Test Command:**
```bash
python3 manage.py test
```

## Step 2: Generate validate.md

Create `.agent/workflows/validate.md` with comprehensive validation phases:

### Phase 1: Linting

**Install if needed:** Add to `requirements-dev.txt`: `flake8`, `flake8-django`

**Command:**
```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

# Run flake8 with Django-specific rules
flake8 . --exclude=migrations,node_modules,.venv,venv,staticfiles --max-line-length=120
```

### Phase 2: Type Checking

**Install if needed:** Add to `requirements-dev.txt`: `mypy`, `django-stubs`

**Command:**
```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

# Run mypy with Django plugin
mypy . --exclude migrations --exclude node_modules --exclude .venv --exclude venv
```

### Phase 3: Style Checking

**Install if needed:** Add to `requirements-dev.txt`: `black`, `isort`

**Commands:**
```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

# Check code formatting with black
black --check . --exclude '/(migrations|node_modules|\.venv|venv|staticfiles)/'

# Check import sorting
isort --check-only . --skip migrations --skip node_modules --skip .venv --skip venv
```

### Phase 4: Unit Testing

**Command:**
```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

# Run all Django unit tests with coverage
coverage run --source='.' manage.py test --exclude-tag=e2e
coverage report --omit='*/migrations/*,*/tests/*,*/venv/*,*/.venv/*'
coverage html
```

### Phase 5: End-to-End Testing (COMPREHENSIVE)

**This is the critical phase that tests complete user workflows.**

#### Setup Test Environment:
```bash
# Start test database and services
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready
sleep 5

# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

# Run migrations for test database
python3 manage.py migrate --settings=taxcollector_project.settings_test

# Load test fixtures
python3 manage.py loaddata e2e_tests/fixtures/test_users.json
python3 manage.py loaddata e2e_tests/fixtures/test_vehicles.json
```

#### Run E2E Tests:

**Test 1: Complete Vehicle Tax Declaration Flow**
```bash
npx playwright test e2e_tests/test_vehicle_tax_flow.py
```
- Register new user (individual citizen)
- Login
- Navigate to "Add Vehicle" form
- Fill vehicle details (license plate, fiscal power, engine size, energy source)
- Submit and verify tax calculation is correct
- Proceed to payment
- Complete MVola payment (test mode)
- Verify payment confirmation page
- Download QR code and PDF receipt
- Logout

**Verify in Database:**
- Query users table: verify user created
- Query vehicles table: verify vehicle registered with correct details
- Query tax calculations: verify amount matches legal grid
- Query payments: verify payment recorded with MVola transaction ID
- Query QR codes: verify unique token generated

**Test 2: QR Code Public Verification**
```bash
npx playwright test e2e_tests/test_qr_verification.py
```
- Extract QR code URL from previous test
- Navigate to verification page (public, no login)
- Verify displays: license plate, tax year, "PAYÉ" status, payment date, expiry date

**Test 3: Contravention Flow**
```bash
npx playwright test e2e_tests/test_contravention_flow.py
```
- Login as police officer
- Create new contravention
- Select infraction type (e.g., "Excès de vitesse")
- Enter vehicle details and location
- Generate contravention with QR code
- Logout from police account
- Login as citizen (vehicle owner)
- View "My Contraventions" page
- See new contravention with amount due
- Pay contravention via MVola
- Verify receipt and payment confirmation

**Verify in Database:**
- Query contraventions table: verify created
- Query payments: verify fine paid
- Verify status updated to "payée"

**Test 4: Exemption Handling**
```bash
npx playwright test e2e_tests/test_exemptions.py
```
- Login as public institution user
- Add vehicle with category "Ambulance"
- Verify tax amount shows 0 (exempt)
- Verify "EXONÉRÉ" status displayed
- Add vehicle with category "Administratif"
- Verify exempt status
- Generate QR code
- Scan QR and verify shows "EXONÉRÉ" not "PAYÉ"

**Test 5: Admin Operations**
```bash
npx playwright test e2e_tests/test_admin_operations.py
```
- Login as admin
- Search vehicle by license plate
- View payment history
- Generate revenue report
- Export data to CSV
- Verify all operations complete successfully

**Test 6: Multi-Vehicle Fleet Management**
```bash
npx playwright test e2e_tests/test_fleet_management.py
```
- Login as company user
- Add 5 vehicles
- View all vehicles in dashboard
- Select multiple vehicles for bulk payment
- Complete consolidated payment
- Verify all QR codes generated

#### Cleanup:
```bash
# Stop test containers
docker-compose -f docker-compose.test.yml down

# Clean up test data
python3 manage.py flush --no-input --settings=taxcollector_project.settings_test
```

## Critical: Don't Stop Until Everything is Validated

The E2E tests **must**:
1. ✅ Test complete user journeys from docs, not just API endpoints
2. ✅ Verify data in database after each operation
3. ✅ Test external integrations (MVola, email, QR generation)
4. ✅ Cover all user types (citizen, company, police, admin, public institution)
5. ✅ Test error scenarios (payment failures, invalid data, etc.)
6. ✅ Verify exemption logic matches legal requirements

## Output

After running this workflow, you should have a complete `validate.md` file that can be executed with a single command:

```bash
/validate
```

This will run all 5 phases and give you **complete confidence** that the application works correctly, eliminating the need for manual testing.
