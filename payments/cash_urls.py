"""
URL Configuration for Cash Payment System
Includes both Agent Partenaire and Admin Staff routes
"""

from django.urls import path

from . import cash_admin_views, cash_views

# Note: app_name is defined in payments/urls.py, not here
# This file is included via include() in payments/urls.py

urlpatterns = [
    # ============================================================================
    # AGENT PARTENAIRE ROUTES
    # ============================================================================
    # Session Management
    path("cash/session/open/", cash_views.CashSessionOpenView.as_view(), name="cash_session_open"),
    path("cash/session/<uuid:pk>/", cash_views.CashSessionDetailView.as_view(), name="cash_session_detail"),
    path("cash/session/<uuid:pk>/close/", cash_views.CashSessionCloseView.as_view(), name="cash_session_close"),
    # Payment Processing
    path("cash/payment/create/", cash_views.CashPaymentCreateView.as_view(), name="cash_payment_create"),
    path(
        "cash/payment/search-customer/", cash_views.CashPaymentSearchCustomerView.as_view(), name="cash_search_customer"
    ),
    path("cash/payment/calculate-tax/", cash_views.CashPaymentCalculateTaxView.as_view(), name="cash_calculate_tax"),
    path("cash/payment/<uuid:pk>/success/", cash_views.CashPaymentSuccessView.as_view(), name="cash_payment_success"),
    # Receipt Management
    path("cash/receipt/<uuid:pk>/print/", cash_views.ReceiptPrintView.as_view(), name="cash_receipt_print"),
    path("cash/receipt/<uuid:pk>/reprint/", cash_views.ReceiptReprintView.as_view(), name="cash_receipt_reprint"),
    path("cash/receipt/<uuid:pk>/download/", cash_views.ReceiptDownloadView.as_view(), name="cash_receipt_download"),
    # Commission and Dashboard
    path("cash/commission/", cash_views.CollectorCommissionView.as_view(), name="cash_commission"),
    path("cash/dashboard/", cash_views.CollectorDashboardView.as_view(), name="cash_dashboard"),
    # Transaction Void
    path(
        "cash/transaction/<uuid:pk>/void/", cash_views.CashTransactionVoidView.as_view(), name="cash_transaction_void"
    ),
    # ============================================================================
    # ADMIN STAFF ROUTES
    # ============================================================================
    # Collector Management
    path("cash/admin/collectors/", cash_admin_views.CollectorListView.as_view(), name="admin_collector_list"),
    path(
        "cash/admin/collectors/create/", cash_admin_views.CollectorCreateView.as_view(), name="admin_collector_create"
    ),
    path(
        "cash/admin/collectors/<uuid:pk>/",
        cash_admin_views.CollectorDetailView.as_view(),
        name="admin_collector_detail",
    ),
    path(
        "cash/admin/collectors/<uuid:pk>/edit/",
        cash_admin_views.CollectorUpdateView.as_view(),
        name="admin_collector_update",
    ),
    # Transaction Approval
    path("cash/admin/approvals/", cash_admin_views.TransactionApprovalListView.as_view(), name="admin_approval_list"),
    path(
        "cash/admin/approvals/<uuid:pk>/",
        cash_admin_views.TransactionApproveView.as_view(),
        name="admin_approve_transaction",
    ),
    # Reconciliation
    path("cash/admin/reconciliation/", cash_admin_views.DailyReconciliationView.as_view(), name="admin_reconciliation"),
    path(
        "cash/admin/reconciliation/history/",
        cash_admin_views.ReconciliationReportView.as_view(),
        name="admin_reconciliation_history",
    ),
    # Reports
    path(
        "cash/admin/reports/collection/",
        cash_admin_views.CashCollectionReportView.as_view(),
        name="admin_collection_report",
    ),
    path(
        "cash/admin/reports/discrepancies/",
        cash_admin_views.DiscrepancyReportView.as_view(),
        name="admin_discrepancy_report",
    ),
    path(
        "cash/admin/reports/commission/",
        cash_admin_views.CommissionReportView.as_view(),
        name="admin_commission_report",
    ),
    path("cash/admin/reports/audit/", cash_admin_views.AuditTrailView.as_view(), name="admin_audit_trail"),
    # System Configuration
    path("cash/admin/config/", cash_admin_views.CashSystemConfigView.as_view(), name="admin_system_config"),
]
