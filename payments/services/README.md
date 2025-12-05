# Cash Payment Services

This directory contains the core services for the cash payment system.

## Services Overview

### 1. CashPaymentService (`cash_payment_service.py`)
Handles cash payment processing, change calculation, and dual verification.

**Key Methods:**
- `calculate_change(tax_amount, amount_tendered)` - Calculate change with validation
- `create_cash_payment(collector, vehicle, customer_data, amount_tendered, ...)` - Create new cash payment for new/existing customers
- `process_existing_customer_payment(collector, vehicle_plate, amount_tendered, ...)` - Process payment for existing customer
- `requires_dual_verification(amount)` - Check if amount requires admin approval
- `approve_transaction(transaction, admin_user, notes, ...)` - Approve transaction requiring dual verification
- `void_transaction(transaction, admin_user, reason, ...)` - Void a transaction within time limit

### 2. CashSessionService (`cash_session_service.py`)
Manages cash collection sessions for agent partenaires.

**Key Methods:**
- `open_session(collector, opening_balance, ...)` - Open new cash collection session
- `close_session(session, closing_balance, counted_by, ...)` - Close session with reconciliation
- `get_active_session(collector)` - Get collector's active session
- `calculate_session_totals(session)` - Calculate session totals (transactions, commission, etc.)
- `get_session_summary(session)` - Get comprehensive session summary
- `approve_session_closure(session, admin_user, notes, ...)` - Approve session closure with discrepancy
- `get_collector_sessions(collector, start_date, end_date, status)` - Get sessions with filters
- `check_session_timeout(session)` - Check if session has timed out

### 3. CashReceiptService (`cash_receipt_service.py`)
Handles receipt generation, printing, and QR code integration.

**Key Methods:**
- `generate_cash_receipt(cash_transaction, ...)` - Generate receipt with QR code
- `reprint_receipt(original_receipt, requested_by, ...)` - Reprint existing receipt (marked as duplicate)
- `generate_cash_receipt_pdf(receipt)` - Generate printable PDF receipt using ReportLab
- `get_receipt_by_number(receipt_number)` - Get receipt by receipt number
- `get_receipts_for_vehicle(vehicle_plate, tax_year)` - Get all receipts for a vehicle

### 4. CommissionService (`commission_service.py`)
Manages commission calculations and tracking for agent partenaires.

**Key Methods:**
- `calculate_commission(tax_amount, commission_rate)` - Calculate commission amount
- `record_commission(transaction, collector, session)` - Record commission for a transaction
- `get_session_commission(session)` - Get total commission for a session
- `get_collector_commission_report(collector, start_date, end_date, payment_status)` - Generate commission report
- `mark_commissions_as_paid(commission_ids, paid_by, payment_date)` - Mark commissions as paid
- `get_pending_commissions(collector, min_amount)` - Get pending commissions
- `get_commission_summary_by_period(start_date, end_date, group_by)` - Get commission summary grouped by period

### 5. ReconciliationService (`reconciliation_service.py`)
Handles daily reconciliation and discrepancy reporting.

**Key Methods:**
- `generate_daily_report(date)` - Generate daily cash collection report
- `reconcile_day(date, admin_user, physical_count, notes, ...)` - Perform end-of-day reconciliation
- `get_discrepancy_report(start_date, end_date, collector, min_discrepancy)` - Generate discrepancy tracking report
- `get_reconciliation_history(start_date, end_date)` - Get reconciliation history for date range
- `get_unreconciled_sessions(max_age_days)` - Get sessions that are closed but not reconciled
- `get_reconciliation_summary(start_date, end_date)` - Get overall reconciliation summary

### 6. CashAuditService (`cash_audit_service.py`)
Manages audit trail with hash chain and optional encryption.

**Key Methods:**
- `log_action(action_type, user, data, session, transaction, request)` - Create audit log entry with hash chain
- `verify_audit_trail(start_date, end_date)` - Verify integrity of audit trail hash chain
- `get_audit_trail(filters, decrypt)` - Retrieve audit trail with filters
- `get_audit_statistics(start_date, end_date)` - Get audit trail statistics
- `get_user_activity(user, start_date, end_date)` - Get audit trail for specific user
- `export_audit_trail(start_date, end_date, format)` - Export audit trail for compliance

## Usage Examples

### Processing a Cash Payment

```python
from payments.services import CashPaymentService
from payments.models import AgentPartenaireProfile
from vehicles.models import Vehicule
from decimal import Decimal

# Get the collector
collector = AgentPartenaireProfile.objects.get(agent_id='AG12345678')

# Get the vehicle
vehicle = Vehicule.objects.get(plaque_immatriculation='1234 TAA')

# Customer data
customer_data = {
    'owner_name': 'John Doe',
}

# Process payment
transaction, error = CashPaymentService.create_cash_payment(
    collector=collector,
    vehicle=vehicle,
    customer_data=customer_data,
    amount_tendered=Decimal('150000.00'),
    tax_year=2024,
    request=request  # Django request object
)

if error:
    print(f"Error: {error}")
else:
    print(f"Payment successful: {transaction.transaction_number}")
```

### Opening and Closing a Session

```python
from payments.services import CashSessionService
from decimal import Decimal

# Open session
session, error = CashSessionService.open_session(
    collector=collector,
    opening_balance=Decimal('50000.00'),
    request=request
)

# ... process payments ...

# Close session
session, discrepancy = CashSessionService.close_session(
    session=session,
    closing_balance=Decimal('200000.00'),
    counted_by=request.user,
    discrepancy_notes='',
    request=request
)
```

### Generating a Receipt

```python
from payments.services import CashReceiptService

# Generate receipt
receipt, error = CashReceiptService.generate_cash_receipt(
    cash_transaction=transaction,
    request=request
)

# Generate PDF
pdf_buffer = CashReceiptService.generate_cash_receipt_pdf(receipt)

# Return as download
response = HttpResponse(pdf_buffer, content_type='application/pdf')
response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'
return response
```

### Daily Reconciliation

```python
from payments.services import ReconciliationService
from datetime import date
from decimal import Decimal

# Generate daily report
report = ReconciliationService.generate_daily_report(date.today())

# Reconcile the day
success, error, data = ReconciliationService.reconcile_day(
    date=date.today(),
    admin_user=request.user,
    physical_count=Decimal('500000.00'),
    notes='All sessions reconciled',
    request=request
)
```

## Dependencies

- Django 5.x
- ReportLab (for PDF generation)
- qrcode (for QR code generation)
- cryptography (optional, for audit log encryption)

## Security Features

1. **Hash Chain**: All audit logs are linked with SHA-256 hash chain for tamper detection
2. **Encryption**: Sensitive data in audit logs can be encrypted with AES-256 (requires cryptography library)
3. **Dual Verification**: Large transactions require admin approval
4. **Immutable Records**: Transaction records cannot be modified, only voided with compensating entries
5. **Session Timeout**: Sessions automatically expire after configured timeout period
6. **Void Time Limit**: Transactions can only be voided within configured time limit

## Configuration

All system configuration is managed through the `CashSystemConfig` model:

```python
from payments.models import CashSystemConfig

config = CashSystemConfig.get_config()
config.default_commission_rate = Decimal('2.50')  # 2.5%
config.dual_verification_threshold = Decimal('500000.00')  # 500,000 Ar
config.reconciliation_tolerance = Decimal('1000.00')  # 1,000 Ar
config.session_timeout_hours = 12
config.void_time_limit_minutes = 30
config.save()
```

## Error Handling

All services return tuples with error messages:
- `(result, error_message)` - For operations that return a single result
- `(success, error_message, data)` - For operations that return boolean success

Always check for errors:

```python
transaction, error = CashPaymentService.create_cash_payment(...)
if error:
    # Handle error
    return JsonResponse({'error': error}, status=400)
else:
    # Process successful transaction
    return JsonResponse({'transaction_id': str(transaction.id)})
```

## Testing

To test the services, ensure you have:
1. Created test agent partenaire profiles
2. Created test vehicles
3. Set up the cash system configuration

See the test files in `payments/tests/` for examples.
