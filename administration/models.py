from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class AgentVerification(models.Model):
    """Verification agents for QR code validation"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='agent_verification'
    )
    numero_badge = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name="Numéro de badge"
    )
    zone_affectation = models.CharField(
        max_length=100,
        verbose_name="Zone d'affectation"
    )
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Agent de vérification"
        verbose_name_plural = "Agents de vérification"
        indexes = [
            models.Index(fields=['numero_badge']),
            models.Index(fields=['zone_affectation']),
            models.Index(fields=['est_actif']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.numero_badge}"

class VerificationQR(models.Model):
    """QR code verification logs"""
    
    STATUT_CHOICES = [
        ('valide', 'Valide'),
        ('expire', 'Expiré'),
        ('invalide', 'Invalide'),
        ('deja_utilise', 'Déjà utilisé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        AgentVerification, 
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    qr_code = models.ForeignKey(
        'payments.QRCode', 
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    statut_verification = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES,
        verbose_name="Statut de vérification"
    )
    date_verification = models.DateTimeField(auto_now_add=True)
    localisation_gps = models.JSONField(
        null=True, blank=True,
        verbose_name="Localisation GPS",
        help_text="Coordonnées GPS de la vérification"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes de vérification"
    )
    
    class Meta:
        verbose_name = "Vérification QR"
        verbose_name_plural = "Vérifications QR"
        ordering = ['-date_verification']
        indexes = [
            models.Index(fields=['agent']),
            models.Index(fields=['qr_code']),
            models.Index(fields=['statut_verification']),
            models.Index(fields=['date_verification']),
        ]
    
    def __str__(self):
        return f"Vérification {self.qr_code.code} par {self.agent.user.username}"

class StatistiquesPlateforme(models.Model):
    """Platform statistics and metrics"""
    
    TYPE_CHOICES = [
        ('utilisateurs_actifs', 'Utilisateurs actifs'),
        ('vehicules_enregistres', 'Véhicules enregistrés'),
        ('paiements_jour', 'Paiements du jour'),
        ('revenus_jour', 'Revenus du jour'),
        ('qr_generes', 'QR codes générés'),
        ('verifications_qr', 'Vérifications QR'),
    ]
    
    type_statistique = models.CharField(
        max_length=50, 
        choices=TYPE_CHOICES,
        verbose_name="Type de statistique"
    )
    valeur = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        verbose_name="Valeur"
    )
    date_statistique = models.DateField(verbose_name="Date de la statistique")
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Métadonnées supplémentaires"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Statistique plateforme"
        verbose_name_plural = "Statistiques plateforme"
        unique_together = [['type_statistique', 'date_statistique']]
        ordering = ['-date_statistique', 'type_statistique']
        indexes = [
            models.Index(fields=['type_statistique', 'date_statistique']),
            models.Index(fields=['date_statistique']),
        ]
    
    def __str__(self):
        return f"{self.get_type_statistique_display()} - {self.date_statistique}: {self.valeur}"

class ConfigurationSysteme(models.Model):
    """System configuration settings"""
    
    TYPE_CHOICES = [
        ('taux_taxe', 'Taux de taxe'),
        ('duree_validite_qr', 'Durée validité QR (jours)'),
        ('montant_minimum_paiement', 'Montant minimum paiement'),
        ('frais_transaction', 'Frais de transaction (%)'),
        ('email_admin', 'Email administrateur'),
        ('sms_api_key', 'Clé API SMS'),
        ('mobile_money_config', 'Configuration Mobile Money'),
    ]
    
    cle = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Clé de configuration"
    )
    type_config = models.CharField(
        max_length=50, 
        choices=TYPE_CHOICES,
        verbose_name="Type de configuration"
    )
    valeur = models.TextField(verbose_name="Valeur")
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    modifie_par = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Modifié par"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuration système"
        verbose_name_plural = "Configurations système"
        indexes = [
            models.Index(fields=['cle']),
            models.Index(fields=['type_config']),
            models.Index(fields=['est_actif']),
        ]
    
    def __str__(self):
        return f"{self.cle}: {self.valeur}"
    
    @classmethod
    def get_config(cls, cle, default=None):
        """Get configuration value by key"""
        try:
            config = cls.objects.get(cle=cle, est_actif=True)
            return config.valeur
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_config(cls, cle, valeur, user=None, description=""):
        """Set configuration value"""
        config, created = cls.objects.get_or_create(
            cle=cle,
            defaults={
                'valeur': valeur,
                'description': description,
                'modifie_par': user,
            }
        )
        if not created:
            config.valeur = valeur
            config.modifie_par = user
            config.save(update_fields=['valeur', 'modifie_par', 'date_modification'])
        return config


class AdminUserProfile(models.Model):
    """Extended profile for admin users with 2FA and security features"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )
    
    # 2FA Settings
    totp_secret = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="TOTP Secret"
    )
    is_2fa_enabled = models.BooleanField(
        default=False,
        verbose_name="2FA activé"
    )
    backup_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Codes de secours"
    )
    
    # IP Whitelisting
    ip_whitelist = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Liste blanche IP",
        help_text="Liste des adresses IP autorisées (format: ['192.168.1.1', '10.0.0.0/24'])"
    )
    is_ip_whitelist_enabled = models.BooleanField(
        default=False,
        verbose_name="Liste blanche IP activée"
    )
    
    # Security Tracking
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dernière IP de connexion"
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        verbose_name="Tentatives de connexion échouées"
    )
    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Compte verrouillé jusqu'à"
    )
    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernier changement de mot de passe"
    )
    
    # Preferences
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Clair'), ('dark', 'Sombre')],
        default='light',
        verbose_name="Thème préféré"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil administrateur"
        verbose_name_plural = "Profils administrateurs"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_2fa_enabled']),
            models.Index(fields=['last_login_ip']),
        ]
    
    def __str__(self):
        return f"Admin Profile: {self.user.username}"
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        from django.utils import timezone
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def reset_failed_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def increment_failed_attempts(self):
        """Increment failed login attempts and lock if threshold reached"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 15 minutes
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timedelta(minutes=15)
        
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def is_ip_allowed(self, ip_address):
        """Check if IP address is in whitelist"""
        if not self.is_ip_whitelist_enabled:
            return True
        
        if not self.ip_whitelist:
            return False
        
        import ipaddress
        try:
            ip = ipaddress.ip_address(ip_address)
            for allowed in self.ip_whitelist:
                if '/' in allowed:
                    # CIDR notation
                    if ip in ipaddress.ip_network(allowed, strict=False):
                        return True
                else:
                    # Single IP
                    if str(ip) == allowed:
                        return True
        except ValueError:
            return False
        
        return False


class PermissionGroup(models.Model):
    """Custom permission groups for RBAC"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du groupe"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    permissions = models.JSONField(
        default=dict,
        verbose_name="Permissions",
        help_text="Format: {'module': ['view', 'create', 'edit', 'delete']}"
    )
    users = models.ManyToManyField(
        User,
        related_name='custom_permission_groups',
        blank=True,
        verbose_name="Utilisateurs"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_permission_groups',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Groupe de permissions"
        verbose_name_plural = "Groupes de permissions"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def has_permission(self, module, action):
        """Check if group has specific permission"""
        if module in self.permissions:
            return action in self.permissions.get(module, [])
        return False


class AdminSession(models.Model):
    """Track admin user sessions"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='admin_sessions'
    )
    session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Clé de session"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(
        verbose_name="User Agent"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière activité"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Est actif"
    )
    
    class Meta:
        verbose_name = "Session administrateur"
        verbose_name_plural = "Sessions administrateurs"
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} ({self.created_at})"
    
    def is_expired(self, timeout_minutes=30):
        """Check if session is expired"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.is_active:
            return True
        
        timeout = timezone.now() - timedelta(minutes=timeout_minutes)
        return self.last_activity < timeout


class DataVersion(models.Model):
    """Track version history for records"""
    
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType
    
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Type de contenu"
    )
    object_id = models.CharField(
        max_length=50,
        verbose_name="ID de l'objet"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    version_number = models.IntegerField(
        verbose_name="Numéro de version"
    )
    data_snapshot = models.JSONField(
        verbose_name="Snapshot des données"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modifié par"
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Modifié le"
    )
    change_reason = models.TextField(
        blank=True,
        verbose_name="Raison du changement"
    )
    
    class Meta:
        verbose_name = "Version de données"
        verbose_name_plural = "Versions de données"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['changed_at']),
        ]
        unique_together = [['content_type', 'object_id', 'version_number']]
    
    def __str__(self):
        return f"Version {self.version_number} - {self.content_type} #{self.object_id}"


class SMTPConfiguration(models.Model):
    """SMTP Configuration for sending emails"""
    
    ENCRYPTION_CHOICES = [
        ('none', 'Aucun'),
        ('tls', 'TLS'),
        ('ssl', 'SSL'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la configuration",
        help_text="Nom descriptif pour identifier cette configuration SMTP"
    )
    host = models.CharField(
        max_length=255,
        verbose_name="Serveur SMTP",
        help_text="Exemple: smtp.gmail.com, smtp.office365.com"
    )
    port = models.IntegerField(
        default=587,
        verbose_name="Port SMTP",
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        help_text="Port standard: 587 (TLS), 465 (SSL), 25 (non sécurisé)"
    )
    encryption = models.CharField(
        max_length=10,
        choices=ENCRYPTION_CHOICES,
        default='tls',
        verbose_name="Type de chiffrement"
    )
    username = models.CharField(
        max_length=255,
        verbose_name="Nom d'utilisateur",
        help_text="Adresse email ou nom d'utilisateur SMTP"
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Mot de passe",
        help_text="Mot de passe ou mot de passe d'application"
    )
    from_email = models.EmailField(
        verbose_name="Email expéditeur",
        help_text="Adresse email qui apparaîtra comme expéditeur"
    )
    from_name = models.CharField(
        max_length=100,
        default="Tax Collector",
        verbose_name="Nom de l'expéditeur",
        help_text="Nom qui apparaîtra comme expéditeur"
    )
    reply_to_email = models.EmailField(
        blank=True,
        verbose_name="Email de réponse",
        help_text="Adresse email pour les réponses (optionnel)"
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Configuration active",
        help_text="Une seule configuration peut être active à la fois"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Configuration vérifiée",
        help_text="Indique si la configuration a été testée avec succès"
    )
    last_test_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière date de test"
    )
    last_test_result = models.TextField(
        blank=True,
        verbose_name="Résultat du dernier test"
    )
    daily_limit = models.IntegerField(
        default=500,
        verbose_name="Limite quotidienne d'emails",
        validators=[MinValueValidator(0)],
        help_text="Nombre maximum d'emails par jour (0 = illimité)"
    )
    emails_sent_today = models.IntegerField(
        default=0,
        verbose_name="Emails envoyés aujourd'hui"
    )
    last_reset_date = models.DateField(
        auto_now_add=True,
        verbose_name="Dernière réinitialisation du compteur"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Notes ou description de cette configuration"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='smtp_configs_created',
        verbose_name="Créé par"
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='smtp_configs_modified',
        verbose_name="Modifié par"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )
    
    class Meta:
        verbose_name = "Configuration SMTP"
        verbose_name_plural = "Configurations SMTP"
        ordering = ['-is_active', '-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"
    
    def save(self, *args, **kwargs):
        # Ensure only one config is active
        if self.is_active:
            SMTPConfiguration.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_config(cls):
        """Get the currently active SMTP configuration"""
        return cls.objects.filter(is_active=True).first()
    
    def can_send_email(self):
        """Check if daily limit is reached"""
        if self.daily_limit == 0:
            return True
        
        # Reset counter if new day
        from django.utils import timezone
        today = timezone.now().date()
        if self.last_reset_date != today:
            self.emails_sent_today = 0
            self.last_reset_date = today
            self.save(update_fields=['emails_sent_today', 'last_reset_date'])
            
        return self.emails_sent_today < self.daily_limit
    
    def increment_counter(self):
        """Increment sent emails counter"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_reset_date != today:
            self.emails_sent_today = 1
            self.last_reset_date = today
        else:
            self.emails_sent_today += 1
            
        self.save(update_fields=['emails_sent_today', 'last_reset_date'])

    def test_connection(self):
        """Test SMTP connection and return result"""
        import smtplib
        import ssl
        from django.utils import timezone
        
        try:
            # Create SSL context that ignores certificate errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Auto-detect SSL for port 465
            use_ssl = self.encryption == "ssl" or self.port == 465
            use_tls = self.encryption == "tls" and self.port != 465
            
            if use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, context=ssl_context, timeout=10)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=10)
                if use_tls:
                    server.starttls(context=ssl_context)
            
            server.login(self.username, self.password)
            server.quit()
            
            self.is_verified = True
            self.last_test_date = timezone.now()
            self.last_test_result = "✓ Connexion réussie"
            self.save(update_fields=["is_verified", "last_test_date", "last_test_result"])
            
            return True, "Connexion SMTP réussie"
        except Exception as e:
            error_msg = f"✗ Erreur: {str(e)}"
            self.is_verified = False
            self.last_test_date = timezone.now()
            self.last_test_result = error_msg
            self.save(update_fields=["is_verified", "last_test_date", "last_test_result"])
            return False, error_msg


class EmailLog(models.Model):
    """Log of sent emails"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
        ('bounced', 'Rejeté'),
    ]
    
    recipient = models.EmailField(verbose_name="Destinataire")
    subject = models.CharField(max_length=255, verbose_name="Sujet")
    body = models.TextField(verbose_name="Corps du message")
    html_body = models.TextField(blank=True, verbose_name="Corps HTML")
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    
    smtp_config = models.ForeignKey(
        SMTPConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        related_name='email_logs',
        verbose_name="Configuration SMTP"
    )
    
    email_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Type d'email",
        help_text="Ex: reminder, notification, verification"
    )
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Type d'objet lié"
    )
    related_object_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="ID de l'objet lié"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Envoyé le")
    
    class Meta:
        verbose_name = "Journal d'email"
        verbose_name_plural = "Journaux d'emails"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['status']),
            models.Index(fields=['email_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} -> {self.recipient} ({self.status})"
