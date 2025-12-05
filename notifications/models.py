import uuid

from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):
    """Notification system for users"""

    TYPE_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push"),
        ("system", "Système"),
    ]

    LANGUE_CHOICES = [
        ("fr", "Français"),
        ("mg", "Malagasy"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type de notification")
    titre = models.CharField(max_length=200, verbose_name="Titre")
    contenu = models.TextField(verbose_name="Contenu")
    langue = models.CharField(max_length=5, choices=LANGUE_CHOICES, default="fr", verbose_name="Langue")
    est_lue = models.BooleanField(default=False, verbose_name="Est lue")
    date_envoi = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    date_lecture = models.DateTimeField(null=True, blank=True, verbose_name="Date de lecture")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Métadonnées")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-date_envoi"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["type_notification"]),
            models.Index(fields=["user", "est_lue"], condition=models.Q(est_lue=False), name="notif_user_non_lue_idx"),
            models.Index(fields=["date_envoi"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_lecture__isnull=True) | models.Q(date_lecture__gte=models.F("date_envoi")),
                name="date_lecture_after_envoi",
            )
        ]

    def __str__(self):
        return f"{self.titre} - {self.user.username} ({self.type_notification})"

    def marquer_comme_lue(self):
        """Mark notification as read"""
        if not self.est_lue:
            from django.utils import timezone

            self.est_lue = True
            self.date_lecture = timezone.now()
            self.save(update_fields=["est_lue", "date_lecture"])


class NotificationTemplate(models.Model):
    """Templates for notifications"""

    TYPE_CHOICES = [
        ("rappel_echeance", "Rappel d'échéance"),
        ("confirmation_paiement", "Confirmation de paiement"),
        ("vehicule_ajoute", "Véhicule ajouté"),
        ("paiement_echoue", "Paiement échoué"),
        ("qr_genere", "QR code généré"),
        ("bienvenue", "Bienvenue"),
    ]

    LANGUE_CHOICES = [
        ("fr", "Français"),
        ("mg", "Malagasy"),
    ]

    nom = models.CharField(max_length=100, verbose_name="Nom du template")
    type_template = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="Type de template")
    langue = models.CharField(max_length=5, choices=LANGUE_CHOICES, verbose_name="Langue")
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    contenu_html = models.TextField(verbose_name="Contenu HTML")
    contenu_texte = models.TextField(verbose_name="Contenu texte")
    variables_disponibles = models.JSONField(
        default=list, verbose_name="Variables disponibles", help_text="Liste des variables utilisables dans le template"
    )
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Template de notification"
        verbose_name_plural = "Templates de notifications"
        unique_together = [["type_template", "langue"]]
        indexes = [
            models.Index(fields=["type_template", "langue", "est_actif"]),
        ]

    def __str__(self):
        return f"{self.nom} ({self.langue})"

    def render(self, context=None):
        """Render template with context variables"""
        if context is None:
            context = {}

        sujet_rendu = self.sujet
        contenu_html_rendu = self.contenu_html
        contenu_texte_rendu = self.contenu_texte

        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            sujet_rendu = sujet_rendu.replace(placeholder, str(value))
            contenu_html_rendu = contenu_html_rendu.replace(placeholder, str(value))
            contenu_texte_rendu = contenu_texte_rendu.replace(placeholder, str(value))

        return {
            "sujet": sujet_rendu,
            "contenu_html": contenu_html_rendu,
            "contenu_texte": contenu_texte_rendu,
        }
