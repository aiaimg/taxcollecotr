# Test Data Setup - Quick Guide

## ✅ What Was Created

1. **SMTP Configuration System** - Manage email sending for reminders and notifications
2. **Test Data Command** - Create users, vehicles, payments, QR codes, and agents
3. **QR Verification System** - Scan and verify vehicle tax payments
4. **Show QR Codes Command** - Display QR codes for testing

## 🚀 Quick Start

### 1. Load Official Tax Grid

```bash
python load_official_tax_grid.py
```

This loads the official 2025 tax rates (80 rates loaded).

### 2. Create Test Data

```bash
python manage.py create_test_data --users 2 --vehicles-per-user 2 --create-agent
```

This creates:
- 2 test users (testuser1, testuser2) with password: `test123`
- 2 vehicles per user with realistic specs
- Payments for each vehicle (mix of paid/unpaid)
- QR codes for paid vehicles
- 1 verification agent (agent1) with password: `agent123`

### 3. View QR Codes

```bash
python manage.py show_qr_codes --limit 5
```

Shows QR codes with scan URLs for testing.

## 📱 Testing QR Code Verification

### Method 1: Web Browser
1. Copy a scan URL from the output
2. Open in browser: `http://127.0.0.1:8000/payments/qr/verify/{token}/`
3. View vehicle and payment information

### Method 2: As Verification Agent
1. Login as agent: `agent1` / `agent123`
2. Visit the scan URL
3. Verification will be logged automatically

### Method 3: API
```bash
curl http://127.0.0.1:8000/payments/qr/api/{token}/
```

Returns JSON with vehicle and payment data.

## 👥 Test Accounts

### Regular Users
- **Username**: testuser1, testuser2
- **Password**: test123
- **Email**: testuser1@example.com, testuser2@example.com

### Verification Agent
- **Username**: agent1
- **Password**: agent123
- **Badge**: AGENT#### (random)
- **Zone**: Antananarivo Centre

## 🔗 Important URLs

- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Vehicles**: http://127.0.0.1:8000/vehicles/
- **Payments**: http://127.0.0.1:8000/payments/
- **QR Codes Admin**: http://127.0.0.1:8000/admin/payments/qrcode/
- **Verification Logs**: http://127.0.0.1:8000/admin/administration/verificationqr/
- **SMTP Config**: http://127.0.0.1:8000/admin/administration/smtpconfiguration/

## 📧 SMTP Configuration

### Setup Email Sending

1. Go to: http://127.0.0.1:8000/admin/administration/smtpconfiguration/
2. Click "Add SMTP Configuration"
3. Fill in your SMTP details (Gmail, Office365, etc.)
4. Click "Test" to verify connection
5. Check "Configuration active" and save

### Quick SMTP Setup Script

```bash
python scripts/create_test_smtp.py
```

Interactive wizard to configure SMTP.

### Test SMTP

```bash
python manage.py test_smtp your-email@example.com
```

## 🧪 Testing Workflow

### Complete Test Scenario

1. **Setup**:
   ```bash
   python load_official_tax_grid.py
   python manage.py create_test_data --clean --users 2 --vehicles-per-user 2 --create-agent
   ```

2. **Login as User** (testuser1/test123):
   - View vehicles
   - Check payments
   - Download QR codes

3. **Login as Agent** (agent1/agent123):
   - Scan QR codes
   - Verify payments
   - View verification logs

4. **Check Admin**:
   - View all vehicles
   - Check payment status
   - Review QR code scans
   - See verification logs

## 🔍 What to Test

### Vehicle Management
- ✅ Create vehicles with different types
- ✅ Calculate taxes based on power, age, fuel type
- ✅ View vehicle list and details

### Payment System
- ✅ Create payments
- ✅ Different payment statuses (paid, pending, exempt)
- ✅ Payment methods (card, mobile money, cash)

### QR Code System
- ✅ Generate QR codes for paid taxes
- ✅ Scan QR codes
- ✅ Verify vehicle tax status
- ✅ Track scan count
- ✅ Check expiration dates

### Verification Agent
- ✅ Agent login
- ✅ QR code scanning
- ✅ Verification logging
- ✅ View verification history

### Email System (if SMTP configured)
- ✅ Send payment reminders
- ✅ Send notifications
- ✅ Track email logs
- ✅ Monitor daily limits

## 🛠️ Useful Commands

### Clean and Recreate Data
```bash
python manage.py create_test_data --clean --users 3 --vehicles-per-user 3 --create-agent
```

### Show Only Active QR Codes
```bash
python manage.py show_qr_codes --active-only --limit 10
```

### Send Payment Reminders
```bash
python manage.py send_payment_reminders
```

### Test SMTP Configuration
```bash
python manage.py test_smtp your-email@example.com
```

## 📊 Sample Data Created

### Vehicles
- Realistic plate numbers (e.g., "7280 TCD", "5172 TAB")
- Various types (Car, Moto, Truck, Bus, Scooter)
- Different power ratings (4-30 CV)
- Different ages (2010-2023)
- Various fuel types (Essence, Diesel, Electric, Hybrid)

### Payments
- Calculated from official tax grid
- Mix of paid (75%) and pending (25%)
- Realistic amounts (30,000 - 315,000 Ar)
- Different payment methods
- Proper expiration dates (1 year from payment)

### QR Codes
- 32-character secure tokens
- Linked to vehicles and fiscal year
- Expiration tracking
- Scan count tracking
- Active/inactive status

## 🐛 Troubleshooting

### "No vehicle types found"
Run: `python manage.py create_test_data` (it creates them automatically)

### "No tax grid found"
Run: `python load_official_tax_grid.py`

### "QR Code not found"
Make sure the payment is marked as "PAYE" (paid)

### "SMTP not configured"
Follow SMTP setup guide in `SMTP_CONFIGURATION_GUIDE.md`

## 📝 Notes

- Test data uses prefix "testuser" for easy identification
- All test vehicles have "T" prefix in plate numbers
- QR codes expire 1 year after payment
- Agent badge numbers are random (AGENT####)
- Payments use realistic tax calculations from official grid

## 🎯 Next Steps

1. Configure SMTP for email notifications
2. Test QR code scanning with mobile device
3. Create custom test scenarios
4. Test payment reminder system
5. Verify agent workflow
6. Test API endpoints

For more details, see:
- `SMTP_CONFIGURATION_GUIDE.md` - Email setup
- `SMTP_SETUP_SUMMARY.md` - Quick SMTP reference
- `PAYMENT_REMINDER_SYSTEM.md` - Reminder system docs
