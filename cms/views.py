from decimal import Decimal

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView

from .models import FooterSettings, HeaderSettings, MenuItem, Page, PageSection, SiteSettings, ThemeSettings


class CMSBaseView(TemplateView):
    """Base view for CMS pages with context"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the helper function to ensure consistency and avoid code duplication
        context.update(get_cms_context())
        return context


class CMSHomeView(CMSBaseView):
    """Homepage view"""

    template_name = "cms/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get homepage
        try:
            homepage = Page.objects.filter(is_homepage=True, status="published").first()
        except Page.DoesNotExist:
            homepage = None

        # Get active sections for homepage
        sections = []
        if homepage:
            sections = homepage.sections.filter(is_active=True).order_by("order")

        context.update(
            {
                "homepage": homepage,
                "sections": sections,
                "page_title": _("Accueil"),
            }
        )

        return context


class CMSPageDetailView(DetailView):
    """Page detail view"""

    model = Page
    template_name = "cms/page_detail.html"
    context_object_name = "page"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Page.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.object
        language = get_language()

        # Get CMS base context (site settings, header, footer, menus, theme settings)
        # Use the helper function to ensure consistency across all views
        context.update(get_cms_context())

        # Get sections for this page
        sections = page.sections.filter(is_active=True).order_by("order")

        # Get translated title and meta description
        if language == "mg" and page.title_mg:
            page_title = page.title_mg
            meta_description = page.meta_description_mg or page.meta_description
        elif language == "fr" and page.title_fr:
            page_title = page.title_fr
            meta_description = page.meta_description_fr or page.meta_description
        else:
            page_title = page.title
            meta_description = page.meta_description

        # Add page-specific context
        context.update(
            {
                "sections": sections,
                "page_title": page_title,
                "meta_description": meta_description,
            }
        )

        return context

    def get_template_names(self):
        if self.object.template_name:
            return [self.object.template_name]
        return [self.template_name]


def get_cms_context():
    """Helper function to get CMS context for any view"""
    language = get_language()

    try:
        site_settings = SiteSettings.objects.filter(is_active=True).first()
    except SiteSettings.DoesNotExist:
        site_settings = None

    try:
        header_settings = HeaderSettings.objects.filter(is_active=True).first()
    except HeaderSettings.DoesNotExist:
        header_settings = None

    try:
        footer_settings = FooterSettings.objects.filter(is_active=True).first()
    except FooterSettings.DoesNotExist:
        footer_settings = None

    try:
        theme_settings = ThemeSettings.objects.filter(is_active=True).first()
    except ThemeSettings.DoesNotExist:
        theme_settings = None

    header_menu_items = (
        MenuItem.objects.filter(menu_location__in=["header", "both"], is_active=True, parent=None)
        .order_by("order")
        .prefetch_related("children")
    )

    footer_menu_items = (
        MenuItem.objects.filter(menu_location__in=["footer", "both"], is_active=True, parent=None)
        .order_by("order")
        .prefetch_related("children")
    )

    return {
        "site_settings": site_settings,
        "header_settings": header_settings,
        "footer_settings": footer_settings,
        "theme_settings": theme_settings,
        "header_menu_items": header_menu_items,
        "footer_menu_items": footer_menu_items,
        "current_language": language,
    }


class Home2View(CMSBaseView):
    """Hybrid homepage combining CMS (header/footer/content) with Velzon design components"""

    template_name = "cms/home2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get homepage from CMS
        try:
            homepage = Page.objects.filter(is_homepage=True, status="published").first()
        except Page.DoesNotExist:
            homepage = None

        # Get active sections for homepage
        sections = []
        if homepage:
            sections = homepage.sections.filter(is_active=True).order_by("order")

        context.update(
            {
                "homepage": homepage,
                "sections": sections,
                "page_title": _("Accueil"),
            }
        )

        return context


class PublicHomeView(TemplateView):
    """Public-facing home page view with modern design"""

    template_name = "cms/public_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get CMS settings using the existing helper function
        context.update(get_cms_context())
        
        # Get homepage from CMS Page model
        try:
            homepage = Page.objects.filter(is_homepage=True, status="published").first()
        except Page.DoesNotExist:
            homepage = None
        
        # Get active sections for homepage
        sections = []
        if homepage:
            sections = homepage.sections.filter(is_active=True).order_by("order")
        
        # Include user authentication status
        is_authenticated = self.request.user.is_authenticated
        
        # Get language preference from cookie (handled by Django i18n middleware)
        # The current language is already in context from get_cms_context()
        
        # Add page-specific context
        context.update({
            "homepage": homepage,
            "sections": sections,
            "page_title": _("Accueil"),
            "is_authenticated": is_authenticated,
        })
        
        return context



@csrf_exempt
@require_POST
def public_tax_simulation(request):
    """
    Public AJAX endpoint for tax simulation on the home page.
    Uses the actual tariff grids from the database.
    No authentication required.
    """
    try:
        from datetime import datetime
        from vehicles.models import GrilleTarifaire
        
        # Get parameters
        vehicle_type = request.POST.get('vehicle_type', '')
        annee_mise_circulation = request.POST.get('annee_mise_circulation', '')
        annee_fiscale = request.POST.get('annee_fiscale', str(datetime.now().year))
        
        # Validate required fields
        if not vehicle_type:
            return JsonResponse({
                'success': False,
                'message': _('Veuillez sélectionner un type de véhicule.')
            })
        
        if not annee_mise_circulation:
            return JsonResponse({
                'success': False,
                'message': _('Veuillez entrer une année de mise en service.')
            })
        
        try:
            annee_mise_circulation = int(annee_mise_circulation)
            annee_fiscale = int(annee_fiscale)
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': _('Année invalide.')
            })
        
        # Calculate vehicle age
        vehicle_age = annee_fiscale - annee_mise_circulation
        
        # Get base tax from tariff grid
        base_tax = Decimal('0')
        grid_info = None
        
        if vehicle_type == 'terrestre':
            puissance = request.POST.get('puissance', '')
            source_energie = request.POST.get('source_energie', 'Essence')
            
            if not puissance:
                return JsonResponse({
                    'success': False,
                    'message': _('Veuillez entrer la puissance fiscale (CV).')
                })
            
            try:
                puissance = int(puissance)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': _('Puissance invalide.')
                })
            
            # Validate source_energie
            valid_sources = ['Essence', 'Diesel', 'Electrique', 'Hybride']
            if source_energie not in valid_sources:
                source_energie = 'Essence'
            
            # Determine age bracket
            if vehicle_age <= 5:
                age_min = 0
                age_max = 5
            elif vehicle_age <= 10:
                age_min = 6
                age_max = 10
            elif vehicle_age <= 20:
                age_min = 11
                age_max = 20
            else:
                age_min = 21
                age_max = None
            
            # Find applicable tariff grid for terrestrial vehicles (PROGRESSIVE type)
            # Match by power range, energy source, and age bracket
            grid_query = GrilleTarifaire.objects.filter(
                grid_type='PROGRESSIVE',
                annee_fiscale=annee_fiscale,
                puissance_min_cv__lte=puissance,
                source_energie=source_energie,
                age_min_annees=age_min,
                est_active=True
            )
            
            # Handle puissance_max_cv (can be None for 16+ CV)
            grid = grid_query.filter(
                puissance_max_cv__gte=puissance
            ).first()
            
            # If not found, try with puissance_max_cv=None (for 16+ CV range)
            if not grid:
                grid = grid_query.filter(puissance_max_cv__isnull=True).first()
            
            if grid:
                base_tax = grid.montant_ariary
                puissance_range = f'{grid.puissance_min_cv}'
                if grid.puissance_max_cv:
                    puissance_range += f'-{grid.puissance_max_cv}'
                else:
                    puissance_range += '+'
                
                age_range = f'{grid.age_min_annees}'
                if grid.age_max_annees:
                    age_range += f'-{grid.age_max_annees}'
                else:
                    age_range += '+'
                
                grid_info = {
                    'type': 'TERRESTRE',
                    'puissance_range': f'{puissance_range} CV',
                    'source_energie': source_energie,
                    'age_range': f'{age_range} ans',
                    'montant': str(grid.montant_ariary)
                }
            else:
                # Fallback: use a simple calculation if no grid found
                # Based on typical Madagascar tax rates (Essence, 0-5 years)
                if puissance <= 4:
                    base_tax = Decimal('15000')
                elif puissance <= 9:
                    base_tax = Decimal('30000')
                elif puissance <= 12:
                    base_tax = Decimal('60000')
                elif puissance <= 15:
                    base_tax = Decimal('90000')
                else:
                    base_tax = Decimal('180000')
                
                # Apply energy source modifier
                if source_energie == 'Diesel':
                    base_tax = base_tax * Decimal('1.33')
                elif source_energie == 'Electrique':
                    base_tax = base_tax * Decimal('0.33')
                elif source_energie == 'Hybride':
                    base_tax = base_tax * Decimal('0.67')
                
                # Apply age modifier
                if vehicle_age > 20:
                    base_tax = base_tax * Decimal('7.5')
                elif vehicle_age > 10:
                    base_tax = base_tax * Decimal('6')
                elif vehicle_age > 5:
                    base_tax = base_tax * Decimal('2.5')
                
                base_tax = base_tax.quantize(Decimal('1'))
        
        elif vehicle_type == 'maritime':
            longueur = request.POST.get('longueur', '')
            tonnage = request.POST.get('tonnage', '')
            
            if not longueur or not tonnage:
                return JsonResponse({
                    'success': False,
                    'message': _('Veuillez entrer la longueur et le tonnage.')
                })
            
            try:
                longueur = Decimal(longueur)
                tonnage = Decimal(tonnage)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': _('Valeurs invalides.')
                })
            
            # Find applicable tariff grid for maritime vehicles
            grid = GrilleTarifaire.objects.filter(
                grid_type='FLAT_MARITIME',
                annee_fiscale=annee_fiscale,
                longueur_min_metres__lte=longueur,
                est_active=True
            ).order_by('-longueur_min_metres').first()
            
            if grid:
                base_tax = grid.montant_ariary
                grid_info = {
                    'type': 'MARITIME',
                    'category': grid.maritime_category,
                    'montant': str(grid.montant_ariary)
                }
            else:
                # Fallback calculation based on length
                if longueur < 7:
                    base_tax = Decimal('100000')
                elif longueur < 12:
                    base_tax = Decimal('200000')
                elif longueur < 24:
                    base_tax = Decimal('400000')
                else:
                    base_tax = Decimal('800000')
        
        elif vehicle_type == 'aerien':
            masse = request.POST.get('masse_decollage', '')
            
            if not masse:
                return JsonResponse({
                    'success': False,
                    'message': _('Veuillez entrer la masse maximale au décollage.')
                })
            
            try:
                masse = int(masse)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': _('Masse invalide.')
                })
            
            # Find applicable tariff grid for aerial vehicles
            grid = GrilleTarifaire.objects.filter(
                grid_type='FLAT_AERIAL',
                annee_fiscale=annee_fiscale,
                est_active=True
            ).first()
            
            if grid:
                base_tax = grid.montant_ariary
                grid_info = {
                    'type': 'AERIEN',
                    'aerial_type': grid.aerial_type,
                    'montant': str(grid.montant_ariary)
                }
            else:
                # Fallback calculation based on mass
                if masse <= 1000:
                    base_tax = Decimal('200000')
                elif masse <= 5700:
                    base_tax = Decimal('500000')
                elif masse <= 25000:
                    base_tax = Decimal('1000000')
                else:
                    base_tax = Decimal('2000000')
        
        else:
            return JsonResponse({
                'success': False,
                'message': _('Type de véhicule non reconnu.')
            })
        
        # For terrestrial vehicles, age is already factored into the tariff grid
        # For maritime and aerial, we use a flat rate with no age coefficient
        # The age coefficient is kept at 1.0 since the grid already accounts for age
        age_coef = Decimal('1.0')
        
        # Calculate total tax
        total_tax = (base_tax * age_coef).quantize(Decimal('1'))
        
        return JsonResponse({
            'success': True,
            'base_tax': str(base_tax),
            'age_coefficient': str(age_coef),
            'total_tax': str(total_tax),
            'vehicle_age': vehicle_age,
            'grid_info': grid_info,
            'message': _('Taxe calculée avec succès.')
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in public_tax_simulation: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': _('Erreur lors du calcul de la taxe.')
        })
