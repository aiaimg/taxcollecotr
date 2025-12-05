from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """General site settings"""

    site_name = models.CharField(max_length=200, default="Tax Collector", verbose_name=_("Site Name"))
    site_tagline = models.CharField(max_length=500, blank=True, verbose_name=_("Site Tagline"))
    site_logo = models.ImageField(upload_to="cms/logos/", blank=True, null=True, verbose_name=_("Site Logo"))
    site_favicon = models.ImageField(upload_to="cms/favicons/", blank=True, null=True, verbose_name=_("Site Favicon"))
    contact_email = models.EmailField(default="contact@taxcollector.mg", verbose_name=_("Contact Email"))
    contact_phone = models.CharField(max_length=50, blank=True, verbose_name=_("Contact Phone"))
    contact_address = models.TextField(blank=True, verbose_name=_("Contact Address"))
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook URL"))
    twitter_url = models.URLField(blank=True, verbose_name=_("Twitter URL"))
    linkedin_url = models.URLField(blank=True, verbose_name=_("LinkedIn URL"))
    instagram_url = models.URLField(blank=True, verbose_name=_("Instagram URL"))
    youtube_url = models.URLField(blank=True, verbose_name=_("YouTube URL"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Site Settings")
        verbose_name_plural = _("Site Settings")
        ordering = ["-updated_at"]

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one active site settings instance
        if self.is_active:
            SiteSettings.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class MenuItem(models.Model):
    """Navigation menu items"""

    MENU_LOCATION_CHOICES = [
        ("header", _("Header")),
        ("footer", _("Footer")),
        ("both", _("Both")),
    ]

    title = models.CharField(max_length=200, verbose_name=_("Title"))
    title_fr = models.CharField(max_length=200, blank=True, verbose_name=_("Title (French)"))
    title_mg = models.CharField(max_length=200, blank=True, verbose_name=_("Title (Malagasy)"))
    url = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("URL or path (e.g., /about/ or https://example.com)"),
        verbose_name=_("URL"),
    )
    icon = models.CharField(
        max_length=100, blank=True, help_text=_("Font Awesome icon class (e.g., fa-home)"), verbose_name=_("Icon")
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent Menu Item"),
    )
    menu_location = models.CharField(
        max_length=10, choices=MENU_LOCATION_CHOICES, default="header", verbose_name=_("Menu Location")
    )
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    open_in_new_tab = models.BooleanField(default=False, verbose_name=_("Open in New Tab"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.url:
            return self.url
        return reverse("cms:page_detail", kwargs={"slug": self.slug}) if hasattr(self, "slug") else "/"


class PageSection(models.Model):
    """Reusable page sections (hero, features, testimonials, etc.)"""

    SECTION_TYPE_CHOICES = [
        ("hero", _("Hero Section")),
        ("features", _("Features Section")),
        ("testimonials", _("Testimonials Section")),
        ("cta", _("Call to Action")),
        ("content", _("Content Section")),
        ("stats", _("Statistics Section")),
        ("gallery", _("Gallery Section")),
        ("faq", _("FAQ Section")),
        ("contact", _("Contact Section")),
        ("custom", _("Custom Section")),
    ]

    name = models.CharField(max_length=200, unique=True, verbose_name=_("Section Name"))
    section_type = models.CharField(
        max_length=50, choices=SECTION_TYPE_CHOICES, default="content", verbose_name=_("Section Type")
    )
    title = models.CharField(max_length=500, blank=True, verbose_name=_("Title"))
    title_fr = models.CharField(max_length=500, blank=True, verbose_name=_("Title (French)"))
    title_mg = models.CharField(max_length=500, blank=True, verbose_name=_("Title (Malagasy)"))
    subtitle = models.TextField(blank=True, verbose_name=_("Subtitle"))
    subtitle_fr = models.TextField(blank=True, verbose_name=_("Subtitle (French)"))
    subtitle_mg = models.TextField(blank=True, verbose_name=_("Subtitle (Malagasy)"))
    content = models.TextField(blank=True, verbose_name=_("Content"))
    content_fr = models.TextField(blank=True, verbose_name=_("Content (French)"))
    content_mg = models.TextField(blank=True, verbose_name=_("Content (Malagasy)"))
    background_image = models.ImageField(
        upload_to="cms/sections/", blank=True, null=True, verbose_name=_("Background Image")
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        default="#ffffff",
        help_text=_("Hex color code (e.g., #ffffff)"),
        verbose_name=_("Background Color"),
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        default="#000000",
        help_text=_("Hex color code (e.g., #000000)"),
        verbose_name=_("Text Color"),
    )
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Page Section")
        verbose_name_plural = _("Page Sections")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_section_type_display()})"


class SectionItem(models.Model):
    """Items within a section (e.g., individual features, testimonials)"""

    section = models.ForeignKey(PageSection, on_delete=models.CASCADE, related_name="items", verbose_name=_("Section"))
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    title_fr = models.CharField(max_length=200, blank=True, verbose_name=_("Title (French)"))
    title_mg = models.CharField(max_length=200, blank=True, verbose_name=_("Title (Malagasy)"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    description_fr = models.TextField(blank=True, verbose_name=_("Description (French)"))
    description_mg = models.TextField(blank=True, verbose_name=_("Description (Malagasy)"))
    icon = models.CharField(max_length=100, blank=True, help_text=_("Font Awesome icon class"), verbose_name=_("Icon"))
    image = models.ImageField(upload_to="cms/section_items/", blank=True, null=True, verbose_name=_("Image"))
    link_url = models.CharField(max_length=500, blank=True, verbose_name=_("Link URL"))
    link_text = models.CharField(max_length=200, blank=True, verbose_name=_("Link Text"))
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Section Item")
        verbose_name_plural = _("Section Items")
        ordering = ["order", "title"]

    def __str__(self):
        return f"{self.section.name} - {self.title}"


class Page(models.Model):
    """CMS Pages"""

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("published", _("Published")),
        ("archived", _("Archived")),
    ]

    title = models.CharField(max_length=500, verbose_name=_("Title"))
    title_fr = models.CharField(max_length=500, blank=True, verbose_name=_("Title (French)"))
    title_mg = models.CharField(max_length=500, blank=True, verbose_name=_("Title (Malagasy)"))
    slug = models.SlugField(max_length=500, unique=True, verbose_name=_("Slug"))
    meta_description = models.TextField(blank=True, verbose_name=_("Meta Description"))
    meta_description_fr = models.TextField(blank=True, verbose_name=_("Meta Description (French)"))
    meta_description_mg = models.TextField(blank=True, verbose_name=_("Meta Description (Malagasy)"))
    content = models.TextField(blank=True, verbose_name=_("Content"))
    content_fr = models.TextField(blank=True, verbose_name=_("Content (French)"))
    content_mg = models.TextField(blank=True, verbose_name=_("Content (Malagasy)"))
    featured_image = models.ImageField(upload_to="cms/pages/", blank=True, null=True, verbose_name=_("Featured Image"))
    sections = models.ManyToManyField(PageSection, blank=True, related_name="pages", verbose_name=_("Sections"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name=_("Status"))
    is_homepage = models.BooleanField(default=False, verbose_name=_("Is Homepage"))
    template_name = models.CharField(
        max_length=200, blank=True, help_text=_("Custom template name (optional)"), verbose_name=_("Template Name")
    )
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Published At"))

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.is_homepage:
            return reverse("cms:home")
        return reverse("cms:page_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        # Ensure only one homepage
        if self.is_homepage:
            Page.objects.filter(is_homepage=True).exclude(pk=self.pk).update(is_homepage=False)
        super().save(*args, **kwargs)


class HeaderSettings(models.Model):
    """Header/Navigation settings"""

    # Basic Settings
    site_name = models.CharField(max_length=200, default="Tax Collector", verbose_name=_("Site Name"))
    site_name_fr = models.CharField(max_length=200, blank=True, verbose_name=_("Site Name (French)"))
    site_name_mg = models.CharField(max_length=200, blank=True, verbose_name=_("Site Name (Malagasy)"))
    logo = models.ImageField(upload_to="cms/headers/", blank=True, null=True, verbose_name=_("Logo"))
    logo_alt_text = models.CharField(max_length=200, blank=True, verbose_name=_("Logo Alt Text"))
    logo_height = models.IntegerField(default=40, help_text=_("Logo height in pixels"), verbose_name=_("Logo Height"))

    # Display Options
    show_search = models.BooleanField(default=False, verbose_name=_("Show Search"))
    show_language_switcher = models.BooleanField(default=True, verbose_name=_("Show Language Switcher"))
    is_sticky = models.BooleanField(default=True, verbose_name=_("Sticky Header"))

    # Colors
    background_color = models.CharField(
        max_length=7, default="#1a73e8", help_text=_("Header background color"), verbose_name=_("Background Color")
    )
    text_color = models.CharField(
        max_length=7, default="#ffffff", help_text=_("Text and brand color"), verbose_name=_("Text Color")
    )
    link_color = models.CharField(
        max_length=7, default="#ffffff", help_text=_("Menu link color"), verbose_name=_("Link Color")
    )
    link_hover_color = models.CharField(
        max_length=7, default="#e3f2fd", help_text=_("Menu link hover color"), verbose_name=_("Link Hover Color")
    )

    # Dropdown Menu Colors
    dropdown_background_color = models.CharField(
        max_length=7, default="#ffffff", help_text=_("Dropdown menu background"), verbose_name=_("Dropdown Background")
    )
    dropdown_text_color = models.CharField(
        max_length=7, default="#212529", help_text=_("Dropdown menu text color"), verbose_name=_("Dropdown Text Color")
    )
    dropdown_hover_color = models.CharField(
        max_length=7, default="#f8f9fa", help_text=_("Dropdown item hover background"), verbose_name=_("Dropdown Hover")
    )

    # Button Colors
    button_background_color = models.CharField(
        max_length=7, default="#ffffff", help_text=_("Button background color"), verbose_name=_("Button Background")
    )
    button_text_color = models.CharField(
        max_length=7, default="#1a73e8", help_text=_("Button text color"), verbose_name=_("Button Text")
    )
    button_hover_background = models.CharField(
        max_length=7,
        default="#e3f2fd",
        help_text=_("Button hover background"),
        verbose_name=_("Button Hover Background"),
    )

    # Spacing & Layout
    header_padding = models.IntegerField(default=15, help_text=_("Padding in pixels"), verbose_name=_("Header Padding"))

    # Shadow & Border
    shadow_enabled = models.BooleanField(default=True, verbose_name=_("Enable Shadow"))
    shadow_color = models.CharField(
        max_length=20, default="rgba(0,0,0,0.1)", help_text=_("CSS shadow value"), verbose_name=_("Shadow Color")
    )
    border_bottom_width = models.IntegerField(
        default=0, help_text=_("Border width in pixels (0 for none)"), verbose_name=_("Border Width")
    )
    border_bottom_color = models.CharField(max_length=7, default="#dee2e6", verbose_name=_("Border Color"))

    # Transparency
    background_opacity = models.FloatField(
        default=1.0, help_text=_("0.0 (transparent) to 1.0 (opaque)"), verbose_name=_("Background Opacity")
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Header Settings")
        verbose_name_plural = _("Header Settings")

    def __str__(self):
        return f"Header Settings - {self.site_name}"

    def save(self, *args, **kwargs):
        # Ensure only one active header settings
        if self.is_active:
            HeaderSettings.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class ThemeSettings(models.Model):
    """Theme settings for enhanced navbar design"""

    NAVBAR_STYLE_CHOICES = [
        ("enhanced", _("Enhanced (Modern with backdrop blur)")),
        ("classic", _("Classic (Standard Bootstrap)")),
        ("minimal", _("Minimal (Simple design)")),
    ]

    THEME_NAME_CHOICES = [
        ("default", _("Default (Blue)")),
        ("green_theme", _("Green Theme (Teal/Green)")),
        ("purple_theme", _("Purple Theme")),
        ("red_theme", _("Red Theme")),
        ("custom", _("Custom")),
    ]

    # Basic Settings
    theme_name = models.CharField(
        max_length=30,
        choices=THEME_NAME_CHOICES,
        default="default",
        verbose_name=_("Theme Name"),
        help_text=_("Choose a predefined theme or custom"),
    )

    navbar_style = models.CharField(
        max_length=20,
        choices=NAVBAR_STYLE_CHOICES,
        default="enhanced",
        verbose_name=_("Navbar Style"),
        help_text=_("Choose the navigation bar style"),
    )

    # Enhanced Navbar Settings
    use_enhanced_navbar = models.BooleanField(
        default=True,
        verbose_name=_("Use Enhanced Navbar"),
        help_text=_("Enable the enhanced navbar with modern styling and animations"),
    )

    navbar_background_opacity = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.95,
        help_text=_("Background opacity (0.0 to 1.0)"),
        verbose_name=_("Navbar Background Opacity"),
    )

    enable_backdrop_blur = models.BooleanField(
        default=True, verbose_name=_("Enable Backdrop Blur"), help_text=_("Enable blur effect on navbar background")
    )

    blur_amount = models.IntegerField(default=10, help_text=_("Blur amount in pixels"), verbose_name=_("Blur Amount"))

    # Scroll Effects
    enable_scroll_effect = models.BooleanField(
        default=True, verbose_name=_("Enable Scroll Effect"), help_text=_("Change navbar appearance on scroll")
    )

    scroll_threshold = models.IntegerField(
        default=50, help_text=_("Scroll threshold in pixels for effect activation"), verbose_name=_("Scroll Threshold")
    )

    # Animation Settings
    enable_animations = models.BooleanField(
        default=True, verbose_name=_("Enable Animations"), help_text=_("Enable smooth animations and transitions")
    )

    animation_duration = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.3,
        help_text=_("Animation duration in seconds"),
        verbose_name=_("Animation Duration"),
    )

    # Active Link Settings
    highlight_active_links = models.BooleanField(
        default=True,
        verbose_name=_("Highlight Active Links"),
        help_text=_("Automatically highlight the active navigation link"),
    )

    active_link_background = models.CharField(
        max_length=50,
        default="rgba(var(--bs-primary-rgb), 0.15)",
        help_text=_("Background color for active links (CSS color value)"),
        verbose_name=_("Active Link Background"),
    )

    # Mobile Menu Settings
    mobile_menu_style = models.CharField(
        max_length=20,
        choices=[
            ("slide", _("Slide Down")),
            ("fade", _("Fade In")),
            ("collapse", _("Collapse")),
        ],
        default="slide",
        verbose_name=_("Mobile Menu Style"),
    )

    # Brand Settings
    brand_hover_effect = models.BooleanField(
        default=True, verbose_name=_("Brand Hover Effect"), help_text=_("Enable scale effect on brand hover")
    )

    # Link Hover Effects
    link_hover_lift = models.BooleanField(
        default=True, verbose_name=_("Link Hover Lift"), help_text=_("Enable lift effect on link hover")
    )

    link_hover_scale = models.BooleanField(
        default=False, verbose_name=_("Link Hover Scale"), help_text=_("Enable scale effect on link hover")
    )

    # Theme Colors (for custom themes)
    primary_color = models.CharField(
        max_length=7, default="#1a73e8", help_text=_("Primary theme color (hex code)"), verbose_name=_("Primary Color")
    )

    accent_color = models.CharField(
        max_length=7,
        default="#20C997",
        help_text=_("Accent color for buttons and highlights (hex code)"),
        verbose_name=_("Accent Color"),
    )

    navbar_text_color = models.CharField(
        max_length=7,
        default="#343A40",
        help_text=_("Navbar text color (hex code)"),
        verbose_name=_("Navbar Text Color"),
    )

    navbar_link_color = models.CharField(
        max_length=7,
        default="#6C757D",
        help_text=_("Navbar link color (hex code)"),
        verbose_name=_("Navbar Link Color"),
    )

    navbar_link_hover_color = models.CharField(
        max_length=7,
        default="#20C997",
        help_text=_("Navbar link hover color (hex code)"),
        verbose_name=_("Navbar Link Hover Color"),
    )

    button_background_color = models.CharField(
        max_length=7,
        default="#20C997",
        help_text=_("Button background color (hex code)"),
        verbose_name=_("Button Background Color"),
    )

    button_text_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        help_text=_("Button text color (hex code)"),
        verbose_name=_("Button Text Color"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Theme Settings")
        verbose_name_plural = _("Theme Settings")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Theme Settings - {self.get_theme_name_display()}"

    def save(self, *args, **kwargs):
        # Ensure only one active theme settings
        if self.is_active:
            ThemeSettings.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)

        # Apply theme colors based on theme_name if not custom
        if self.theme_name == "green_theme":
            self.primary_color = "#20C997"
            self.accent_color = "#20C997"
            self.navbar_text_color = "#343A40"
            self.navbar_link_color = "#6C757D"
            self.navbar_link_hover_color = "#20C997"
            self.button_background_color = "#20C997"
            self.button_text_color = "#FFFFFF"
        elif self.theme_name == "default":
            self.primary_color = "#1a73e8"
            self.accent_color = "#0d47a1"
            self.navbar_text_color = "#FFFFFF"
            self.navbar_link_color = "#FFFFFF"
            self.navbar_link_hover_color = "#e3f2fd"
            self.button_background_color = "#1a73e8"
            self.button_text_color = "#FFFFFF"
        # Add more theme presets as needed

        super().save(*args, **kwargs)


class FooterSettings(models.Model):
    """Footer settings"""

    BACKGROUND_SIZE_CHOICES = [
        ("cover", _("Cover (fill entire area)")),
        ("contain", _("Contain (fit within area)")),
        ("auto", _("Auto (original size)")),
        ("100% 100%", _("Stretch (100% width and height)")),
    ]

    BACKGROUND_REPEAT_CHOICES = [
        ("no-repeat", _("No Repeat")),
        ("repeat", _("Repeat")),
        ("repeat-x", _("Repeat Horizontally")),
        ("repeat-y", _("Repeat Vertically")),
    ]

    BACKGROUND_POSITION_CHOICES = [
        ("center center", _("Center")),
        ("top center", _("Top Center")),
        ("bottom center", _("Bottom Center")),
        ("left center", _("Left Center")),
        ("right center", _("Right Center")),
        ("top left", _("Top Left")),
        ("top right", _("Top Right")),
        ("bottom left", _("Bottom Left")),
        ("bottom right", _("Bottom Right")),
    ]

    # Content
    copyright_text = models.CharField(
        max_length=500, default="© Tax Collector. Tous droits réservés.", verbose_name=_("Copyright Text")
    )
    copyright_text_fr = models.CharField(max_length=500, blank=True, verbose_name=_("Copyright Text (French)"))
    copyright_text_mg = models.CharField(max_length=500, blank=True, verbose_name=_("Copyright Text (Malagasy)"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    description_fr = models.TextField(blank=True, verbose_name=_("Description (French)"))
    description_mg = models.TextField(blank=True, verbose_name=_("Description (Malagasy)"))

    # Display Options
    show_social_links = models.BooleanField(default=True, verbose_name=_("Show Social Links"))
    show_newsletter = models.BooleanField(default=False, verbose_name=_("Show Newsletter Signup"))

    # Background Image
    background_image = models.ImageField(
        upload_to="cms/footer_backgrounds/", blank=True, null=True, verbose_name=_("Background Image")
    )
    background_size = models.CharField(
        max_length=20, choices=BACKGROUND_SIZE_CHOICES, default="cover", verbose_name=_("Background Size")
    )
    background_repeat = models.CharField(
        max_length=20, choices=BACKGROUND_REPEAT_CHOICES, default="no-repeat", verbose_name=_("Background Repeat")
    )
    background_position = models.CharField(
        max_length=30,
        choices=BACKGROUND_POSITION_CHOICES,
        default="center center",
        verbose_name=_("Background Position"),
    )
    background_attachment = models.CharField(
        max_length=10,
        choices=[("scroll", _("Scroll")), ("fixed", _("Fixed"))],
        default="scroll",
        verbose_name=_("Background Attachment"),
    )

    # Colors & Transparency
    background_color = models.CharField(
        max_length=7, default="#212529", help_text=_("Footer background color"), verbose_name=_("Background Color")
    )
    background_opacity = models.FloatField(
        default=1.0, help_text=_("0.0 (transparent) to 1.0 (opaque)"), verbose_name=_("Background Opacity")
    )
    background_overlay_color = models.CharField(
        max_length=20,
        default="rgba(0,0,0,0.5)",
        help_text=_("Overlay color over background image (e.g., rgba(0,0,0,0.5))"),
        verbose_name=_("Overlay Color"),
    )
    enable_overlay = models.BooleanField(default=False, verbose_name=_("Enable Overlay"))

    text_color = models.CharField(
        max_length=7, default="#ffffff", help_text=_("Footer text color"), verbose_name=_("Text Color")
    )
    link_color = models.CharField(
        max_length=7, default="#adb5bd", help_text=_("Footer link color"), verbose_name=_("Link Color")
    )
    link_hover_color = models.CharField(
        max_length=7, default="#ffffff", help_text=_("Footer link hover color"), verbose_name=_("Link Hover Color")
    )
    heading_color = models.CharField(
        max_length=7, default="#ffffff", help_text=_("Footer heading color"), verbose_name=_("Heading Color")
    )

    # Spacing
    padding_top = models.IntegerField(default=60, help_text=_("Top padding in pixels"), verbose_name=_("Padding Top"))
    padding_bottom = models.IntegerField(
        default=60, help_text=_("Bottom padding in pixels"), verbose_name=_("Padding Bottom")
    )

    # Border
    border_top_width = models.IntegerField(
        default=0, help_text=_("Border width in pixels (0 for none)"), verbose_name=_("Border Top Width")
    )
    border_top_color = models.CharField(max_length=7, default="#dee2e6", verbose_name=_("Border Top Color"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Footer Settings")
        verbose_name_plural = _("Footer Settings")

    def __str__(self):
        return "Footer Settings"

    def save(self, *args, **kwargs):
        # Ensure only one active footer settings
        if self.is_active:
            FooterSettings.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
