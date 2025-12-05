# Validation Framework Implementation

This README explains how to use the validation framework for the Madagascar Tax Collector application.

## Overview

The validation framework provides a comprehensive testing approach with 5 phases:

1. **Linting** - Code quality checks with flake8
2. **Type Checking** - Static type analysis with mypy
3. **Style Checking** - Code formatting with black and isort
4. **Unit Testing** - Django unit tests with coverage reporting
5. **End-to-End Testing** - Complete user workflow testing with Playwright

**Philosophy:** If `/validate` passes, your app works. Manual testing becomes largely unnecessary.

## Initial Setup

### 1. Install Development Dependencies

```bash
# Activate your virtual environment
source .venv/bin/activate  # or: source venv/bin/activate

# Install validation tools
pip install -r requirements-dev.txt
```

### 2. Install Playwright Browsers

```bash
# Install Playwright browsers for E2E testing
npx playwright install
```

### 3. Verify Docker is Running

E2E tests require Docker for the test database:

```bash
docker --version
# If Docker is not installed, download from: https://www.docker.com/products/docker-desktop
```

## Running Validation

### Complete Validation (All Phases)

Run all validation phases with a single command:

```bash
/validate
```

Or if not using the workflow system:

```bash
bash .agent/workflows/validate.md
```

### Individual Phases

You can also run individual phases:

#### Phase 1: Linting

```bash
source .venv/bin/activate || source venv/bin/activate
flake8 .
```

#### Phase 2: Type Checking

```bash
source .venv/bin/activate || source venv/bin/activate
mypy .
```

#### Phase 3: Style Checking

```bash
source .venv/bin/activate || source venv/bin/activate
black --check .
isort --check-only .
```

To auto-fix style issues:

```bash
black .
isort .
```

#### Phase 4: Unit Tests

```bash
source .venv/bin/activate || source venv/bin/activate
python3 manage.py test
```

With coverage:

```bash
source .venv/bin/activate || source venv/bin/activate
coverage run manage.py test
coverage report
coverage html  # Generate HTML report at htmlcov/index.html
```

#### Phase 5: E2E Tests

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run E2E tests
npx playwright test

# View test report
npx playwright show-report

# Cleanup
docker-compose -f docker-compose.test.yml down
```

## Understanding E2E Tests

The E2E tests cover complete user workflows:

### Test Suites

- **test_vehicle_tax_flow.spec.ts** - Vehicle registration and tax payment
- **test_qr_verification.spec.ts** - QR code verification flow
- **test_contravention_flow.spec.ts** - Contravention creation and payment
- **test_exemptions.spec.ts** - Tax exemption handling
- **test_admin_operations.spec.ts** - Admin dashboard operations
- **test_fleet_management.spec.ts** - Multi-vehicle fleet management

### What E2E Tests Verify

✅ Complete user journeys from start to finish  
✅ Database integrity after each operation  
✅ External integrations (MVola payments, email notifications)  
✅ QR code generation and public verification  
✅ Error handling and edge cases  
✅ Tax calculation accuracy per legal requirements  

## Configuration Files

- `.flake8` - Linting configuration
- `mypy.ini` - Type checking configuration
- `pyproject.toml` - Black, isort, coverage, and pytest configuration
- `playwright.config.ts` - E2E test configuration
- `docker-compose.test.yml` - Test environment setup
- `requirements-dev.txt` - Development dependencies

## Troubleshooting

### Linting Errors

If you get linting errors:
- Review the specific line and fix the issue
- Or add `# noqa` comment if it's a false positive

### Type Checking Errors

- Add type annotations to functions
- Use `# type: ignore` for third-party libraries without types

### Style Errors

Auto-fix with:
```bash
black .
isort .
```

### E2E Test Failures

1. Check test report: `npx playwright show-report`
2. View screenshots in `test-results/` directory
3. Ensure Docker is running
4. Verify test database settings in `settings_test.py`

### Docker Issues

If Docker containers don't start:
```bash
# Stop all containers
docker-compose -f docker-compose.test.yml down

# Remove volumes and restart
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up -d
```

## CI/CD Integration

This validation framework can be integrated into CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run validation
        run: bash .agent/workflows/validate.md
```

## Next Steps

1. Run `/ultimate_validate_command` to analyze your specific codebase
2. Run `/validate` to execute all validation phases
3. Review reports in `htmlcov/` and `playwright-report/`
4. Add more E2E test scenarios as needed
5. Integrate into your CI/CD pipeline

## Support

For issues or questions:
- Review the implementation plan: `.gemini/antigravity/brain/.../implementation_plan.md`
- Check Playwright documentation: https://playwright.dev
- Check Django testing documentation: https://docs.djangoproject.com/en/stable/topics/testing/
