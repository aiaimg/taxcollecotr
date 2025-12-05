# Current Payment System - Complete Explanation

## Overview

Your platform is a **vehicle tax collection system** for Madagascar (using Ariary currency). The system currently handles **online digital payments** and we're now adding **in-person cash payment** capabilities.

---

## Current Payment Architecture

### 1. **Core Payment Model: `PaiementTaxe`**

This is the central model that records ALL tax payments, regardless of payment method.

**Key Fields:**
- `vehicule_plaque` - Links to the vehicle being taxed (ForeignKey to Vehicule model)
- `annee_fiscale` - The tax year (e.g., 2025)
- `montant_du_ariary` - Amount owed in Ariary (Madagascar currency)
- `montant_paye_ariary` - Amount actually paid
- `statut` - Payment status:
  - `IMPAYE` - Unpaid
  - `EN_ATTENTE` - Pending
  - `PAYE` - Paid
  - `EXONERE` - Exempt
  - `ANNULE` - Cancelled
- `transaction_id` - Unique transaction ID (auto-generated: TX + 10 random chars)
- `methode_paiement` - Payment method (NOW includes 'cash'):
  - `mvola` - MVola (mobile money)
  - `orange_money` - Orange Money (mobile money)
  - `airtel_money` - Airtel Money (mobile money)
  - `carte_bancaire` - Bank card (Stripe)
  - **`cash`** - Cash (NEW - what we're implementing)

**Stripe-Specific Fields:**
- `stripe_payment_intent_id` - Stripe payment intent ID
- `stripe_customer_id` - Stripe customer ID
- `stripe_charge_id` - Stripe charge ID
- `stripe_status` - Stripe payment status
- `stripe_receipt_url` - URL to Stripe receipt
- `billing_email`, `billing_name` - Billing information

**NEW Cash-Specific Field:**
- `collected_by` - ForeignKey to `AgentPartenaireProfile` (the agent who collected the cash)

**Important Constraint:**
- `unique_together = [['vehicule_plaque', 'annee_fiscale']]` - One payment per vehicle per year

---

### 2. **QR Code System: `QRCode` Model**

Used for payment verification (already exists, we'll reuse it for cash receipts).

**Key Fields:**
- `vehicule_plaque` - Vehicle reference
- `annee_fiscale` - Tax year
- `token` - Unique verification token (32 random chars)
- `date_expiration` - When QR code expires
- `est_actif` - Is active
- `nombre_scans` - Number of times scanned
- `est_valide()` - Method to check if QR code is valid

**Usage:**
- Generated when payment is completed
- Printed on receipts
- Can be scanned to verify payment authenticity
- Links to the payment record

---

### 3. **Current Payment Methods**

#### A. **Mobile Money (MVola, Orange Money, Airtel Money)**
- Handled by `MobileMoneyService` classes in `payments/services.py`
- Each service has methods:
  - `initiate_payment()` - Start payment process
  - `check_payment_status()` - Check if payment completed
  - `process_callback()` - Handle payment provider callback
- Payment flow:
  1. User selects vehicle and year
  2. System calculates tax amount
  3. User chooses mobile money provider
  4. System initiates payment with provider API
  5. User completes payment on their phone
  6. Provider sends callback to confirm
  7. System updates `PaiementTaxe` status to 'PAYE'

#### B. **Stripe (Bank Cards)**
- Handled by Stripe integration
- Uses `StripeConfig` model for API keys
- Payment flow:
  1. User selects vehicle and year
  2. System creates Stripe Payment Intent
  3. User enters card details
  4. Stripe processes payment
  5. Webhook confirms payment
  6. System updates `PaiementTaxe` with Stripe details

---

## What We're Adding: Cash Payment System

### New Models Created

#### 1. **`CashSystemConfig`** (Singleton)
Configuration for the entire cash payment system:
- `default_commission_rate` - Default commission % for agents (2%)
- `dual_verification_threshold` - Amount requiring admin approval (500,000 Ar)
- `reconciliation_tolerance` - Acceptable discrepancy (1,000 Ar)
- `session_timeout_hours` - Session expiration time (12 hours)
- `void_time_limit_minutes` - Time limit to void transactions (30 min)
- `receipt_footer_text` - Custom text for receipts

#### 2. **`AgentPartenaireProfile`**
Profile for authorized cash collection agents:
- `user` - Links to Django User account
- `agent_id` - Unique agent ID (auto-generated: AG + 8 chars)
- `full_name` - Agent's full name
- `phone_number` - Contact number
- `collection_location` - Where they collect payments
- `commission_rate` - Custom commission rate (optional)
- `use_default_commission` - Use system default or custom rate
- `is_active` - Can accept payments or not
- `get_commission_rate()` - Returns effective commission rate

#### 3. **`CashSession`**
Tracks a collection period for an agent:
- `collector` - Which agent
- `session_number` - Unique session ID (SESS-YYYYMMDD-XXXXXX)
- `opening_balance` - Starting cash amount
- `opening_time` - When session opened
- `closing_balance` - Actual cash counted at end
- `expected_balance` - Calculated expected cash
- `discrepancy_amount` - Difference between expected and actual
- `total_commission` - Total commission earned in session
- `status` - open, closed, or reconciled

**Purpose:** Ensures accountability - agent must account for all cash collected during their shift.

#### 4. **`CashTransaction`**
Individual cash payment transaction:
- `session` - Which cash session
- `payment` - Links to `PaiementTaxe` (OneToOne)
- `transaction_number` - Unique ID (CASH-YYYYMMDD-XXXXXX)
- `customer_name` - Customer who paid
- `vehicle_plate` - Vehicle being taxed
- `tax_amount` - Tax amount
- `amount_tendered` - Cash given by customer
- `change_given` - Change returned
- `commission_amount` - Agent's commission
- `collector` - Agent who collected
- `requires_approval` - If amount > threshold
- `approved_by` - Admin who approved (if needed)
- `receipt_printed` - Was receipt printed
- `is_voided` - Was transaction cancelled
- `notes` - Additional notes

#### 5. **`CashReceipt`**
Receipt record for cash payments:
- `transaction` - Links to CashTransaction
- `receipt_number` - Unique receipt ID (REC-YYYYMMDD-XXXXXX)
- `qr_code` - Links to QRCode for verification
- `vehicle_registration` - Vehicle plate
- `vehicle_owner` - Owner name
- `tax_year` - Year paid for
- `tax_amount`, `amount_paid`, `change_given` - Payment details
- `collector_name`, `collector_id` - Agent info
- `payment_date` - When paid
- `qr_code_data` - QR code content
- `is_duplicate` - Is this a reprint
- `original_receipt` - If duplicate, links to original

#### 6. **`CommissionRecord`**
Tracks commission earnings:
- `collector` - Agent earning commission
- `session` - Session it was earned in
- `transaction` - Transaction that generated it
- `tax_amount` - Tax amount
- `commission_rate` - Rate applied
- `commission_amount` - Amount earned
- `payment_status` - pending, paid, or cancelled
- `paid_date`, `paid_by` - When/who paid commission

#### 7. **`CashAuditLog`**
Immutable audit trail with hash chain:
- `action_type` - What happened (session_open, transaction_create, etc.)
- `user` - Who did it
- `session`, `transaction` - Related records
- `action_data` - JSON details
- `ip_address`, `user_agent` - Context
- `previous_hash` - Hash of previous log entry
- `current_hash` - Hash of this entry (SHA-256)
- `timestamp` - When it happened

**Security:** Uses blockchain-like hash chain to detect tampering.

---

## How Cash Payments Will Work

### Workflow for New Customer:

1. **Agent opens cash session**
   - Agent logs in
   - Opens session with starting cash amount
   - System creates `CashSession` record

2. **Customer arrives to pay**
   - Agent creates new customer account (User + UserProfile)
   - Agent registers vehicle (Vehicule model)
   - System calculates tax using `TaxCalculationService`

3. **Agent processes payment**
   - Agent enters amount customer gave
   - System calculates change
   - If amount > threshold, requires admin approval
   - System creates:
     - `PaiementTaxe` (methode_paiement='cash', statut='PAYE')
     - `CashTransaction` (linked to session and payment)
     - `CommissionRecord` (agent's commission)
     - `QRCode` (for verification)
     - `CashReceipt` (with QR code)
   - Updates session totals

4. **Receipt generation**
   - System generates receipt with:
     - Vehicle and owner info
     - Payment details
     - Agent info
     - QR code for verification
   - Receipt can be printed or downloaded as PDF

5. **End of day**
   - Agent closes session
   - Counts physical cash
   - System compares with expected amount
   - If discrepancy > tolerance, requires admin approval
   - Session marked as 'closed'

6. **Admin reconciliation**
   - Admin reviews all closed sessions
   - Verifies cash collected matches records
   - Marks sessions as 'reconciled'
   - Approves commission payments

### Workflow for Existing Customer:

1. Agent searches for customer by name/phone/plate
2. System displays customer's vehicles
3. Agent selects vehicle to pay tax for
4. System calculates tax
5. Rest of process same as above (steps 3-6)

---

## Key Differences from Online Payments

| Aspect | Online Payments | Cash Payments |
|--------|----------------|---------------|
| **Who initiates** | Customer themselves | Agent Partenaire |
| **Payment method** | Mobile money, Stripe | Physical cash |
| **Verification** | Automatic via API | Manual by agent |
| **Receipt** | Digital only | Printed + digital |
| **Commission** | None | Agent earns commission |
| **Approval** | Automatic | May require admin approval |
| **Reconciliation** | Not needed | Daily reconciliation required |
| **Audit trail** | Standard logs | Enhanced hash-chain audit |
| **Customer account** | Must exist | Can be created on-the-spot |

---

## Integration Points

### With Existing Systems:

1. **Vehicles App**
   - Uses `Vehicule` model for vehicle data
   - Uses `TaxCalculationService` to calculate tax amounts
   - Can create new vehicles during cash payment

2. **Core App**
   - Uses `User` model for customer accounts
   - Uses `UserProfile` for customer details
   - Can create new users during cash payment

3. **Notifications App**
   - Will send notifications when:
     - Payment completed
     - Approval required
     - Session closed
     - Discrepancy detected

4. **Administration App**
   - Admin console will show:
     - Agent management
     - Session monitoring
     - Transaction approvals
     - Reconciliation reports
     - Commission reports

---

## Security Features

1. **Dual Verification**
   - Large transactions require admin approval
   - Prevents fraud

2. **Session Management**
   - All transactions tied to sessions
   - Sessions must be opened/closed
   - Ensures accountability

3. **Audit Trail**
   - Every action logged
   - Hash chain prevents tampering
   - Immutable records

4. **Reconciliation**
   - Daily cash counting
   - Discrepancy tracking
   - Admin oversight

5. **QR Code Verification**
   - Receipts have QR codes
   - Can be scanned to verify authenticity
   - Links to payment record

---

## What's Next in Implementation

We've completed **Task 1** (models and migrations). Next tasks:

- **Task 2:** Services (payment processing logic)
- **Task 3:** Forms (user input)
- **Task 4:** Agent views (for cash collectors)
- **Task 5:** Admin views (for oversight)
- **Task 6:** Templates (UI)
- **Task 7:** URLs (routing)
- **Task 8:** Permissions (access control)
- **Task 9:** JavaScript (interactivity)
- **Task 10:** Integration (connect to existing systems)
- **Task 11:** Management commands (automation)

---

## Summary

Your current system handles **online digital payments** (mobile money + Stripe) where customers pay themselves through the web platform.

The new cash payment system adds **in-person cash collection** by authorized agents who:
- Accept physical cash from customers
- Can register new customers on-the-spot
- Earn commissions on collections
- Must reconcile cash daily
- Have all actions audited

Both systems use the same core `PaiementTaxe` model, just with different `methode_paiement` values. The cash system adds extra layers of accountability, security, and commission tracking that aren't needed for online payments.
