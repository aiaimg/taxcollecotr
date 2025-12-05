from django.urls import include, path

from allauth.account import urls as allauth_account_urls
from allauth.socialaccount import urls as allauth_socialaccount_urls
from django.urls import include

from .allauth_views import CustomAllauthLoginView

# Override the login URL with our custom view
custom_account_patterns = [
    path("login/", CustomAllauthLoginView.as_view(), name="account_login"),
]

# Include all other allauth URLs except login
urlpatterns = custom_account_patterns + [
    path("", include(allauth_account_urls)),
    path("", include(allauth_socialaccount_urls)),
    path("", include("allauth.urls")),
]
