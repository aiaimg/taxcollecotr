from django.urls import path, include
from allauth.account import urls as allauth_account_urls
from .allauth_views import CustomAllauthLoginView

# Override the login URL with our custom view
custom_account_patterns = [
    path('login/', CustomAllauthLoginView.as_view(), name='account_login'),
]

# Include all other allauth URLs except login
urlpatterns = custom_account_patterns + [
    path('', include(allauth_account_urls)),
]