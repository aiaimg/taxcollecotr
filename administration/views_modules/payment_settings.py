from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from administration.forms.stripe_config import StripeConfigForm
from administration.mixins import AdminRequiredMixin
from payments.models import StripeConfig


class StripeConfigManageView(AdminRequiredMixin, View):
    """Admin UI to manage Stripe configuration and activate environment."""

    template_name = "administration/payment_settings/stripe_config.html"

    def _get_or_init_configs(self, request):
        # Ensure both configs exist with sensible defaults
        dev_cfg, _ = StripeConfig.objects.get_or_create(
            environment="development",
            defaults={
                "currency": getattr(settings, "STRIPE_CURRENCY", "MGA"),
                "success_url": request.build_absolute_uri(reverse("payments:stripe_success")),
                "cancel_url": request.build_absolute_uri(reverse("payments:stripe_cancel")),
            },
        )
        prod_cfg, _ = StripeConfig.objects.get_or_create(
            environment="production",
            defaults={
                "currency": getattr(settings, "STRIPE_CURRENCY", "MGA"),
                "success_url": request.build_absolute_uri(reverse("payments:stripe_success")),
                "cancel_url": request.build_absolute_uri(reverse("payments:stripe_cancel")),
            },
        )
        return dev_cfg, prod_cfg

    def get(self, request):
        dev_cfg, prod_cfg = self._get_or_init_configs(request)
        dev_form = StripeConfigForm(instance=dev_cfg, initial={"environment": "development"})
        prod_form = StripeConfigForm(instance=prod_cfg, initial={"environment": "production"})

        active_env = (
            "development"
            if (dev_cfg.is_active and not prod_cfg.is_active)
            else ("production" if (prod_cfg.is_active and not dev_cfg.is_active) else None)
        )

        return render(
            request,
            self.template_name,
            {
                "dev_form": dev_form,
                "prod_form": prod_form,
                "dev_cfg": dev_cfg,
                "prod_cfg": prod_cfg,
                "active_env": active_env,
            },
        )

    def post(self, request):
        dev_cfg, prod_cfg = self._get_or_init_configs(request)
        action = request.POST.get("action")

        if action == "save_development":
            dev_form = StripeConfigForm(request.POST, instance=dev_cfg, initial={"environment": "development"})
            prod_form = StripeConfigForm(instance=prod_cfg, initial={"environment": "production"})
            if dev_form.is_valid():
                dev_form.save()
                messages.success(request, "Configuration Stripe (dev) mise à jour avec succès.")
            else:
                messages.error(request, "Erreur lors de la mise à jour de la configuration dev.")
            return render(
                request,
                self.template_name,
                {
                    "dev_form": dev_form,
                    "prod_form": prod_form,
                    "dev_cfg": dev_cfg,
                    "prod_cfg": prod_cfg,
                    "active_env": (
                        "development" if dev_cfg.is_active else ("production" if prod_cfg.is_active else None)
                    ),
                },
            )

        if action == "save_production":
            prod_form = StripeConfigForm(request.POST, instance=prod_cfg, initial={"environment": "production"})
            dev_form = StripeConfigForm(instance=dev_cfg, initial={"environment": "development"})
            if prod_form.is_valid():
                prod_form.save()
                messages.success(request, "Configuration Stripe (prod) mise à jour avec succès.")
            else:
                messages.error(request, "Erreur lors de la mise à jour de la configuration prod.")
            return render(
                request,
                self.template_name,
                {
                    "dev_form": dev_form,
                    "prod_form": prod_form,
                    "dev_cfg": dev_cfg,
                    "prod_cfg": prod_cfg,
                    "active_env": (
                        "development" if dev_cfg.is_active else ("production" if prod_cfg.is_active else None)
                    ),
                },
            )

        if action == "activate_development":
            StripeConfig.activate("development")
            messages.success(request, "Environnement Stripe actif: développement")
            return redirect("administration:stripe_config_manage")

        if action == "activate_production":
            StripeConfig.activate("production")
            messages.success(request, "Environnement Stripe actif: production")
            return redirect("administration:stripe_config_manage")

        messages.error(request, "Action inconnue.")
        return redirect("administration:stripe_config_manage")
