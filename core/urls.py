from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('qr-verification/', views.QRVerificationView.as_view(), name='qr_verification'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # Fleet Manager URLs
    path('fleet/', views.FleetDashboardView.as_view(), name='fleet_dashboard'),
    path('fleet/vehicles/', views.FleetVehicleListView.as_view(), name='fleet_vehicles'),
    path('fleet/batch-payment/', views.FleetBatchPaymentView.as_view(), name='fleet_batch_payment'),
    path('fleet/export/', views.FleetExportView.as_view(), name='fleet_export'),
    path('fleet/export/csv/', views.FleetExportCSVView.as_view(), name='fleet_export_csv'),
    path('fleet/export/excel/', views.FleetExportExcelView.as_view(), name='fleet_export_excel'),
    path('fleet/export/pdf/', views.FleetExportPDFView.as_view(), name='fleet_export_pdf'),
]