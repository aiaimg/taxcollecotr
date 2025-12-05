from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    FooterSettings,
    HeaderSettings,
    MenuItem,
    Page,
    PageSection,
    SectionItem,
    SiteSettings,
    ThemeSettings,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_name", "contact_email", "is_active", "updated_at"]
    list_filter = ["is_active", "created_at"]
    fieldsets = (
        (_("Basic Information"), {"fields": ("site_name", "site_tagline", "site_logo", "site_favicon", "is_active")}),
        (_("Contact Information"), {"fields": ("contact_email", "contact_phone", "contact_address")}),
        (
            _("Social Media"),
            {"fields": ("facebook_url", "twitter_url", "linkedin_url", "instagram_url", "youtube_url")},
        ),
        (_("Timestamps"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ["created_at", "updated_at"]


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    fk_name = "parent"
    extra = 0
    fields = ["title", "url", "icon", "order", "is_active"]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["title", "url", "menu_location", "parent", "order", "is_active"]
    list_filter = ["menu_location", "is_active", "parent"]
    search_fields = ["title", "url"]
    fieldsets = (
        (_("Basic Information"), {"fields": ("title", "title_fr", "title_mg", "url", "icon", "parent")}),
        (_("Display Settings"), {"fields": ("menu_location", "order", "is_active", "open_in_new_tab")}),
    )
    inlines = [MenuItemInline]


class SectionItemInline(admin.TabularInline):
    model = SectionItem
    extra = 1
    fields = ["title", "title_fr", "title_mg", "description", "icon", "image", "order", "is_active"]


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ["name", "section_type", "order", "is_active", "updated_at"]
    list_filter = ["section_type", "is_active", "created_at"]
    search_fields = ["name", "title"]
    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "name",
                    "section_type",
                    "title",
                    "title_fr",
                    "title_mg",
                    "subtitle",
                    "subtitle_fr",
                    "subtitle_mg",
                    "content",
                    "content_fr",
                    "content_mg",
                )
            },
        ),
        (_("Visual Settings"), {"fields": ("background_image", "background_color", "text_color")}),
        (_("Display Settings"), {"fields": ("order", "is_active")}),
    )
    inlines = [SectionItemInline]


@admin.register(SectionItem)
class SectionItemAdmin(admin.ModelAdmin):
    list_display = ["title", "section", "order", "is_active"]
    list_filter = ["section", "is_active", "created_at"]
    search_fields = ["title", "description"]
    fieldsets = (
        (
            _("Content"),
            {"fields": ("section", "title", "title_fr", "title_mg", "description", "description_fr", "description_mg")},
        ),
        (_("Media"), {"fields": ("icon", "image")}),
        (_("Link"), {"fields": ("link_url", "link_text")}),
        (_("Display Settings"), {"fields": ("order", "is_active")}),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "status", "is_homepage", "order", "updated_at"]
    list_filter = ["status", "is_homepage", "created_at", "updated_at"]
    search_fields = ["title", "slug", "content"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["sections"]
    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "title",
                    "title_fr",
                    "title_mg",
                    "slug",
                    "meta_description",
                    "meta_description_fr",
                    "meta_description_mg",
                    "featured_image",
                )
            },
        ),
        (_("Content"), {"fields": ("content", "content_fr", "content_mg")}),
        (_("Sections"), {"fields": ("sections",)}),
        (_("Settings"), {"fields": ("status", "is_homepage", "template_name", "order", "published_at")}),
    )
    readonly_fields = ["created_at", "updated_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("sections")


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_name", "is_sticky", "is_active", "updated_at"]
    list_filter = ["is_active", "is_sticky", "created_at"]
    fieldsets = (
        (_("Basic Information"), {"fields": ("site_name", "site_name_fr", "site_name_mg", "logo", "logo_alt_text")}),
        (_("Display Options"), {"fields": ("show_search", "show_language_switcher", "is_sticky")}),
        (_("Styling"), {"fields": ("background_color", "text_color")}),
        (_("Status"), {"fields": ("is_active",)}),
    )
    readonly_fields = ["created_at", "updated_at"]


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    list_display = ["copyright_text", "show_social_links", "is_active", "updated_at"]
    list_filter = ["is_active", "show_social_links", "created_at"]
    fieldsets = (
        (
            _("Content"),
            {
                "fields": (
                    "copyright_text",
                    "copyright_text_fr",
                    "copyright_text_mg",
                    "description",
                    "description_fr",
                    "description_mg",
                )
            },
        ),
        (_("Display Options"), {"fields": ("show_social_links", "show_newsletter")}),
        (_("Styling"), {"fields": ("background_color", "text_color")}),
        (_("Status"), {"fields": ("is_active",)}),
    )
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ThemeSettings)
class ThemeSettingsAdmin(admin.ModelAdmin):
    list_display = ["theme_name", "navbar_style", "use_enhanced_navbar", "is_active", "updated_at"]
    list_filter = ["theme_name", "navbar_style", "use_enhanced_navbar", "is_active", "created_at"]
    fieldsets = (
        (
            _("Theme Selection"),
            {
                "fields": ("theme_name", "navbar_style", "use_enhanced_navbar", "is_active"),
                "description": _("Choose a predefined theme or customize colors below"),
            },
        ),
        (
            _("Theme Colors"),
            {
                "fields": (
                    "primary_color",
                    "accent_color",
                    "navbar_text_color",
                    "navbar_link_color",
                    "navbar_link_hover_color",
                    "button_background_color",
                    "button_text_color",
                ),
                "description": _(
                    'Theme colors are automatically set based on theme name. You can customize them if theme_name is set to "Custom".'
                ),
            },
        ),
        (
            _("Enhanced Navbar Settings"),
            {"fields": ("navbar_background_opacity", "enable_backdrop_blur", "blur_amount")},
        ),
        (_("Scroll Effects"), {"fields": ("enable_scroll_effect", "scroll_threshold")}),
        (_("Animation Settings"), {"fields": ("enable_animations", "animation_duration")}),
        (_("Active Link Settings"), {"fields": ("highlight_active_links", "active_link_background")}),
        (_("Mobile Menu Settings"), {"fields": ("mobile_menu_style",)}),
        (_("Brand Settings"), {"fields": ("brand_hover_effect",)}),
        (_("Link Hover Effects"), {"fields": ("link_hover_lift", "link_hover_scale")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ["created_at", "updated_at"]
