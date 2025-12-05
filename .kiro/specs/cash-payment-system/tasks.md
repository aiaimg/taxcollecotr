# Implementation Plan

- [x] 1. Set up project structure and core models
- [x] 1.1 Create AgentPartenaireProfile model in payments app
  - Define model with all fields (agent_id, full_name, phone_number, collection_location, commission_rate, etc.)
  - Add model to admin.py for admin management
  - Create and run migrations
  - _Requirements: 1, 2, 6, 15_

- [x] 1.2 Create CashSession model in payments app
  - Define model for session management
  - Add session_number auto-generation
  - Add status choices (open, closed, reconciled)
  - Create and run migrations
  - _Requirements: 7_

- [x] 1.3 Create CashTransaction model in payments app
  - Define model for individual transactions
  - Link to PaiementTaxe and CashSession
  - Add approval fields for dual verification
  - Create and run migrations
  - _Requirements: 1, 2, 3, 4, 8_

- [x] 1.4 Create CashReceipt model in payments app
  - Define model for receipt storage
  - Link to CashTransaction and existing QRCode model
  - Add duplicate tracking
  - Create and run migrations
  - _Requirements: 5_

- [x] 1.5 Create CommissionRecord model in payments app
  - Define model for commission tracking
  - Link to agent, session, and transaction
  - Add payment status tracking
  - Create and run migrations
  - _Requirements: 6_

- [x] 1.6 Create CashAuditLog model in payments app
  - Define model with hash chain fields
  - Add action type choices
  - Create and run migrations
  - _Requirements: 9, 12_

- [x] 1.7 Create CashSystemConfig model in payments app
  - Define singleton configuration model
  - Add all configuration fields (commission, thresholds, etc.)
  - Add admin interface
  - Create and run migrations
  - _Requirements: 10, 14_

- [x] 1.8 Extend PaiementTaxe model
  - Add 'cash' to METHODE_PAIEMENT_CHOICES
  - Add cash_transaction ForeignKey field
  - Add collected_by ForeignKey to AgentPartenaireProfile
  - Create and run migrations
  - _Requirements: 1, 2, 3, 4_


- [x] 2. Implement core services in payments app
- [x] 2.1 Create payments/services/cash_payment_service.py
  - Implement calculate_change() method
  - Implement create_cash_payment() for new customers
  - Implement process_existing_customer_payment()
  - Implement requires_dual_verification()
  - Implement approve_transaction()
  - _Requirements: 1, 2, 3, 4, 8_

- [x] 2.2 Create payments/services/cash_session_service.py
  - Implement open_session()
  - Implement close_session()
  - Implement get_active_session()
  - Implement calculate_session_totals()
  - _Requirements: 7_

- [x] 2.3 Extend existing ReceiptService or create payments/services/cash_receipt_service.py
  - Implement generate_cash_receipt()
  - Implement generate_cash_receipt_pdf() using ReportLab (reuse existing PDF logic)
  - Implement reprint_receipt()
  - Integrate with existing QRCode model and receipt generation
  - _Requirements: 5_

- [x] 2.4 Create payments/services/commission_service.py
  - Implement calculate_commission()
  - Implement record_commission()
  - Implement get_session_commission()
  - Implement get_collector_commission_report()
  - _Requirements: 6_

- [x] 2.5 Create payments/services/reconciliation_service.py
  - Implement generate_daily_report()
  - Implement reconcile_day()
  - Implement get_discrepancy_report()
  - _Requirements: 10, 11_

- [x] 2.6 Create payments/services/cash_audit_service.py
  - Implement log_action() with hash chain
  - Implement verify_audit_trail()
  - Implement get_audit_trail()
  - Use SHA-256 for hashing
  - Use AES-256 for encryption
  - _Requirements: 9, 12_

- [x] 3. Create forms in payments app
- [x] 3.1 Create payments/forms.py - CashSessionOpenForm
  - Add opening_balance field
  - Add validation
  - _Requirements: 7_

- [x] 3.2 Create CashPaymentForm
  - Add customer search/new customer fields
  - Add vehicle fields (new or existing)
  - Add payment fields (tax_amount, amount_tendered)
  - Add comprehensive validation
  - Integrate with TaxCalculationService
  - _Requirements: 1, 2, 3, 4_

- [x] 3.3 Create CashSessionCloseForm
  - Add closing_balance field
  - Add discrepancy_notes field
  - _Requirements: 7_

- [x] 3.4 Create TransactionApprovalForm
  - Add approval_notes field
  - Add action choice (approve/reject)
  - _Requirements: 8_

- [x] 3.5 Create ReconciliationForm
  - Add reconciliation_date field
  - Add physical_cash_count field
  - Add reconciliation_notes field
  - _Requirements: 10_


- [x] 4. Implement Agent Partenaire views in payments app
- [x] 4.1 Create CashSessionOpenView
  - Implement session opening logic
  - Check for existing open session
  - Validate opening balance
  - _Requirements: 7_

- [x] 4.2 Create CashSessionCloseView
  - Implement session closing logic
  - Calculate expected balance
  - Calculate discrepancy
  - Flag for admin review if needed
  - _Requirements: 7_

- [x] 4.3 Create CashSessionDetailView
  - Display session information
  - Show all transactions in session
  - Show commission earned
  - _Requirements: 6, 7_

- [x] 4.4 Create CashPaymentCreateView
  - Handle both new and existing customers
  - Implement customer search
  - Implement vehicle registration
  - Calculate tax using TaxCalculationService
  - Process payment with change calculation
  - Check for dual verification requirement
  - Generate receipt
  - Update session totals
  - _Requirements: 1, 2, 3, 4, 5, 6, 8_

- [x] 4.5 Create CashPaymentSearchCustomerView (AJAX)
  - Search by name, phone, or vehicle plate
  - Return customer and vehicle data as JSON
  - _Requirements: 2_

- [x] 4.6 Create CashPaymentCalculateTaxView (AJAX)
  - Calculate tax for vehicle
  - Return tax amount as JSON
  - _Requirements: 1, 2, 3, 4_

- [x] 4.7 Create ReceiptPrintView
  - Generate and display receipt
  - Mark as printed
  - _Requirements: 5_

- [x] 4.8 Create ReceiptReprintView
  - Reprint existing receipt
  - Mark as duplicate
  - Log reprint action
  - _Requirements: 5_

- [x] 4.9 Create ReceiptDownloadView
  - Generate PDF receipt
  - Return as download
  - _Requirements: 5_

- [x] 4.10 Create CollectorCommissionView
  - Display commission history
  - Filter by date range
  - Show totals
  - _Requirements: 6_

- [x] 4.11 Create CollectorDashboardView
  - Show active session status
  - Show today's transactions
  - Show today's commission
  - Show quick actions
  - _Requirements: 3, 6, 7_

- [x] 4.12 Create CashTransactionVoidView
  - Search for transaction in current open session
  - Display original transaction details
  - Validate transaction is voidable (same session, within time limit)
  - Require admin approval for void
  - Create void transaction record (compensating entry)
  - Update session balance (reverse amounts)
  - Mark original transaction as voided
  - Log void action in audit trail
  - _Requirements: 13_


- [x] 5. Implement Admin Staff views in payments app
- [x] 5.1 Create CollectorListView
  - List all Agent Partenaire profiles
  - Show active/inactive status
  - Add search and filters
  - _Requirements: 15_

- [x] 5.2 Create CollectorCreateView
  - Create new Agent Partenaire
  - Set commission rate (default or custom)
  - Assign collection location
  - _Requirements: 6, 14, 15_

- [x] 5.3 Create CollectorUpdateView
  - Edit Agent Partenaire details
  - Update commission rate
  - Activate/deactivate agent
  - _Requirements: 6, 14, 15_

- [x] 5.4 Create CollectorDetailView
  - Show agent details
  - Show session history
  - Show commission totals
  - Show performance metrics
  - _Requirements: 6, 11, 15_

- [x] 5.5 Create TransactionApprovalListView
  - List pending approvals
  - Filter by amount, date, agent
  - Show transaction details
  - _Requirements: 8_

- [x] 5.6 Create TransactionApproveView
  - Approve or reject transaction
  - Add approval notes
  - Send notification to agent
  - _Requirements: 8_

- [x] 5.7 Create DailyReconciliationView
  - Show all sessions for selected date
  - Calculate expected totals
  - Enter physical cash count
  - Calculate discrepancies
  - Require approval if over tolerance
  - _Requirements: 10_

- [x] 5.8 Create ReconciliationReportView
  - Show reconciliation history
  - Filter by date range
  - Show discrepancies
  - Export to PDF/CSV
  - _Requirements: 10, 11_

- [x] 5.9 Create CashCollectionReportView
  - Generate collection reports
  - Filter by date, agent, vehicle type
  - Show summary statistics
  - Export to PDF/CSV
  - _Requirements: 11_

- [x] 5.10 Create DiscrepancyReportView
  - Show all discrepancies
  - Filter by agent, date range
  - Show resolution status
  - _Requirements: 11_

- [x] 5.11 Create CommissionReportView
  - Show commission by agent
  - Filter by date range
  - Show payment status
  - Export to PDF/CSV
  - _Requirements: 6, 11_

- [x] 5.12 Create AuditTrailView
  - Display audit log entries
  - Filter by action type, user, date
  - Verify hash chain integrity
  - Export audit logs
  - _Requirements: 9, 12_

- [x] 5.13 Create CashSystemConfigView
  - Edit system configuration
  - Set default commission rate
  - Set dual verification threshold
  - Set reconciliation tolerance
  - Configure receipt format
  - _Requirements: 6, 8, 10, 14_


- [x] 6. Create templates in templates/payments directory
- [x] 6.1 Create Agent Partenaire templates
  - templates/payments/cash/session_open.html
  - templates/payments/cash/session_detail.html
  - templates/payments/cash/session_close.html
  - templates/payments/cash/payment_create.html (with customer search and vehicle form)
  - templates/payments/cash/payment_success.html
  - templates/payments/cash/receipt_preview.html
  - templates/payments/cash/agent_dashboard.html
  - templates/payments/cash/commission_list.html
  - _Requirements: 1, 2, 3, 4, 5, 6, 7_

- [x] 6.2 Create Admin Staff templates
  - templates/payments/cash/admin/agent_list.html
  - templates/payments/cash/admin/agent_detail.html
  - templates/payments/cash/admin/agent_form.html
  - templates/payments/cash/admin/approval_list.html
  - templates/payments/cash/admin/reconciliation.html
  - templates/payments/cash/admin/reconciliation_history.html
  - templates/payments/cash/admin/collection_report.html
  - templates/payments/cash/admin/discrepancy_report.html
  - templates/payments/cash/admin/commission_report.html
  - templates/payments/cash/admin/audit_trail.html
  - templates/payments/cash/admin/system_config.html
  - _Requirements: 6, 8, 9, 10, 11, 12, 14, 15_

- [x] 6.3 Create shared partial templates
  - templates/payments/cash/partials/customer_search.html (AJAX search widget)
  - templates/payments/cash/partials/vehicle_form.html
  - templates/payments/cash/partials/payment_calculator.html (tax calculator)
  - templates/payments/cash/partials/cash_receipt_template.html
  - _Requirements: 1, 2, 3, 4, 5_

- [x] 7. Configure URLs
- [x] 7.1 Update payments/urls.py
  - Add URL patterns for cash payment views (agent and admin)
  - Organize under /payments/cash/ prefix
  - _Requirements: All_

- [x] 7.2 Update sidebar navigation
  - Add Agent Partenaire menu items
  - Add Admin cash management menu items
  - Update templates/velzon/partials/sidebar_tax_collector.html (rename to sidebar_agent_partenaire.html)
  - Update templates/velzon/partials/sidebar_administration.html
  - _Requirements: 15_

- [x] 8. Implement permissions and access control
- [x] 8.1 Create permission groups
  - Create "Agent Partenaire" group with appropriate permissions
  - Create "Admin Staff" group with full permissions
  - _Requirements: 15_

- [x] 8.2 Add permission checks to views
  - Use LoginRequiredMixin for all views
  - Use UserPassesTestMixin for admin views
  - Check user roles in view methods
  - _Requirements: 15_

- [x] 8.3 Create permission decorators
  - @agent_partenaire_required decorator
  - @admin_staff_required decorator
  - _Requirements: 15_


- [x] 9. Add JavaScript functionality
- [x] 9.1 Create customer search AJAX
  - Implement real-time customer search
  - Display search results
  - Auto-fill customer and vehicle data
  - _Requirements: 2_

- [x] 9.2 Create tax calculator
  - Calculate tax based on vehicle details
  - Display tax amount in real-time
  - _Requirements: 1, 2, 3, 4_

- [x] 9.3 Create change calculator
  - Calculate change when amount tendered is entered
  - Validate sufficient payment
  - Display change amount
  - _Requirements: 4_

- [x] 9.4 Create receipt preview
  - Show receipt preview before printing
  - Generate QR code display
  - _Requirements: 5_

- [x] 9.5 Add form validation
  - Client-side validation for all forms
  - Real-time error messages
  - _Requirements: All_

- [x] 10. Integrate with existing systems
- [x] 10.1 Update PaiementTaxe admin
  - Add cash transaction fields to admin display
  - Add filters for payment method
  - _Requirements: 1, 2, 3, 4_

- [x] 10.2 Integrate with notification system
  - Send notification when payment is completed
  - Send notification when approval is required
  - Send notification when session is closed
  - _Requirements: 3, 8_

- [x] 10.3 Update dashboard widgets
  - Add cash collection widget to admin dashboard
  - Add agent performance widget
  - _Requirements: 11_

- [x] 10.4 Integrate with QR code system
  - Use existing QRCode model
  - Link cash receipts to QR codes
  - _Requirements: 5_

- [x] 11. Create management commands
- [x] 11.1 Create close_expired_sessions command
  - Auto-close sessions after timeout
  - Send notifications to agents
  - _Requirements: 7_

- [x] 11.2 Create generate_commission_report command
  - Generate monthly commission reports
  - Email reports to admin
  - _Requirements: 6, 11_

- [x] 11.3 Create verify_audit_trail command
  - Verify hash chain integrity
  - Alert if tampering detected
  - _Requirements: 9, 12_

- [x] 11.4 Create reconciliation_reminder command
  - Send daily reconciliation reminders
  - List unreconciled sessions
  - _Requirements: 10_

