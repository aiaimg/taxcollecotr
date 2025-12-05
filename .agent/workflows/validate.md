---
description: Run complete validation workflow for TaxCollector
---

# Complete Validation Workflow

Run all validation phases: linting, type checking, style checking, unit tests, and comprehensive E2E tests.

**Philosophy:** If this command passes, your app works. No manual testing needed.

## Prerequisites

Before running this workflow for the first time, ensure validation tools are installed:

```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

# Install validation dependencies (if not already in requirements.txt)
pip install flake8 flake8-django mypy django-stubs black isort coverage
```

---

## Phase 1: Linting

Check code quality and catch common Python issues:

```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

echo "=== Phase 1: Running Flake8 Linter ==="
flake8 . \
  --exclude=migrations,node_modules,.venv,venv,staticfiles,htmlcov \
  --max-line-length=120 \
  --extend-ignore=E203,W503

if [ $? -ne 0 ]; then
  echo "❌ Linting failed. Please fix the issues above."
  exit 1
fi

echo "✅ Phase 1 Complete: No linting issues found"
```

---

## Phase 2: Type Checking

Verify type annotations and catch type-related bugs:

```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

echo "=== Phase 2: Running MyPy Type Checker ==="
mypy . \
  --exclude migrations \
  --exclude node_modules \
  --exclude .venv \
  --exclude venv \
  --exclude staticfiles \
  --ignore-missing-imports \
  --no-strict-optional

if [ $? -ne 0 ]; then
  echo "❌ Type checking failed. Please fix the issues above."
  exit 1
fi

echo "✅ Phase 2 Complete: No type errors found"
```

---

## Phase 3: Style Checking

Ensure consistent code formatting:

```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

echo "=== Phase 3: Checking Code Style ==="

# Check with Black
echo "Checking formatting with Black..."
black --check . \
  --exclude '/(migrations|node_modules|\.venv|venv|staticfiles|htmlcov)/'

if [ $? -ne 0 ]; then
  echo "❌ Black formatting check failed. Run 'black .' to auto-format."
  exit 1
fi

# Check import sorting
echo "Checking import sorting with isort..."
isort --check-only . \
  --skip migrations \
  --skip node_modules \
  --skip .venv \
  --skip venv \
  --skip staticfiles \
  --profile black

if [ $? -ne 0 ]; then
  echo "❌ Import sorting check failed. Run 'isort .' to auto-fix."
  exit 1
fi

echo "✅ Phase 3 Complete: Code style is consistent"
```

---

## Phase 4: Unit Testing

Run all Django unit tests with coverage:

```bash
# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

echo "=== Phase 4: Running Unit Tests ==="

# Run tests with coverage
coverage run --source='.' manage.py test --exclude-tag=e2e

if [ $? -ne 0 ]; then
  echo "❌ Unit tests failed. Please fix the failing tests."
  exit 1
fi

# Generate coverage report
echo ""
echo "Coverage Report:"
coverage report \
  --omit='*/migrations/*,*/tests/*,*/venv/*,*/.venv/*,*/node_modules/*,*/staticfiles/*' \
  --skip-covered

# Generate HTML coverage report
coverage html \
  --omit='*/migrations/*,*/tests/*,*/venv/*,*/.venv/*,*/node_modules/*,*/staticfiles/*'

echo ""
echo "ℹ️  Detailed coverage report: htmlcov/index.html"
echo "✅ Phase 4 Complete: All unit tests passed"
```

---

## Phase 5: End-to-End Testing

**This is the comprehensive phase that tests complete user workflows.**

### Setup Test Environment

```bash
echo "=== Phase 5: Running End-to-End Tests ==="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "⚠️  Docker is not running. Starting Docker..."
  open -a Docker
  sleep 10
fi

# Start test environment
echo "Starting test environment..."
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 10

# Activate virtual environment
source .venv/bin/activate || source venv/bin/activate

# Apply migrations to test database
echo "Applying migrations to test database..."
python3 manage.py migrate --settings=taxcollector_project.settings_test

# Load test fixtures
echo "Loading test data..."
if [ -f "e2e_tests/fixtures/test_users.json" ]; then
  python3 manage.py loaddata e2e_tests/fixtures/test_users.json --settings=taxcollector_project.settings_test
fi
if [ -f "e2e_tests/fixtures/test_vehicles.json" ]; then
  python3 manage.py loaddata e2e_tests/fixtures/test_vehicles.json --settings=taxcollector_project.settings_test
fi
```

### Run E2E Test Suites

```bash
echo ""
echo "Running E2E Test Suite..."
echo "=========================="

# Test 1: Vehicle Tax Declaration Flow
echo ""
echo "Test 1: Complete Vehicle Tax Declaration Flow"
npx playwright test e2e_tests/test_vehicle_tax_flow.spec.ts --reporter=html

if [ $? -ne 0 ]; then
  echo "❌ Vehicle tax flow test failed"
  docker-compose -f docker-compose.test.yml down
  exit 1
fi

# Test 2: QR Code Verification
echo ""
echo "Test 2: QR Code Public Verification"
npx playwright test e2e_tests/test_qr_verification.spec.ts --reporter=html

if [ $? -ne 0 ]; then
  echo "❌ QR verification test failed"
  docker-compose -f docker-compose.test.yml down
  exit 1
fi

# Test 3: Contravention Flow
echo ""
echo "Test 3: Contravention Creation and Payment"
npx playwright test e2e_tests/test_contravention_flow.spec.ts --reporter=html

if [ $? -ne 0 ]; then
  echo "❌ Contravention flow test failed"
  docker-compose -f docker-compose.test.yml down
  exit 1
fi

# Test 4: Exemption Handling
echo ""
echo "Test 4: Tax Exemption Verification"
npx playwright test e2e_tests/test_exemptions.spec.ts --reporter=html

if [ $? -ne 0 ]; then
  echo "❌ Exemption handling test failed"
  docker-compose -f docker-compose.test.yml down
  exit 1
fi

# Test 5: Admin Operations
echo ""
echo "Test 5: Admin Dashboard Operations"
npx playwright test e2e_tests/test_admin_operations.spec.ts --reporter=html

if [ $? -ne 0 ]; then
  echo "❌ Admin operations test failed"
  docker-compose -f docker-compose.test.yml down
  exit 1
fi

# Test 6: Fleet Management
echo ""
echo "Test 6: Multi-Vehicle Fleet Management"
npx playwright test e2e_tests/test_fleet_management.spec.ts --reporter=html

if [ $? -ne 0 ]; then
  echo "❌ Fleet management test failed"
  docker-compose -f docker-compose.test.yml down
  exit 1
fi

echo ""
echo "ℹ️  E2E Test Report: playwright-report/index.html"
```

### Cleanup Test Environment

```bash
echo ""
echo "Cleaning up test environment..."

# Stop and remove test containers
docker-compose -f docker-compose.test.yml down

# Clean up test data
python3 manage.py flush --no-input --settings=taxcollector_project.settings_test 2>/dev/null || true

echo "✅ Phase 5 Complete: All E2E tests passed"
```

---

## Summary

```bash
echo ""
echo "=========================================="
echo "✅ ALL VALIDATION PHASES PASSED"
echo "=========================================="
echo ""
echo "✅ Phase 1: Linting - No issues found"
echo "✅ Phase 2: Type Checking - No type errors"
echo "✅ Phase 3: Style Checking - Code is well-formatted"
echo "✅ Phase 4: Unit Tests - All tests passing"
echo "✅ Phase 5: E2E Tests - All user workflows verified"
echo ""
echo "🎉 Your application is working correctly!"
echo ""
echo "Reports:"
echo "  - Coverage: htmlcov/index.html"
echo "  - E2E Tests: playwright-report/index.html"
echo ""
```

---

## Troubleshooting

If any phase fails:

1. **Phase 1 (Linting):** Fix the reported issues or run `flake8 . --exclude=migrations,node_modules,.venv,venv,staticfiles` to see details

2. **Phase 2 (Type Checking):** Add type annotations or use `# type: ignore` for third-party library issues

3. **Phase 3 (Style):** Run `black .` and `isort .` to auto-format the code

4. **Phase 4 (Unit Tests):** Run `python3 manage.py test` with verbose mode to see detailed failure information

5. **Phase 5 (E2E Tests):** 
   - Check Docker is running
   - View test report at `playwright-report/index.html`
   - Check screenshots/videos in `test-results/` directory
   - Ensure test database settings are correct in `settings_test.py`

---

## Quick Fixes

Auto-fix style issues:
```bash
source .venv/bin/activate || source venv/bin/activate
black .
isort .
```

Run only unit tests:
```bash
source .venv/bin/activate || source venv/bin/activate
python3 manage.py test
```

Run only E2E tests:
```bash
docker-compose -f docker-compose.test.yml up -d
npx playwright test
docker-compose -f docker-compose.test.yml down
```
