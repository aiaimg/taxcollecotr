"""
Modèles pour le système de contravention numérique.
"""

import hashlib
import json
import secrets
import string
import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class TypeInfraction(models.Model):
    """Catalogue des infractions conformes à la Loi n°2017-002"""

    CATEGORIE_CHOICES = [
        ("DELIT_GRAVE", "Délits routiers graves"),
        ("CIRCULATION", "Infractions de circulation"),
        ("DOCUMENTAIRE", "Infractions documentaires"),
        ("SECURITE", "Infractions de sécurité"),
    ]

    AUTORITE_CHOICES = [
        ("POLICE_NATIONALE", "Police Nationale"),
        ("GENDARMERIE", "Gendarmerie"),
        ("POLICE_COMMUNALE", "Police Communale"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(
        max_length=255, verbose_name="Nom de l'infraction", help_text="Nom descriptif de l'infraction"
    )
    article_code = models.CharField(
        max_length=50, verbose_name="Article du Code", help_text="Article du Code de la Route (ex: L7.1-1)"
    )
    loi_reference = models.CharField(
        max_length=100, default="Loi n°2017-002 du 6 juillet 2017", verbose_name="Référence légale"
    )
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES, verbose_name="Catégorie")
    montant_min_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Montant minimum (Ariary)",
    )
    montant_max_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Montant maximum (Ariary)",
    )
    montant_variable = models.BooleanField(
        default=False,
        verbose_name="Montant variable",
        help_text="Si le montant est déterminé par l'autorité compétente",
    )
    sanctions_administratives = models.TextField(
        blank=True, verbose_name="Sanctions administratives", help_text="Description des sanctions complémentaires"
    )
    fourriere_obligatoire = models.BooleanField(default=False, verbose_name="Fourrière obligatoire")
    emprisonnement_possible = models.CharField(
        max_length=100, blank=True, verbose_name="Emprisonnement possible", help_text="Durée possible d'emprisonnement"
    )
    penalite_accident_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Pénalité en cas d'accident (Ariary)",
    )
    penalite_recidive_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Pénalité de récidive (%)",
    )
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Type d'infraction"
        verbose_name_plural = "Types d'infractions"
        ordering = ["categorie", "nom"]
        indexes = [
            models.Index(fields=["categorie"]),
            models.Index(fields=["article_code"]),
            models.Index(fields=["est_actif"]),
        ]

    def __str__(self):
        return f"{self.article_code} - {self.nom}"

    def get_montant_pour_autorite(self, autorite=None):
        """Retourne le montant applicable selon l'autorité"""
        if not self.montant_variable:
            return self.montant_min_ariary

        # Pour les montants variables, retourner le montant moyen par défaut
        # Les montants spécifiques par autorité peuvent être configurés ultérieurement
        return (self.montant_min_ariary + self.montant_max_ariary) / 2

    def calculer_montant_avec_aggravations(self, has_accident=False, is_recidive=False, autorite=None):
        """Calcule le montant final avec aggravations"""
        montant_base = self.get_montant_pour_autorite(autorite)

        # Ajouter pénalité accident
        if has_accident and self.penalite_accident_ariary:
            montant_base += self.penalite_accident_ariary

        # Ajouter pénalité récidive (pourcentage)
        if is_recidive and self.penalite_recidive_pct:
            montant_base += montant_base * (self.penalite_recidive_pct / 100)

        return montant_base


class AgentControleurProfile(models.Model):
    """Profil des agents de police/gendarmerie autorisés"""

    AUTORITE_CHOICES = [
        ("POLICE_NATIONALE", "Police Nationale"),
        ("GENDARMERIE", "Gendarmerie"),
        ("POLICE_COMMUNALE", "Police Communale"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="agent_controleur_profile", verbose_name="Utilisateur"
    )
    matricule = models.CharField(
        max_length=50, unique=True, verbose_name="Matricule", help_text="Matricule unique de l'agent"
    )
    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet")
    unite_affectation = models.CharField(
        max_length=200, verbose_name="Unité d'affectation", help_text="Unité ou brigade d'affectation"
    )
    grade = models.CharField(max_length=100, verbose_name="Grade")
    autorite_type = models.CharField(max_length=50, choices=AUTORITE_CHOICES, verbose_name="Type d'autorité")
    juridiction = models.CharField(
        max_length=200, verbose_name="Juridiction", help_text="Zone de compétence géographique"
    )
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil Agent Contrôleur"
        verbose_name_plural = "Profils Agents Contrôleurs"
        ordering = ["nom_complet"]
        indexes = [
            models.Index(fields=["matricule"]),
            models.Index(fields=["user"]),
            models.Index(fields=["autorite_type"]),
            models.Index(fields=["est_actif"]),
        ]

    def __str__(self):
        return f"{self.matricule} - {self.nom_complet}"


class Conducteur(models.Model):
    """Informations sur le conducteur en infraction"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cin = models.CharField(
        max_length=12,
        validators=[RegexValidator(r"^\d{12}$", "Le CIN doit contenir exactement 12 chiffres")],
        verbose_name="Numéro CIN",
        help_text="Numéro de Carte d'Identité Nationale (12 chiffres)",
    )
    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet")
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    numero_permis = models.CharField(max_length=50, blank=True, verbose_name="Numéro de permis de conduire")
    categorie_permis = models.CharField(
        max_length=20, blank=True, verbose_name="Catégorie de permis", help_text="Ex: A, B, C, D, E"
    )
    date_delivrance_permis = models.DateField(null=True, blank=True, verbose_name="Date de délivrance du permis")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conducteur"
        verbose_name_plural = "Conducteurs"
        ordering = ["nom_complet"]
        indexes = [
            models.Index(fields=["cin"]),
            models.Index(fields=["numero_permis"]),
        ]

    def __str__(self):
        return f"{self.nom_complet} (CIN: {self.cin})"


class Contravention(models.Model):
    """Enregistrement principal d'une contravention"""

    STATUT_CHOICES = [
        ("IMPAYEE", "Impayée"),
        ("PAYEE", "Payée"),
        ("CONTESTEE", "Contestée"),
        ("ANNULEE", "Annulée"),
    ]

    ROUTE_TYPE_CHOICES = [
        ("NATIONALE", "Route Nationale"),
        ("COMMUNALE", "Route Communale"),
        ("AUTRE", "Autre"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_pv = models.CharField(
        max_length=50, unique=True, verbose_name="Numéro PV", help_text="Format: PV-YYYYMMDD-XXXXXX"
    )
    agent_controleur = models.ForeignKey(
        AgentControleurProfile,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="contraventions",
        verbose_name="Agent contrôleur",
    )
    type_infraction = models.ForeignKey(
        TypeInfraction,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="contraventions",
        verbose_name="Type d'infraction",
    )
    vehicule = models.ForeignKey(
        "vehicles.Vehicule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contraventions",
        verbose_name="Véhicule",
        help_text="Véhicule enregistré dans le système (si trouvé)",
    )
    vehicule_plaque_manuelle = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Plaque manuelle",
        help_text="Plaque si véhicule non trouvé dans le système",
    )
    vehicule_marque_manuelle = models.CharField(max_length=100, blank=True, verbose_name="Marque manuelle")
    vehicule_modele_manuelle = models.CharField(max_length=100, blank=True, verbose_name="Modèle manuel")
    conducteur = models.ForeignKey(
        Conducteur,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="contraventions",
        verbose_name="Conducteur",
    )
    date_heure_infraction = models.DateTimeField(null=True, blank=True, verbose_name="Date et heure de l'infraction")
    lieu_infraction = models.TextField(
        blank=True, default="", verbose_name="Lieu de l'infraction", help_text="Adresse textuelle du lieu"
    )
    route_type = models.CharField(max_length=50, choices=ROUTE_TYPE_CHOICES, blank=True, verbose_name="Type de route")
    route_numero = models.CharField(max_length=20, blank=True, verbose_name="Numéro de route", help_text="Ex: RN1, RN7")
    coordonnees_gps_lat = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True, verbose_name="Latitude GPS"
    )
    coordonnees_gps_lon = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="Longitude GPS"
    )
    montant_amende_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Montant de l'amende (Ariary)",
    )
    a_accident_associe = models.BooleanField(default=False, verbose_name="Accident associé")
    est_recidive = models.BooleanField(default=False, verbose_name="Est une récidive")
    observations = models.TextField(blank=True, verbose_name="Observations")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="IMPAYEE", verbose_name="Statut")
    delai_paiement_jours = models.IntegerField(default=15, verbose_name="Délai de paiement (jours)")
    date_limite_paiement = models.DateField(verbose_name="Date limite de paiement")
    date_paiement = models.DateTimeField(null=True, blank=True, verbose_name="Date de paiement")
    signature_electronique_conducteur = models.TextField(
        blank=True, verbose_name="Signature électronique", help_text="Signature en base64"
    )
    qr_code = models.ForeignKey(
        "payments.QRCode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contraventions",
        verbose_name="QR Code",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contravention"
        verbose_name_plural = "Contraventions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["numero_pv"]),
            models.Index(fields=["agent_controleur", "date_heure_infraction"]),
            models.Index(fields=["vehicule", "statut"]),
            models.Index(fields=["conducteur", "statut"]),
            models.Index(fields=["statut", "date_limite_paiement"]),
            models.Index(fields=["date_heure_infraction"]),
        ]

    def __str__(self):
        return f"{self.numero_pv} - {self.statut}"

    def generate_numero_pv(self):
        """Génère un numéro PV unique"""
        from django.utils import timezone

        date_str = timezone.now().strftime("%Y%m%d")

        # Générer un identifiant aléatoire de 6 caractères
        alphabet = string.ascii_uppercase + string.digits
        random_id = "".join(secrets.choice(alphabet) for _ in range(6))

        numero = f"PV-{date_str}-{random_id}"

        # Vérifier l'unicité
        while Contravention.objects.filter(numero_pv=numero).exists():
            random_id = "".join(secrets.choice(alphabet) for _ in range(6))
            numero = f"PV-{date_str}-{random_id}"

        return numero

    def calculer_date_limite(self):
        """Calcule la date limite de paiement"""
        if self.date_heure_infraction:
            return self.date_heure_infraction.date() + timedelta(days=self.delai_paiement_jours)
        return timezone.now().date() + timedelta(days=self.delai_paiement_jours)

    def est_en_retard(self):
        """Vérifie si le délai de paiement est dépassé"""
        return timezone.now().date() > self.date_limite_paiement and self.statut == "IMPAYEE"

    def calculer_penalite_retard(self):
        """Calcule la pénalité de retard"""
        if not self.est_en_retard():
            return Decimal("0")

        config = ConfigurationSysteme.get_config()
        penalite = self.montant_amende_ariary * (config.penalite_retard_pct / 100)
        return penalite

    def get_montant_total(self):
        """Retourne le montant total avec pénalités si applicable"""
        montant = self.montant_amende_ariary
        if self.est_en_retard():
            montant += self.calculer_penalite_retard()
        return montant

    def get_vehicle_display(self):
        """Retourne l'affichage du véhicule (plaque enregistrée ou manuelle)"""
        if self.vehicule:
            return self.vehicule.plaque_immatriculation
        return self.vehicule_plaque_manuelle or "Véhicule non identifié"

    def save(self, *args, **kwargs):
        """Override save pour générer le numéro PV et calculer la date limite"""
        if not self.numero_pv:
            self.numero_pv = self.generate_numero_pv()

        if not self.date_limite_paiement:
            self.date_limite_paiement = self.calculer_date_limite()

        super().save(*args, **kwargs)


class DossierFourriere(models.Model):
    """Gestion des véhicules mis en fourrière"""

    STATUT_CHOICES = [
        ("EN_FOURRIERE", "En fourrière"),
        ("RESTITUE", "Restitué"),
        ("VENDU_AUX_ENCHERES", "Vendu aux enchères"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contravention = models.OneToOneField(
        Contravention, on_delete=models.CASCADE, related_name="dossier_fourriere", verbose_name="Contravention"
    )
    numero_dossier = models.CharField(
        max_length=50, unique=True, verbose_name="Numéro de dossier", help_text="Format: FOUR-YYYYMMDD-XXXXX"
    )
    date_mise_fourriere = models.DateTimeField(verbose_name="Date de mise en fourrière")
    lieu_fourriere = models.CharField(max_length=200, verbose_name="Lieu de la fourrière")
    adresse_fourriere = models.TextField(verbose_name="Adresse de la fourrière")
    type_vehicule = models.CharField(max_length=50, verbose_name="Type de véhicule", help_text="Pour calcul des frais")
    frais_transport_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Frais de transport (Ariary)",
    )
    frais_gardiennage_journalier_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Frais de gardiennage journalier (Ariary)",
    )
    duree_minimale_jours = models.IntegerField(default=10, verbose_name="Durée minimale (jours)")
    date_sortie_fourriere = models.DateTimeField(null=True, blank=True, verbose_name="Date de sortie")
    frais_totaux_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Frais totaux (Ariary)",
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="EN_FOURRIERE", verbose_name="Statut")
    bon_sortie_numero = models.CharField(max_length=50, blank=True, verbose_name="Numéro de bon de sortie")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dossier de fourrière"
        verbose_name_plural = "Dossiers de fourrière"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["numero_dossier"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["date_mise_fourriere"]),
        ]

    def __str__(self):
        return f"{self.numero_dossier} - {self.statut}"

    def generate_numero_dossier(self):
        """Génère un numéro de dossier unique"""
        date_str = timezone.now().strftime("%Y%m%d")
        alphabet = string.ascii_uppercase + string.digits
        random_id = "".join(secrets.choice(alphabet) for _ in range(5))

        numero = f"FOUR-{date_str}-{random_id}"

        while DossierFourriere.objects.filter(numero_dossier=numero).exists():
            random_id = "".join(secrets.choice(alphabet) for _ in range(5))
            numero = f"FOUR-{date_str}-{random_id}"

        return numero

    def calculer_frais_gardiennage(self):
        """Calcule les frais de gardiennage selon les jours écoulés"""
        if self.date_sortie_fourriere:
            jours = (self.date_sortie_fourriere.date() - self.date_mise_fourriere.date()).days
        else:
            jours = (timezone.now().date() - self.date_mise_fourriere.date()).days

        return self.frais_gardiennage_journalier_ariary * max(jours, 0)

    def calculer_frais_totaux(self):
        """Calcule les frais totaux (transport + gardiennage)"""
        return self.frais_transport_ariary + self.calculer_frais_gardiennage()

    def peut_etre_restitue(self):
        """Vérifie si le véhicule peut être restitué"""
        # Vérifier durée minimale
        jours_ecoules = (timezone.now().date() - self.date_mise_fourriere.date()).days
        if jours_ecoules < self.duree_minimale_jours:
            return False, f"Durée minimale non atteinte ({jours_ecoules}/{self.duree_minimale_jours} jours)"

        # Vérifier paiement de l'amende
        if self.contravention.statut != "PAYEE":
            return False, "L'amende n'est pas payée"

        # Vérifier paiement des frais de fourrière
        # (À implémenter avec le système de paiement)

        return True, "Le véhicule peut être restitué"

    def generer_bon_sortie(self):
        """Génère le bon de sortie avec QR code"""
        if not self.bon_sortie_numero:
            date_str = timezone.now().strftime("%Y%m%d")
            alphabet = string.ascii_uppercase + string.digits
            random_id = "".join(secrets.choice(alphabet) for _ in range(6))
            self.bon_sortie_numero = f"BS-{date_str}-{random_id}"
            self.save()

        return self.bon_sortie_numero

    def save(self, *args, **kwargs):
        """Override save pour générer le numéro de dossier"""
        if not self.numero_dossier:
            self.numero_dossier = self.generate_numero_dossier()

        # Mettre à jour les frais totaux
        self.frais_totaux_ariary = self.calculer_frais_totaux()

        super().save(*args, **kwargs)


class PhotoContravention(models.Model):
    """Photos et preuves de l'infraction"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contravention = models.ForeignKey(
        Contravention, on_delete=models.CASCADE, related_name="photos", verbose_name="Contravention"
    )
    fichier = models.ImageField(upload_to="contraventions/%Y/%m/%d/", verbose_name="Fichier photo")
    description = models.CharField(max_length=200, blank=True, verbose_name="Description")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    metadata_exif = models.JSONField(
        default=dict, blank=True, verbose_name="Métadonnées EXIF", help_text="Date, GPS, etc."
    )
    hash_fichier = models.CharField(
        max_length=64, blank=True, verbose_name="Hash SHA-256", help_text="Pour vérification d'intégrité"
    )
    annotations = models.JSONField(
        default=dict, blank=True, verbose_name="Annotations", help_text="Marqueurs et textes"
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Téléchargé par")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo de contravention"
        verbose_name_plural = "Photos de contraventions"
        ordering = ["contravention", "ordre"]
        indexes = [
            models.Index(fields=["contravention", "ordre"]),
        ]

    def __str__(self):
        return f"Photo {self.ordre} - {self.contravention.numero_pv}"

    def calculate_hash(self):
        """Calcule le hash SHA-256 du fichier"""
        if self.fichier:
            self.fichier.seek(0)
            file_hash = hashlib.sha256()
            for chunk in self.fichier.chunks():
                file_hash.update(chunk)
            return file_hash.hexdigest()
        return ""

    def verify_integrity(self):
        """Vérifie que le hash correspond au fichier"""
        if not self.hash_fichier:
            return False
        return self.calculate_hash() == self.hash_fichier

    def save(self, *args, **kwargs):
        """Override save pour compression et calcul du hash"""
        if self.fichier and hasattr(self.fichier, "file"):
            try:
                # Compression via ImageOptimizer
                from core.utils.image_optimizer import ImageOptimizer

                optimized = ImageOptimizer.optimize_document(self.fichier, document_type="contravention_photo")
                self.fichier = optimized
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error optimizing contravention photo: {str(e)}")

        # Calculer le hash
        if self.fichier and not self.hash_fichier:
            self.hash_fichier = self.calculate_hash()

        super().save(*args, **kwargs)


class Contestation(models.Model):
    """Gestion des contestations de contraventions"""

    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente"),
        ("EN_EXAMEN", "En examen"),
        ("ACCEPTEE", "Acceptée"),
        ("REJETEE", "Rejetée"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contravention = models.ForeignKey(
        Contravention, on_delete=models.CASCADE, related_name="contestations", verbose_name="Contravention"
    )
    numero_contestation = models.CharField(max_length=50, unique=True, verbose_name="Numéro de contestation")
    demandeur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contestations_soumises",
        verbose_name="Demandeur (utilisateur)",
    )
    nom_demandeur = models.CharField(max_length=200, verbose_name="Nom du demandeur")
    email_demandeur = models.EmailField(blank=True, verbose_name="Email du demandeur")
    telephone_demandeur = models.CharField(max_length=20, blank=True, verbose_name="Téléphone du demandeur")
    motif = models.TextField(verbose_name="Motif de la contestation")
    date_soumission = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="EN_ATTENTE", verbose_name="Statut")
    examine_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contestations_examinees",
        verbose_name="Examiné par",
    )
    date_examen = models.DateTimeField(null=True, blank=True, verbose_name="Date d'examen")
    decision_motif = models.TextField(blank=True, verbose_name="Motif de la décision")
    documents_justificatifs = models.JSONField(
        default=list, blank=True, verbose_name="Documents justificatifs", help_text="URLs des documents"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contestation"
        verbose_name_plural = "Contestations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["numero_contestation"]),
            models.Index(fields=["contravention", "statut"]),
            models.Index(fields=["statut"]),
        ]

    def __str__(self):
        return f"{self.numero_contestation} - {self.statut}"

    def generate_numero_contestation(self):
        """Génère un numéro de contestation unique"""
        date_str = timezone.now().strftime("%Y%m%d")
        alphabet = string.ascii_uppercase + string.digits
        random_id = "".join(secrets.choice(alphabet) for _ in range(6))

        numero = f"CONT-{date_str}-{random_id}"

        while Contestation.objects.filter(numero_contestation=numero).exists():
            random_id = "".join(secrets.choice(alphabet) for _ in range(6))
            numero = f"CONT-{date_str}-{random_id}"

        return numero

    def suspendre_delai_paiement(self):
        """Suspend le délai de paiement pendant l'examen"""
        if self.contravention.statut == "IMPAYEE":
            self.contravention.statut = "CONTESTEE"
            self.contravention.save()

    def reactiver_delai_paiement(self):
        """Réactive le délai si la contestation est rejetée"""
        if self.statut == "REJETEE" and self.contravention.statut == "CONTESTEE":
            self.contravention.statut = "IMPAYEE"
            self.contravention.save()

    def annuler_contravention(self):
        """Annule la contravention si la contestation est acceptée"""
        if self.statut == "ACCEPTEE":
            self.contravention.statut = "ANNULEE"
            self.contravention.save()

    def save(self, *args, **kwargs):
        """Override save pour générer le numéro de contestation"""
        if not self.numero_contestation:
            self.numero_contestation = self.generate_numero_contestation()

        # Suspendre le délai si nouvelle contestation
        if not self.pk and self.statut == "EN_ATTENTE":
            self.suspendre_delai_paiement()

        super().save(*args, **kwargs)


class ContraventionAuditLog(models.Model):
    """Journal d'audit immutable pour traçabilité"""

    ACTION_TYPE_CHOICES = [
        ("CREATE", "Création"),
        ("UPDATE", "Modification"),
        ("PAYMENT", "Paiement"),
        ("CANCEL", "Annulation"),
        ("CONTEST", "Contestation"),
        ("FOURRIERE", "Mise en fourrière"),
        ("RESTITUTION", "Restitution"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES, verbose_name="Type d'action")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Utilisateur")
    contravention = models.ForeignKey(
        Contravention,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Contravention",
    )
    action_data = models.JSONField(default=dict, blank=True, verbose_name="Données de l'action")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    previous_hash = models.CharField(
        max_length=64, blank=True, verbose_name="Hash précédent", help_text="Pour chaînage cryptographique"
    )
    current_hash = models.CharField(max_length=64, blank=True, verbose_name="Hash actuel")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")

    class Meta:
        verbose_name = "Log d'audit de contravention"
        verbose_name_plural = "Logs d'audit de contraventions"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["contravention", "timestamp"]),
            models.Index(fields=["action_type", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.timestamp}"

    @classmethod
    def get_last_hash(cls):
        """Récupère le hash du dernier enregistrement pour chaînage"""
        last_log = cls.objects.order_by("-timestamp").first()
        return last_log.current_hash if last_log else ""

    def calculate_hash(self):
        """Calcule le hash SHA-256 de cet enregistrement"""
        data = {
            "action_type": self.action_type,
            "user_id": str(self.user.id) if self.user else "",
            "contravention_id": str(self.contravention.id) if self.contravention else "",
            "action_data": self.action_data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else "",
            "previous_hash": self.previous_hash,
        }

        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

    def save(self, *args, **kwargs):
        """Override save pour calcul automatique du hash"""
        if not self.previous_hash:
            self.previous_hash = self.get_last_hash()

        # Sauvegarder d'abord pour avoir un timestamp
        if not self.pk:
            super().save(*args, **kwargs)

        # Calculer et mettre à jour le hash
        if not self.current_hash:
            self.current_hash = self.calculate_hash()
            # Mettre à jour uniquement le hash
            ContraventionAuditLog.objects.filter(pk=self.pk).update(current_hash=self.current_hash)
        else:
            super().save(*args, **kwargs)


class ConfigurationSysteme(models.Model):
    """
    Configuration globale du système de contraventions (Singleton).
    """

    id = models.AutoField(primary_key=True)

    # Délais de paiement
    delai_paiement_standard_jours = models.IntegerField(
        default=15,
        verbose_name="Délai de paiement standard (jours)",
        help_text="Nombre de jours pour payer une contravention standard",
    )
    delai_paiement_immediat_jours = models.IntegerField(
        default=1,
        verbose_name="Délai de paiement immédiat (jours)",
        help_text="Nombre de jours pour paiement immédiat sur place",
    )

    # Pénalités
    penalite_retard_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Pénalité de retard (%)",
        help_text="Pourcentage de majoration en cas de retard de paiement",
    )

    # Frais de fourrière
    frais_transport_fourriere_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("20000.00"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Frais de transport fourrière (Ariary)",
        help_text="Frais de transport vers la fourrière",
    )
    frais_gardiennage_journalier_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("10000.00"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Frais de gardiennage journalier (Ariary)",
        help_text="Frais de gardiennage par jour en fourrière",
    )
    duree_minimale_fourriere_jours = models.IntegerField(
        default=10, verbose_name="Durée minimale fourrière (jours)", help_text="Durée minimale de mise en fourrière"
    )
    duree_minimale_fourriere_perissable_jours = models.IntegerField(
        default=5,
        verbose_name="Durée minimale fourrière périssable (jours)",
        help_text="Durée minimale pour véhicules transportant des denrées périssables",
    )

    # Délais administratifs
    delai_annulation_directe_heures = models.IntegerField(
        default=24,
        verbose_name="Délai d'annulation directe (heures)",
        help_text="Délai pendant lequel l'agent peut annuler directement",
    )
    delai_contestation_jours = models.IntegerField(
        default=30,
        verbose_name="Délai de contestation (jours)",
        help_text="Nombre de jours pour contester une contravention",
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration du système"
        verbose_name_plural = "Configuration du système"

    def __str__(self):
        return "Configuration du système de contraventions"

    @classmethod
    def get_config(cls):
        """Récupère ou crée la configuration singleton"""
        config, created = cls.objects.get_or_create(pk=1)
        return config

    def save(self, *args, **kwargs):
        """Override pour garantir qu'il n'y a qu'une seule instance (pk=1)"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Empêche la suppression du singleton"""
        pass
