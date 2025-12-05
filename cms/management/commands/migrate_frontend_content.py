from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from cms.models import FooterSettings, HeaderSettings, MenuItem, Page, PageSection, SectionItem, SiteSettings


class Command(BaseCommand):
    help = "Migrate existing frontend content to CMS"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting frontend content migration..."))

        # 1. Create Site Settings
        self.stdout.write("Creating site settings...")
        site_settings, created = SiteSettings.objects.get_or_create(
            is_active=True,
            defaults={
                "site_name": "Tax Collector",
                "site_tagline": "Plateforme de Taxe Véhicules",
                "contact_email": "contact@taxcollector.mg",
                "contact_phone": "+261 20 XX XXX XX",
                "contact_address": "Ministère des Transports\nAntananarivo, Madagascar\nBP 12345",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Site settings created"))
        else:
            self.stdout.write(self.style.WARNING("Site settings already exist"))

        # 2. Create Header Settings
        self.stdout.write("Creating header settings...")
        header_settings, created = HeaderSettings.objects.get_or_create(
            is_active=True,
            defaults={
                "site_name": "Tax Collector",
                "site_name_fr": "Tax Collector",
                "site_name_mg": "Tax Collector",
                "logo_alt_text": "Tax Collector",
                "show_search": False,
                "show_language_switcher": True,
                "background_color": "#1a73e8",
                "text_color": "#ffffff",
                "is_sticky": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Header settings created"))
        else:
            self.stdout.write(self.style.WARNING("Header settings already exist"))

        # 3. Create Footer Settings
        self.stdout.write("Creating footer settings...")
        footer_settings, created = FooterSettings.objects.get_or_create(
            is_active=True,
            defaults={
                "copyright_text": "© Tax Collector. Tous droits réservés.",
                "copyright_text_fr": "© Tax Collector. Tous droits réservés.",
                "copyright_text_mg": "© Tax Collector. Tous droits réservés.",
                "description": "La plateforme officielle pour la gestion et le paiement des taxes véhicules.",
                "description_fr": "La plateforme officielle pour la gestion et le paiement des taxes véhicules.",
                "description_mg": "La plateforme officielle pour la gestion et le paiement des taxes véhicules.",
                "show_social_links": True,
                "show_newsletter": False,
                "background_color": "#212529",
                "text_color": "#ffffff",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Footer settings created"))
        else:
            self.stdout.write(self.style.WARNING("Footer settings already exist"))

        # 4. Create Menu Items
        self.stdout.write("Creating menu items...")
        menu_items_data = [
            {
                "title": "Accueil",
                "title_fr": "Accueil",
                "title_mg": "Fidirana",
                "url": "/",
                "icon": "fas fa-home",
                "menu_location": "both",
                "order": 1,
            },
            {
                "title": "À propos",
                "title_fr": "À propos",
                "title_mg": "Momba",
                "url": "/page/about/",
                "icon": "fas fa-info-circle",
                "menu_location": "both",
                "order": 2,
            },
            {
                "title": "Contact",
                "title_fr": "Contact",
                "title_mg": "Fifandraisana",
                "url": "/page/contact/",
                "icon": "fas fa-envelope",
                "menu_location": "both",
                "order": 3,
            },
            {
                "title": "Vérifier QR",
                "title_fr": "Vérifier QR",
                "title_mg": "Hamarinina QR",
                "url": "/app/qr-verification/",
                "icon": "fas fa-qrcode",
                "menu_location": "header",
                "order": 4,
            },
        ]

        for item_data in menu_items_data:
            menu_item, created = MenuItem.objects.get_or_create(url=item_data["url"], defaults=item_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Menu item "{item_data["title"]}" created'))
            else:
                self.stdout.write(self.style.WARNING(f'Menu item "{item_data["title"]}" already exists'))

        # 5. Create Homepage Sections
        self.stdout.write("Creating homepage sections...")

        # Hero Section
        hero_section, created = PageSection.objects.get_or_create(
            name="homepage-hero",
            defaults={
                "section_type": "hero",
                "title": "Plateforme de Taxe Véhicules",
                "title_fr": "Plateforme de Taxe Véhicules",
                "title_mg": "Plateforme de Taxe Véhicules",
                "subtitle": "Gérez et payez vos taxes véhicules en ligne de manière simple et sécurisée",
                "subtitle_fr": "Gérez et payez vos taxes véhicules en ligne de manière simple et sécurisée",
                "subtitle_mg": "Gérez et payez vos taxes véhicules en ligne de manière simple et sécurisée",
                "background_color": "#667eea",
                "text_color": "#ffffff",
                "order": 1,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Hero section created"))

        # Features Section
        features_section, created = PageSection.objects.get_or_create(
            name="homepage-features",
            defaults={
                "section_type": "features",
                "title": "Nos Fonctionnalités",
                "title_fr": "Nos Fonctionnalités",
                "title_mg": "Ny Fonctionnalités",
                "subtitle": "Des solutions innovantes pour simplifier le paiement de vos taxes",
                "subtitle_fr": "Des solutions innovantes pour simplifier le paiement de vos taxes",
                "subtitle_mg": "Des solutions innovantes pour simplifier le paiement de vos taxes",
                "background_color": "#f8f9fa",
                "text_color": "#000000",
                "order": 2,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Features section created"))

            # Create feature items
            feature_items = [
                {
                    "title": "Paiement Mobile",
                    "title_fr": "Paiement Mobile",
                    "title_mg": "Paiement Mobile",
                    "description": "Payez vos taxes en toute simplicité avec MVola, Orange Money ou Airtel Money",
                    "description_fr": "Payez vos taxes en toute simplicité avec MVola, Orange Money ou Airtel Money",
                    "description_mg": "Payez vos taxes en toute simplicité avec MVola, Orange Money ou Airtel Money",
                    "icon": "fas fa-mobile-alt",
                    "order": 1,
                },
                {
                    "title": "QR Code Sécurisé",
                    "title_fr": "QR Code Sécurisé",
                    "title_mg": "QR Code Sécurisé",
                    "description": "Recevez un QR code unique pour prouver le paiement de vos taxes",
                    "description_fr": "Recevez un QR code unique pour prouver le paiement de vos taxes",
                    "description_mg": "Recevez un QR code unique pour prouver le paiement de vos taxes",
                    "icon": "fas fa-qrcode",
                    "order": 2,
                },
                {
                    "title": "Suivi en Temps Réel",
                    "title_fr": "Suivi en Temps Réel",
                    "title_mg": "Suivi en Temps Réel",
                    "description": "Suivez l'état de vos paiements et recevez des notifications en temps réel",
                    "description_fr": "Suivez l'état de vos paiements et recevez des notifications en temps réel",
                    "description_mg": "Suivez l'état de vos paiements et recevez des notifications en temps réel",
                    "icon": "fas fa-chart-line",
                    "order": 3,
                },
            ]

            for item_data in feature_items:
                SectionItem.objects.get_or_create(
                    section=features_section, title=item_data["title"], defaults=item_data
                )

        # 6. Create Homepage
        self.stdout.write("Creating homepage...")
        homepage, created = Page.objects.get_or_create(
            slug="home",
            defaults={
                "title": "Accueil",
                "title_fr": "Accueil",
                "title_mg": "Fidirana",
                "meta_description": "Plateforme de Taxe Véhicules - Madagascar",
                "meta_description_fr": "Plateforme de Taxe Véhicules - Madagascar",
                "meta_description_mg": "Plateforme de Taxe Véhicules - Madagascar",
                "status": "published",
                "is_homepage": True,
                "order": 1,
            },
        )
        if created:
            homepage.sections.add(hero_section, features_section)
            self.stdout.write(self.style.SUCCESS("✓ Homepage created"))
        else:
            self.stdout.write(self.style.WARNING("Homepage already exists"))

        # 7. Create About Page
        self.stdout.write("Creating about page...")
        about_page, created = Page.objects.get_or_create(
            slug="about",
            defaults={
                "title": "À propos",
                "title_fr": "À propos",
                "title_mg": "Momba",
                "meta_description": "Informations sur la plateforme de collecte de taxe véhicules",
                "meta_description_fr": "Informations sur la plateforme de collecte de taxe véhicules",
                "meta_description_mg": "Informations sur la plateforme de collecte de taxe véhicules",
                "content": "<p>Découvrez notre mission et nos services pour la gestion des taxes véhicules à Madagascar</p>",
                "content_fr": "<p>Découvrez notre mission et nos services pour la gestion des taxes véhicules à Madagascar</p>",
                "content_mg": "<p>Découvrez notre mission et nos services pour la gestion des taxes véhicules à Madagascar</p>",
                "status": "published",
                "is_homepage": False,
                "order": 2,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ About page created"))
        else:
            self.stdout.write(self.style.WARNING("About page already exists"))

        # 8. Create Contact Page
        self.stdout.write("Creating contact page...")
        contact_page, created = Page.objects.get_or_create(
            slug="contact",
            defaults={
                "title": "Contact",
                "title_fr": "Contact",
                "title_mg": "Fifandraisana",
                "meta_description": "Contactez-nous pour toute question ou assistance",
                "meta_description_fr": "Contactez-nous pour toute question ou assistance",
                "meta_description_mg": "Contactez-nous pour toute question ou assistance",
                "content": "<p>Nous sommes là pour vous aider. N'hésitez pas à nous contacter pour toute question ou assistance.</p>",
                "content_fr": "<p>Nous sommes là pour vous aider. N'hésitez pas à nous contacter pour toute question ou assistance.</p>",
                "content_mg": "<p>Nous sommes là pour vous aider. N'hésitez pas à nous contacter pour toute question ou assistance.</p>",
                "status": "published",
                "is_homepage": False,
                "order": 3,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Contact page created"))
        else:
            self.stdout.write(self.style.WARNING("Contact page already exists"))

        self.stdout.write(self.style.SUCCESS("\n✓ Frontend content migration completed successfully!"))
        self.stdout.write(self.style.SUCCESS("You can now manage your frontend content from the Django admin panel."))
