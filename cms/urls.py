from django.urls import path

from . import views

app_name = "cms"

urlpatterns = [
    path("", views.PublicHomeView.as_view(), name="home"),
    path("home2/", views.Home2View.as_view(), name="home2"),
    path("page/<slug:slug>/", views.CMSPageDetailView.as_view(), name="page_detail"),
    path("api/tax-simulation/", views.public_tax_simulation, name="public_tax_simulation"),
]
