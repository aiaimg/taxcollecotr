# Cash Payment System Design Document

## Overview

The Cash Payment System enables authorized partner agents (Agent Partenaire) to accept physical currency payments for vehicle taxes in person. The system integrates with the existing Django-based tax collection platform, providing a complete workflow from customer registration to receipt generation with QR code verification.

**Payment Methods Context:**
- **Cash (this spec)**: Handled in-person by Agent Partenaire
- **Mobile Money** (MVola, Airtel Money, Orange Money): Handled online by customers through existing system
- **Stripe**: Handled online by customers through existing system

### Key Features

- Cash payment processing with automatic change calculation
- Customer and vehicle registration workflow by Agent Partenaire
- Receipt generation with QR codes
- Commission tracking for Agent Partenaire
- Cash session management
- Dual verification for large transactions
- Real-time audit trails
- Daily reconciliation and reporting
- Role-based access control

### Integration Points

The cash payment system integrates with existing modules:
- **payments** app: Extends PaiementTaxe model (adds 'cash' to existing payment methods: mvola, orange_money, airtel_money, carte_bancaire)
- **vehicles** app: Uses Vehicule and VehicleType models
- **core** app: Uses User and UserProfile models
- **administration** app: Extends for Agent Partenaire management
- **notifications** app: Sends payment confirmations

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Cash Payment System                      │
│                   (Agent Partenaire Interface)               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Agent     │  │   Customer   │  │   Receipt    │      │
│  │  Partenaire  │  │  Management  │  │  Generation  │      │
│  │   Interface  │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Cash       │  │  Commission  │  │  Audit &     │      │
│  │  Session     │  │  Tracking    │  │  Reporting   │      │
│  │  Management  │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Payments   │    │   Vehicles   │    │     Core     │
│     App      │    │     App      │    │     App      │
│  (MVola,     │    │              │    │              │
│   Airtel,    │    │              │    │              │
│   Orange,    │    │              │    │              │
│   Stripe,    │    │              │    │              │
│   Cash)      │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```


### Technology Stack

- **Backend**: Django 5.x with Python 3.x
- **Database**: PostgreSQL (existing)
- **Frontend**: Django Templates with Bootstrap 5 (Velzon theme)
- **QR Code**: qrcode library (already in use)
- **PDF Generation**: ReportLab (already in use)
- **Authentication**: Django Auth with role-based permissions

## Components and Interfaces

### 1. Data Models

#### AgentPartenaireProfile (New Model)
Extends the administration app to manage agent partenaires who accept cash payments.

```python
class AgentPartenaireProfile(models.Model):
    """Profile for agent partenaires authorized to accept cash payments"""
    user = ForeignKey(User)  # Links to Django User
    agent_id = CharField(unique=True)  # Unique agent identifier
    full_name = CharField()
    phone_number = CharField()
    collection_location = CharField()  # Where they collect taxes
    commission_rate = DecimalField(null=True, blank=True)  # Agent-specific rate (overrides default)
    use_default_commission = BooleanField(default=True)  # Use system default or custom rate
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    created_by = ForeignKey(User, related_name='created_agents')  # Admin who created
    
    def get_commission_rate(self):
        """Get effective commission rate (custom or default)"""
        if self.use_default_commission or not self.commission_rate:
            return CashSystemConfig.get_config().default_commission_rate
        return self.commission_rate
```

#### CashSession (New Model)
Tracks cash collection sessions for each agent partenaire.

```python
class CashSession(models.Model):
    """Cash collection session for a agent partenaire"""
    id = UUIDField(primary_key=True)
    collector = ForeignKey(AgentPartenaireProfile)
    session_number = CharField(unique=True)  # Auto-generated
    opening_balance = DecimalField()  # Starting cash
    opening_time = DateTimeField()
    closing_balance = DecimalField(null=True)  # Actual cash counted
    expected_balance = DecimalField(null=True)  # Calculated
    closing_time = DateTimeField(null=True)
    discrepancy_amount = DecimalField(default=0)
    discrepancy_notes = TextField(blank=True)
    total_commission = DecimalField(default=0)
    status = CharField(choices=['open', 'closed', 'reconciled'])
    approved_by = ForeignKey(User, null=True)  # Admin who approved
    created_at = DateTimeField(auto_now_add=True)
```


#### CashTransaction (New Model)
Records individual cash payment transactions.

```python
class CashTransaction(models.Model):
    """Individual cash payment transaction"""
    id = UUIDField(primary_key=True)
    session = ForeignKey(CashSession)
    payment = ForeignKey(PaiementTaxe)  # Links to existing payment model
    transaction_number = CharField(unique=True)
    customer_name = CharField()  # From vehicle owner
    vehicle_plate = CharField()
    tax_amount = DecimalField()
    amount_tendered = DecimalField()
    change_given = DecimalField()
    commission_amount = DecimalField()
    collector = ForeignKey(AgentPartenaireProfile)
    requires_approval = BooleanField(default=False)  # For large amounts
    approved_by = ForeignKey(User, null=True)
    approval_time = DateTimeField(null=True)
    transaction_time = DateTimeField(auto_now_add=True)
    receipt_printed = BooleanField(default=False)
    receipt_print_time = DateTimeField(null=True)
    notes = TextField(blank=True)
```

#### CashReceipt (New Model)
Stores receipt information for cash payments.

```python
class CashReceipt(models.Model):
    """Cash payment receipt with QR code"""
    id = UUIDField(primary_key=True)
    transaction = OneToOneField(CashTransaction)
    receipt_number = CharField(unique=True)
    qr_code = ForeignKey(QRCode)  # Links to existing QR code model
    vehicle_registration = CharField()
    vehicle_owner = CharField()
    tax_year = IntegerField()
    tax_amount = DecimalField()
    amount_paid = DecimalField()
    change_given = DecimalField()
    collector_name = CharField()
    collector_id = CharField()
    payment_date = DateTimeField()
    qr_code_data = TextField()  # QR code content
    is_duplicate = BooleanField(default=False)
    original_receipt = ForeignKey('self', null=True)
    created_at = DateTimeField(auto_now_add=True)
```


#### CommissionRecord (New Model)
Tracks commission earnings for agent partenaires.

```python
class CommissionRecord(models.Model):
    """Commission tracking for agent partenaires"""
    id = UUIDField(primary_key=True)
    collector = ForeignKey(AgentPartenaireProfile)
    session = ForeignKey(CashSession)
    transaction = ForeignKey(CashTransaction)
    tax_amount = DecimalField()
    commission_rate = DecimalField()
    commission_amount = DecimalField()
    payment_status = CharField(choices=['pending', 'paid', 'cancelled'])
    paid_date = DateTimeField(null=True)
    paid_by = ForeignKey(User, null=True)
    created_at = DateTimeField(auto_now_add=True)
```

#### CashAuditLog (New Model)
Immutable audit trail for all cash operations.

```python
class CashAuditLog(models.Model):
    """Immutable audit trail for cash operations"""
    id = UUIDField(primary_key=True)
    action_type = CharField(choices=[
        'session_open', 'session_close', 'transaction_create',
        'transaction_approve', 'receipt_print', 'reconciliation'
    ])
    user = ForeignKey(User)
    session = ForeignKey(CashSession, null=True)
    transaction = ForeignKey(CashTransaction, null=True)
    action_data = JSONField()  # Stores action details
    ip_address = GenericIPAddressField()
    user_agent = TextField()
    previous_hash = CharField()  # Hash of previous log entry
    current_hash = CharField()  # Hash of this entry
    timestamp = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
```

### 2. Extended Models

#### PaiementTaxe (Extended)
Add cash payment support to existing payment model.

```python
# Add to existing METHODE_PAIEMENT_CHOICES:
('cash', 'Espèces')

# Add new fields:
cash_transaction = ForeignKey(CashTransaction, null=True, blank=True)
collected_by = ForeignKey(AgentPartenaireProfile, null=True, blank=True)
```


### 3. Services Layer

#### CashPaymentService
Core service for processing cash payments.

```python
class CashPaymentService:
    """Service for processing cash payments"""
    
    @staticmethod
    def calculate_change(tax_amount, amount_tendered):
        """Calculate change with validation"""
        # Returns: (change_amount, is_valid, error_message)
    
    @staticmethod
    def create_cash_payment(collector, vehicle, customer_data, amount_tendered):
        """Create a new cash payment transaction"""
        # 1. Validate collector session is open
        # 2. Calculate tax amount
        # 3. Validate tendered amount
        # 4. Create or get customer account
        # 5. Create/update vehicle record
        # 6. Create PaiementTaxe record
        # 7. Create CashTransaction record
        # 8. Calculate commission
        # 9. Update session totals
        # 10. Create audit log
        # Returns: (transaction, receipt, error)
    
    @staticmethod
    def process_existing_customer_payment(collector, vehicle_plate, amount_tendered):
        """Process payment for existing customer"""
        # Similar to create_cash_payment but skips customer/vehicle creation
    
    @staticmethod
    def requires_dual_verification(amount):
        """Check if amount requires admin approval"""
        # Returns: Boolean based on configured threshold
    
    @staticmethod
    def approve_transaction(transaction, admin_user):
        """Approve a transaction requiring dual verification"""
```

#### CashSessionService
Manages cash collection sessions.

```python
class CashSessionService:
    """Service for managing cash sessions"""
    
    @staticmethod
    def open_session(collector, opening_balance):
        """Open a new cash collection session"""
        # 1. Validate no open session exists
        # 2. Generate session number
        # 3. Create CashSession record
        # 4. Create audit log
        # Returns: session
    
    @staticmethod
    def close_session(session, closing_balance, counted_by):
        """Close a cash session"""
        # 1. Calculate expected balance
        # 2. Calculate discrepancy
        # 3. Update session status
        # 4. Create audit log
        # Returns: (session, discrepancy_amount)
    
    @staticmethod
    def get_active_session(collector):
        """Get collector's active session"""
    
    @staticmethod
    def calculate_session_totals(session):
        """Calculate session totals (transactions, commission, etc.)"""
```


#### ReceiptService
Handles receipt generation and printing.

```python
class ReceiptService:
    """Service for generating receipts"""
    
    @staticmethod
    def generate_receipt(transaction):
        """Generate receipt with QR code"""
        # 1. Create QR code for payment verification
        # 2. Create CashReceipt record
        # 3. Generate receipt number
        # 4. Store QR code data
        # Returns: receipt
    
    @staticmethod
    def generate_receipt_pdf(receipt):
        """Generate printable PDF receipt"""
        # Uses ReportLab to create PDF with:
        # - Receipt header
        # - Vehicle and owner information
        # - Payment details
        # - QR code image
        # - Collector information
        # Returns: PDF file
    
    @staticmethod
    def reprint_receipt(receipt, requested_by):
        """Reprint existing receipt (marked as duplicate)"""
        # Creates duplicate receipt record
        # Logs reprint action
```

#### CommissionService
Manages commission calculations and tracking.

```python
class CommissionService:
    """Service for commission management"""
    
    @staticmethod
    def calculate_commission(tax_amount, commission_rate):
        """Calculate commission amount"""
    
    @staticmethod
    def record_commission(transaction, collector, session):
        """Record commission for a transaction"""
    
    @staticmethod
    def get_session_commission(session):
        """Get total commission for a session"""
    
    @staticmethod
    def get_collector_commission_report(collector, start_date, end_date):
        """Generate commission report for collector"""
```


#### ReconciliationService
Handles daily reconciliation processes.

```python
class ReconciliationService:
    """Service for cash reconciliation"""
    
    @staticmethod
    def generate_daily_report(date):
        """Generate daily cash collection report"""
        # Aggregates all sessions for the day
        # Returns: report data
    
    @staticmethod
    def reconcile_day(date, admin_user, physical_count, notes):
        """Perform end-of-day reconciliation"""
        # 1. Get all closed sessions for the day
        # 2. Calculate expected total
        # 3. Compare with physical count
        # 4. Flag discrepancies
        # 5. Require approval if over tolerance
        # 6. Mark day as reconciled
    
    @staticmethod
    def get_discrepancy_report(start_date, end_date):
        """Generate discrepancy tracking report"""
```

#### AuditService
Manages audit trail and tamper detection.

```python
class AuditService:
    """Service for audit trail management"""
    
    @staticmethod
    def log_action(action_type, user, data, session=None, transaction=None):
        """Create audit log entry with hash chain"""
        # 1. Get previous log entry
        # 2. Calculate hash of previous entry
        # 3. Create new log with previous hash
        # 4. Calculate current hash
        # 5. Store encrypted data
    
    @staticmethod
    def verify_audit_trail():
        """Verify integrity of audit trail"""
        # Checks hash chain for tampering
        # Returns: (is_valid, tampered_entries)
    
    @staticmethod
    def get_audit_trail(filters):
        """Retrieve audit trail with filters"""
```


### 4. Views and URLs

#### Tax Collector Views

```python
# Cash Session Management
class CashSessionOpenView(LoginRequiredMixin, CreateView)
class CashSessionCloseView(LoginRequiredMixin, UpdateView)
class CashSessionDetailView(LoginRequiredMixin, DetailView)

# Payment Processing
class CashPaymentCreateView(LoginRequiredMixin, CreateView)
    # Handles both new and existing customers
class CashPaymentSearchCustomerView(LoginRequiredMixin, View)
    # AJAX endpoint for customer search
class CashPaymentCalculateTaxView(LoginRequiredMixin, View)
    # AJAX endpoint for tax calculation

# Receipt Management
class ReceiptPrintView(LoginRequiredMixin, View)
class ReceiptReprintView(LoginRequiredMixin, View)
class ReceiptDownloadView(LoginRequiredMixin, View)

# Commission Tracking
class CollectorCommissionView(LoginRequiredMixin, ListView)
class CollectorDashboardView(LoginRequiredMixin, TemplateView)
```

#### Admin Staff Views

```python
# Collector Management
class CollectorListView(LoginRequiredMixin, UserPassesTestMixin, ListView)
class CollectorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView)
class CollectorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView)
class CollectorDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView)

# Transaction Approval
class TransactionApprovalListView(LoginRequiredMixin, UserPassesTestMixin, ListView)
class TransactionApproveView(LoginRequiredMixin, UserPassesTestMixin, View)

# Reconciliation
class DailyReconciliationView(LoginRequiredMixin, UserPassesTestMixin, TemplateView)
class ReconciliationReportView(LoginRequiredMixin, UserPassesTestMixin, ListView)

# Reports
class CashCollectionReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView)
class DiscrepancyReportView(LoginRequiredMixin, UserPassesTestMixin, ListView)
class CommissionReportView(LoginRequiredMixin, UserPassesTestMixin, ListView)
class AuditTrailView(LoginRequiredMixin, UserPassesTestMixin, ListView)

# Configuration
class CashSystemConfigView(LoginRequiredMixin, UserPassesTestMixin, UpdateView)
```


#### URL Structure

```python
# cash_payments/urls.py
urlpatterns = [
    # Collector URLs
    path('session/open/', CashSessionOpenView.as_view(), name='session_open'),
    path('session/<uuid:pk>/close/', CashSessionCloseView.as_view(), name='session_close'),
    path('session/<uuid:pk>/', CashSessionDetailView.as_view(), name='session_detail'),
    
    path('payment/create/', CashPaymentCreateView.as_view(), name='payment_create'),
    path('payment/search-customer/', CashPaymentSearchCustomerView.as_view(), name='search_customer'),
    path('payment/calculate-tax/', CashPaymentCalculateTaxView.as_view(), name='calculate_tax'),
    
    path('receipt/<uuid:pk>/print/', ReceiptPrintView.as_view(), name='receipt_print'),
    path('receipt/<uuid:pk>/reprint/', ReceiptReprintView.as_view(), name='receipt_reprint'),
    path('receipt/<uuid:pk>/download/', ReceiptDownloadView.as_view(), name='receipt_download'),
    
    path('commission/', CollectorCommissionView.as_view(), name='commission_list'),
    path('dashboard/', CollectorDashboardView.as_view(), name='collector_dashboard'),
    
    # Admin URLs
    path('admin/collectors/', CollectorListView.as_view(), name='collector_list'),
    path('admin/collectors/create/', CollectorCreateView.as_view(), name='collector_create'),
    path('admin/collectors/<uuid:pk>/', CollectorDetailView.as_view(), name='collector_detail'),
    path('admin/collectors/<uuid:pk>/edit/', CollectorUpdateView.as_view(), name='collector_edit'),
    
    path('admin/approvals/', TransactionApprovalListView.as_view(), name='approval_list'),
    path('admin/approvals/<uuid:pk>/approve/', TransactionApproveView.as_view(), name='approve_transaction'),
    
    path('admin/reconciliation/', DailyReconciliationView.as_view(), name='reconciliation'),
    path('admin/reconciliation/history/', ReconciliationReportView.as_view(), name='reconciliation_history'),
    
    path('admin/reports/collection/', CashCollectionReportView.as_view(), name='collection_report'),
    path('admin/reports/discrepancies/', DiscrepancyReportView.as_view(), name='discrepancy_report'),
    path('admin/reports/commission/', CommissionReportView.as_view(), name='commission_report'),
    path('admin/reports/audit/', AuditTrailView.as_view(), name='audit_trail'),
    
    path('admin/config/', CashSystemConfigView.as_view(), name='system_config'),
]
```


### 5. Forms

```python
class CashSessionOpenForm(forms.ModelForm):
    """Form for opening a cash session"""
    class Meta:
        model = CashSession
        fields = ['opening_balance']

class CashPaymentForm(forms.Form):
    """Form for processing cash payments"""
    # Customer search or new customer
    customer_search = forms.CharField(required=False)
    is_new_customer = forms.BooleanField(required=False)
    
    # New customer fields
    customer_name = forms.CharField(required=False)
    customer_phone = forms.CharField(required=False)
    customer_email = forms.EmailField(required=False)
    customer_id_number = forms.CharField(required=False)
    
    # Vehicle fields (new or existing)
    vehicle_plate = forms.CharField()
    has_plate = forms.BooleanField(initial=True)
    vehicle_type = forms.ModelChoiceField(queryset=VehicleType.objects.filter(est_actif=True))
    vehicle_brand = forms.CharField()
    vehicle_model = forms.CharField(required=False)
    vehicle_color = forms.CharField(required=False)
    engine_power_cv = forms.IntegerField()
    engine_capacity_cc = forms.IntegerField()
    energy_source = forms.ChoiceField(choices=Vehicule.SOURCE_ENERGIE_CHOICES)
    first_circulation_date = forms.DateField()
    vehicle_category = forms.ChoiceField(choices=Vehicule.CATEGORIE_CHOICES)
    owner_name = forms.CharField()
    
    # Payment fields
    tax_amount = forms.DecimalField(widget=forms.HiddenInput())
    amount_tendered = forms.DecimalField()
    
    def clean(self):
        # Validate customer data based on is_new_customer
        # Validate vehicle data
        # Validate payment amount

class CashSessionCloseForm(forms.ModelForm):
    """Form for closing a cash session"""
    class Meta:
        model = CashSession
        fields = ['closing_balance', 'discrepancy_notes']

class TransactionApprovalForm(forms.Form):
    """Form for approving transactions"""
    approval_notes = forms.CharField(widget=forms.Textarea, required=False)
    action = forms.ChoiceField(choices=[('approve', 'Approve'), ('reject', 'Reject')])

class ReconciliationForm(forms.Form):
    """Form for daily reconciliation"""
    reconciliation_date = forms.DateField()
    physical_cash_count = forms.DecimalField()
    reconciliation_notes = forms.CharField(widget=forms.Textarea, required=False)
```


### 6. Templates

#### Collector Templates
- `cash_payments/session_open.html` - Open cash session
- `cash_payments/session_detail.html` - View session details
- `cash_payments/session_close.html` - Close session
- `cash_payments/payment_create.html` - Create payment (new/existing customer)
- `cash_payments/payment_success.html` - Payment confirmation
- `cash_payments/receipt_preview.html` - Receipt preview before printing
- `cash_payments/collector_dashboard.html` - Collector dashboard
- `cash_payments/commission_list.html` - Commission history

#### Admin Templates
- `cash_payments/admin/collector_list.html` - List all collectors
- `cash_payments/admin/collector_detail.html` - Collector details
- `cash_payments/admin/collector_form.html` - Create/edit collector
- `cash_payments/admin/approval_list.html` - Pending approvals
- `cash_payments/admin/reconciliation.html` - Daily reconciliation
- `cash_payments/admin/reconciliation_history.html` - Reconciliation history
- `cash_payments/admin/collection_report.html` - Cash collection report
- `cash_payments/admin/discrepancy_report.html` - Discrepancy report
- `cash_payments/admin/commission_report.html` - Commission report
- `cash_payments/admin/audit_trail.html` - Audit trail viewer
- `cash_payments/admin/system_config.html` - System configuration

#### Shared Templates
- `cash_payments/partials/customer_search.html` - Customer search widget
- `cash_payments/partials/vehicle_form.html` - Vehicle information form
- `cash_payments/partials/payment_calculator.html` - Tax calculator widget
- `cash_payments/partials/receipt_template.html` - Receipt template


## Data Models

### Database Schema

```sql
-- Cash Collector Profile
CREATE TABLE agent_partenaire_profile (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    collector_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    phone_number VARCHAR(20),
    collection_location VARCHAR(200),
    commission_rate DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Cash Session
CREATE TABLE cash_session (
    id UUID PRIMARY KEY,
    collector_id UUID REFERENCES agent_partenaire_profile(id),
    session_number VARCHAR(50) UNIQUE NOT NULL,
    opening_balance DECIMAL(12,2) NOT NULL,
    opening_time TIMESTAMP NOT NULL,
    closing_balance DECIMAL(12,2),
    expected_balance DECIMAL(12,2),
    closing_time TIMESTAMP,
    discrepancy_amount DECIMAL(12,2) DEFAULT 0.00,
    discrepancy_notes TEXT,
    total_commission DECIMAL(12,2) DEFAULT 0.00,
    status VARCHAR(20) NOT NULL,
    approved_by_id INTEGER REFERENCES auth_user(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cash Transaction
CREATE TABLE cash_transaction (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES cash_session(id),
    payment_id UUID REFERENCES payments_paiementtaxe(id),
    transaction_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    vehicle_plate VARCHAR(20) NOT NULL,
    tax_amount DECIMAL(12,2) NOT NULL,
    amount_tendered DECIMAL(12,2) NOT NULL,
    change_given DECIMAL(12,2) NOT NULL,
    commission_amount DECIMAL(12,2) NOT NULL,
    collector_id UUID REFERENCES agent_partenaire_profile(id),
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by_id INTEGER REFERENCES auth_user(id),
    approval_time TIMESTAMP,
    transaction_time TIMESTAMP DEFAULT NOW(),
    receipt_printed BOOLEAN DEFAULT FALSE,
    receipt_print_time TIMESTAMP,
    notes TEXT
);

-- Cash Receipt
CREATE TABLE cash_receipt (
    id UUID PRIMARY KEY,
    transaction_id UUID UNIQUE REFERENCES cash_transaction(id),
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    qr_code_id UUID REFERENCES payments_qrcode(id),
    vehicle_registration VARCHAR(20) NOT NULL,
    vehicle_owner VARCHAR(200) NOT NULL,
    tax_year INTEGER NOT NULL,
    tax_amount DECIMAL(12,2) NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL,
    change_given DECIMAL(12,2) NOT NULL,
    collector_name VARCHAR(200) NOT NULL,
    collector_id VARCHAR(50) NOT NULL,
    payment_date TIMESTAMP NOT NULL,
    qr_code_data TEXT NOT NULL,
    is_duplicate BOOLEAN DEFAULT FALSE,
    original_receipt_id UUID REFERENCES cash_receipt(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Commission Record
CREATE TABLE commission_record (
    id UUID PRIMARY KEY,
    collector_id UUID REFERENCES agent_partenaire_profile(id),
    session_id UUID REFERENCES cash_session(id),
    transaction_id UUID REFERENCES cash_transaction(id),
    tax_amount DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(5,2) NOT NULL,
    commission_amount DECIMAL(12,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    paid_date TIMESTAMP,
    paid_by_id INTEGER REFERENCES auth_user(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cash Audit Log
CREATE TABLE cash_audit_log (
    id UUID PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES auth_user(id),
    session_id UUID REFERENCES cash_session(id),
    transaction_id UUID REFERENCES cash_transaction(id),
    action_data JSONB NOT NULL,
    ip_address INET,
    user_agent TEXT,
    previous_hash VARCHAR(64),
    current_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_cash_session_collector ON cash_session(collector_id);
CREATE INDEX idx_cash_session_status ON cash_session(status);
CREATE INDEX idx_cash_transaction_session ON cash_transaction(session_id);
CREATE INDEX idx_cash_transaction_payment ON cash_transaction(payment_id);
CREATE INDEX idx_cash_transaction_time ON cash_transaction(transaction_time);
CREATE INDEX idx_cash_receipt_transaction ON cash_receipt(transaction_id);
CREATE INDEX idx_commission_collector ON commission_record(collector_id);
CREATE INDEX idx_commission_session ON commission_record(session_id);
CREATE INDEX idx_audit_log_timestamp ON cash_audit_log(timestamp);
CREATE INDEX idx_audit_log_user ON cash_audit_log(user_id);
```


## Error Handling

### Error Types and Responses

1. **Session Errors**
   - No active session: Redirect to session open page
   - Session already open: Display error message
   - Session closed: Cannot process payments

2. **Payment Errors**
   - Insufficient amount: Display error with required amount
   - Invalid vehicle data: Show validation errors
   - Duplicate payment: Check existing payment for year
   - Tax calculation error: Log and show user-friendly message

3. **Approval Errors**
   - No admin available: Queue for approval
   - Approval timeout: Notify admin
   - Approval rejected: Void transaction

4. **Receipt Errors**
   - Print failure: Allow retry, save digital copy
   - QR code generation failure: Log error, retry
   - Duplicate receipt: Mark as duplicate

5. **Reconciliation Errors**
   - Discrepancy over tolerance: Require admin approval
   - Missing sessions: Flag for investigation
   - Calculation errors: Log and alert admin

### Error Logging

All errors are logged to:
- Django logging system
- CashAuditLog for cash-related errors
- Email notifications for critical errors
- Admin dashboard alerts


## Testing Strategy

### Unit Tests

1. **Model Tests**
   - AgentPartenaireProfile creation and validation
   - CashSession lifecycle (open, close, reconcile)
   - CashTransaction creation and validation
   - Commission calculation accuracy
   - Audit log hash chain integrity

2. **Service Tests**
   - CashPaymentService.calculate_change()
   - CashPaymentService.create_cash_payment()
   - CashSessionService.open_session()
   - CashSessionService.close_session()
   - ReceiptService.generate_receipt()
   - CommissionService.calculate_commission()
   - ReconciliationService.reconcile_day()
   - AuditService.log_action()
   - AuditService.verify_audit_trail()

3. **Form Tests**
   - CashPaymentForm validation
   - CashSessionOpenForm validation
   - ReconciliationForm validation

### Integration Tests

1. **Payment Workflow**
   - New customer registration and payment
   - Existing customer payment
   - Payment with dual verification
   - Receipt generation and printing

2. **Session Management**
   - Open session → Process payments → Close session
   - Multiple collectors with concurrent sessions
   - Session reconciliation with discrepancies

3. **Commission Tracking**
   - Commission calculation across multiple transactions
   - Commission report generation
   - Variable commission rates

4. **Audit Trail**
   - Hash chain integrity across multiple operations
   - Tamper detection
   - Audit log retrieval and filtering

### End-to-End Tests

1. **Complete Tax Collection Flow**
   - Collector opens session
   - Customer arrives (new)
   - Collector registers customer and vehicle
   - System calculates tax
   - Customer pays cash
   - System calculates change
   - Receipt printed with QR code
   - Commission recorded
   - Collector closes session
   - Admin reconciles day

2. **Existing Customer Flow**
   - Collector searches for customer
   - Selects vehicle
   - Processes payment
   - Prints receipt

3. **Dual Verification Flow**
   - Large payment requires approval
   - Admin receives notification
   - Admin reviews and approves
   - Payment completes


## Security Considerations

### Authentication and Authorization

1. **Role-Based Access Control**
   - Tax Collector role: Can process payments, manage own sessions
   - Admin Staff role: Full access to all features
   - Permissions checked at view level using UserPassesTestMixin
   - API endpoints protected with authentication decorators

2. **Session Security**
   - Only one active session per collector
   - Session timeout after inactivity
   - Session tied to specific collector
   - Cannot modify closed sessions

3. **Transaction Security**
   - Immutable transaction records
   - Dual verification for large amounts
   - Admin approval required for refunds
   - All actions logged in audit trail

### Data Protection

1. **Encryption**
   - Sensitive data encrypted at rest (AES-256)
   - Audit log data encrypted
   - HTTPS for all communications
   - Database connection encrypted

2. **Data Integrity**
   - Hash chain for audit trail
   - Cryptographic hashing (SHA-256)
   - Tamper detection on audit logs
   - Database constraints and validations

3. **Access Logging**
   - All cash operations logged
   - IP address and user agent recorded
   - Failed access attempts tracked
   - Suspicious activity alerts

### Compliance

1. **Financial Regulations**
   - 7-year data retention
   - Complete audit trail
   - Tamper-proof records
   - Reconciliation requirements

2. **Privacy**
   - Customer data protection
   - Access control to sensitive information
   - Data minimization
   - Right to access/deletion (GDPR-like)


## Configuration

### System Configuration Model

```python
class CashSystemConfig(models.Model):
    """System-wide configuration for cash payments - Managed by Admin Staff"""
    
    # Dual Verification
    dual_verification_threshold = DecimalField(default=500000)  # Ariary
    dual_verification_enabled = BooleanField(default=True)
    
    # Commission (Admin-configurable)
    default_commission_rate = DecimalField(default=2.5)  # Default percentage for all agents
    commission_calculation_method = CharField(
        choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage'
    )
    allow_custom_agent_rates = BooleanField(default=True)  # Allow per-agent custom rates
    
    # Reconciliation
    reconciliation_tolerance = DecimalField(default=1000)  # Ariary
    require_approval_over_tolerance = BooleanField(default=True)
    
    # Receipt
    receipt_format = CharField(choices=[('a4', 'A4'), ('thermal', 'Thermal')])
    include_qr_code = BooleanField(default=True)
    receipt_copies = IntegerField(default=1)
    
    # Session
    session_timeout_minutes = IntegerField(default=480)  # 8 hours
    allow_multiple_sessions = BooleanField(default=False)
    
    # Currency
    currency_code = CharField(default='MGA')
    currency_symbol = CharField(default='Ar')
    currency_decimals = IntegerField(default=2)
    
    # Audit
    audit_log_retention_days = IntegerField(default=2555)  # 7 years
    enable_hash_chain = BooleanField(default=True)
    
    # Metadata
    modified_by = ForeignKey(User, null=True)  # Last admin who modified
    modified_at = DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cash System Configuration"
    
    @classmethod
    def get_config(cls):
        """Get or create singleton configuration"""
        config, created = cls.objects.get_or_create(pk=1)
        return config
```

### Configuration Access

```python
# In views and services
config = CashSystemConfig.get_config()
threshold = config.dual_verification_threshold
```


## Workflow Diagrams

### New Customer Payment Workflow

```
┌─────────────┐
│  Customer   │
│   Arrives   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Collector Opens     │
│ Cash Session        │
│ (if not open)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Collector Creates   │
│ Customer Account    │
│ - Name              │
│ - Phone             │
│ - ID Number         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Collector Adds      │
│ Vehicle Info        │
│ - Plate/Temp ID     │
│ - Type, Brand       │
│ - Engine Details    │
│ - Owner Name        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ System Calculates   │
│ Tax Amount          │
│ (TaxCalculation     │
│  Service)           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Collector Enters    │
│ Amount Tendered     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ System Calculates   │
│ Change              │
└──────┬──────────────┘
       │
       ▼
    ┌──┴──┐
    │ >   │ Amount >= Threshold?
    └──┬──┘
       │ Yes
       ▼
┌─────────────────────┐
│ Request Admin       │
│ Approval            │
│ (Dual Verification) │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Admin Reviews &     │
│ Approves            │
└──────┬──────────────┘
       │
       │ No (or after approval)
       ▼
┌─────────────────────┐
│ Create Payment      │
│ Record              │
│ - PaiementTaxe      │
│ - CashTransaction   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Calculate &         │
│ Record Commission   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Generate QR Code    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Generate & Print    │
│ Receipt             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Update Session      │
│ Totals              │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Create Audit Log    │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│  Customer   │
│  Receives   │
│  Receipt    │
└─────────────┘
```


### Existing Customer Payment Workflow

```
┌─────────────┐
│  Customer   │
│   Arrives   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Collector Searches  │
│ Customer            │
│ - By name           │
│ - By phone          │
│ - By vehicle plate  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ System Displays     │
│ Customer Vehicles   │
│ & Payment Status    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Collector Selects   │
│ Vehicle for Payment │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ System Displays     │
│ Tax Amount Due      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Collector Enters    │
│ Amount Tendered     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Process Payment     │
│ (Same as new        │
│  customer flow)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│  Receipt    │
│  Generated  │
└─────────────┘
```


### Session Management Workflow

```
┌─────────────────────┐
│ Collector Logs In   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Check for Active    │
│ Session             │
└──────┬──────────────┘
       │
    ┌──┴──┐
    │ ?   │ Has Active Session?
    └──┬──┘
       │ No
       ▼
┌─────────────────────┐
│ Open New Session    │
│ - Enter opening     │
│   balance           │
│ - Generate session  │
│   number            │
└──────┬──────────────┘
       │
       │ Yes (or after opening)
       ▼
┌─────────────────────┐
│ Process Payments    │
│ Throughout Day      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ End of Day:         │
│ Close Session       │
│ - Count physical    │
│   cash              │
│ - Enter closing     │
│   balance           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ System Calculates   │
│ Expected Balance    │
│ = Opening +         │
│   Payments -        │
│   Change            │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Compare Actual vs   │
│ Expected            │
└──────┬──────────────┘
       │
    ┌──┴──┐
    │ ?   │ Discrepancy > Tolerance?
    └──┬──┘
       │ Yes
       ▼
┌─────────────────────┐
│ Flag for Admin      │
│ Review              │
└──────┬──────────────┘
       │
       │ No (or after approval)
       ▼
┌─────────────────────┐
│ Mark Session        │
│ Closed              │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Display Commission  │
│ Earned              │
└─────────────────────┘
```

