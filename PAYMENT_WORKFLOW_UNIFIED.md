# Unified Payment Workflow Documentation

## Overview

All payment methods (Cash, MVola, Stripe) now follow the **same workflow** after payment is confirmed. This ensures consistency across all payment types.

## Payment Success Workflow

### 1. Payment Confirmation
When a payment is successfully completed, the payment status is updated to `PAYE`:
- **Cash**: Automatically if no approval needed, or after admin approval
- **MVola**: When callback confirms payment completion
- **Stripe**: When webhook confirms payment success

### 2. QR Code Generation
After payment is confirmed, a QR code is **automatically generated** using the unified `PaymentSuccessService`:

```python
from payments.services.payment_success_service import PaymentSuccessService

qr_code, error = PaymentSuccessService.handle_payment_success(
    payment=payment,
    send_notification=True
)
```

**Key Points:**
- Uses `get_or_create()` to ensure **one QR code per vehicle per tax year**
- The same QR code is reused if payment method changes (e.g., cash payment then online payment)
- QR code contains a unique `token` for verification
- QR code is valid for 365 days from payment date

### 3. QR Code Verification

The generated QR code uses the **same verification system** for all payment methods:

**QR Code URL Format:**
```
/app/qr-verification/?code={qr_code_token}
```

**Verification Endpoint:**
- URL: `/app/qr-verification/`
- Method: POST (AJAX) or GET (with ?code= parameter)
- Public: Yes (no authentication required)

**How it Works:**
1. QR code contains the verification URL with token
2. When scanned, user is directed to `/app/qr-verification/?code={token}`
3. System looks up QR code by `token` field
4. System verifies:
   - QR code is active (`est_actif=True`)
   - QR code is not expired (`date_expiration > now`)
   - Payment exists and is paid (`statut='PAYE'` or `'EXONERE'`)

### 4. Notification
After payment success, a notification is sent to the vehicle owner:
- **Cash**: `create_cash_payment_notification()` (includes collector info)
- **MVola**: `create_payment_confirmation_notification()`
- **Stripe**: `create_payment_confirmation_notification()`

## QR Code Model

The `QRCode` model is shared across all payment methods:

```python
class QRCode(models.Model):
    vehicule_plaque = ForeignKey(Vehicule)
    annee_fiscale = PositiveIntegerField()
    token = CharField(unique=True)  # Used for verification
    date_expiration = DateTimeField()
    est_actif = BooleanField()
    # ... other fields
```

**Unique Constraint:** `unique_together = [['vehicule_plaque', 'annee_fiscale']]`

This ensures:
- One QR code per vehicle per tax year
- Same QR code regardless of payment method
- QR code can be reused if payment is made via different methods

## Payment Methods Implementation

### Cash Payment
```python
# In cash_payment_service.py
if not requires_approval:
    PaymentSuccessService.handle_payment_success(payment, send_notification=True)

# Or after admin approval
PaymentSuccessService.handle_payment_success(payment, send_notification=True)
```

### MVola Payment
```python
# In mvola_views.py callback
if mvola_transaction_status.lower() in ['completed', 'success', 'successful']:
    payment.statut = 'PAYE'
    payment.save()
    PaymentSuccessService.handle_payment_success(payment, send_notification=False)
```

### Stripe Payment
```python
# In payments/views.py webhook handler
def _handle_payment_intent_succeeded(payment_intent):
    paiement.statut = 'PAYE'
    paiement.save()
    PaymentSuccessService.handle_payment_success(paiement, send_notification=True)
```

## Verification Flow

1. **User pays tax** (Cash, MVola, or Stripe)
2. **Payment confirmed** → Status set to `PAYE`
3. **QR code generated** → Unique token created
4. **QR code printed/downloaded** → Contains verification URL
5. **QR code scanned** → Redirects to `/app/qr-verification/?code={token}`
6. **System verifies** → Checks QR code validity and payment status
7. **Result displayed** → Shows vehicle info, payment status, expiration date

## Key Benefits

1. **Consistency**: All payment methods use the same workflow
2. **Reusability**: Same QR code for same vehicle/tax year regardless of payment method
3. **Unified Verification**: One verification endpoint for all payment types
4. **Automatic Generation**: QR codes are generated automatically, no manual step needed
5. **Error Handling**: Unified error handling and logging

## Testing

To test the unified workflow:

1. **Cash Payment:**
   - Make a cash payment (no approval needed)
   - Verify QR code is generated automatically
   - Check QR code token works at `/app/qr-verification/?code={token}`

2. **MVola Payment:**
   - Initiate MVola payment
   - Complete payment on phone
   - Verify QR code is generated in callback
   - Check QR code token works at `/app/qr-verification/?code={token}`

3. **Stripe Payment:**
   - Initiate Stripe payment
   - Complete payment
   - Verify QR code is generated in webhook
   - Check QR code token works at `/app/qr-verification/?code={token}`

## QR Code Verification URL

The QR code verification URL format is:
```
/app/qr-verification/?code={qr_code_token}
```

Where `{qr_code_token}` is the unique token generated by the QRCode model.

This URL is:
- **Public**: No authentication required
- **Secure**: Token is unique and cannot be guessed
- **Verifiable**: System checks QR code validity and payment status
- **Consistent**: Same format for all payment methods

## Summary

✅ **Same workflow** for all payment methods (Cash, MVola, Stripe)
✅ **Same QR code** for same vehicle/tax year (regardless of payment method)
✅ **Same verification** endpoint (`/app/qr-verification/?code={token}`)
✅ **Automatic generation** of QR codes after payment confirmation
✅ **Unified service** (`PaymentSuccessService`) handles all payment success logic

