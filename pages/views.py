from django.http import HttpResponse
from django.shortcuts import render


# Authentication Views
def signin_basic(request):
    return render(request, "velzon/pages/authentication/auth-signin-basic.html")


def signin_cover(request):
    return render(request, "velzon/pages/authentication/auth-signin-cover.html")


def signup_basic(request):
    return render(request, "velzon/pages/authentication/auth-signup-basic.html")


def signup_cover(request):
    return render(request, "velzon/pages/authentication/auth-signup-cover.html")


def pass_reset_basic(request):
    return render(request, "velzon/pages/authentication/auth-pass-reset-basic.html")


def pass_reset_cover(request):
    return render(request, "velzon/pages/authentication/auth-pass-reset-cover.html")


def pass_change_basic(request):
    return render(request, "velzon/pages/authentication/auth-pass-change-basic.html")


def pass_change_cover(request):
    return render(request, "velzon/pages/authentication/auth-pass-change-cover.html")


def lockscreen_basic(request):
    return render(request, "velzon/pages/authentication/auth-lockscreen-basic.html")


def lockscreen_cover(request):
    return render(request, "velzon/pages/authentication/auth-lockscreen-cover.html")


def logout_basic(request):
    return render(request, "velzon/pages/authentication/auth-logout-basic.html")


def logout_cover(request):
    return render(request, "velzon/pages/authentication/auth-logout-cover.html")


def success_msg_basic(request):
    return render(request, "velzon/pages/authentication/auth-success-msg-basic.html")


def success_msg_cover(request):
    return render(request, "velzon/pages/authentication/auth-success-msg-cover.html")


def twostep_basic(request):
    return render(request, "velzon/pages/authentication/auth-twostep-basic.html")


def twostep_cover(request):
    return render(request, "velzon/pages/authentication/auth-twostep-cover.html")


def error_404_basic(request):
    return render(request, "velzon/pages/authentication/auth-404-basic.html")


def error_404_cover(request):
    return render(request, "velzon/pages/authentication/auth-404-cover.html")


def error_404_alt(request):
    return render(request, "velzon/pages/authentication/auth-404-alt.html")


def error_500(request):
    return render(request, "velzon/pages/authentication/auth-500.html")


def offline(request):
    return render(request, "velzon/pages/authentication/auth-offline.html")


# Pages Views
def starter(request):
    return render(request, "velzon/pages/pages-starter.html")


def profile(request):
    return render(request, "velzon/pages/pages-profile.html")


def profile_settings(request):
    return render(request, "velzon/pages/pages-profile-settings.html")


def team(request):
    return render(request, "velzon/pages/pages-team.html")


def timeline(request):
    return render(request, "velzon/pages/pages-timeline.html")


def faqs(request):
    return render(request, "velzon/pages/pages-faqs.html")


def pricing(request):
    return render(request, "velzon/pages/pages-pricing.html")


def gallery(request):
    return render(request, "velzon/pages/pages-gallery.html")


def maintenance(request):
    return render(request, "velzon/pages/pages-maintenance.html")


def coming_soon(request):
    return render(request, "velzon/pages/pages-coming-soon.html")


def sitemap(request):
    return render(request, "velzon/pages/pages-sitemap.html")


def search_results(request):
    return render(request, "velzon/pages/pages-search-results.html")


def privacy_policy(request):
    return render(request, "velzon/pages/pages-privacy-policy.html")


def terms_conditions(request):
    return render(request, "velzon/pages/pages-term-conditions.html")


def blog_list(request):
    return render(request, "velzon/pages/pages-blog-list.html")


def blog_grid(request):
    return render(request, "velzon/pages/pages-blog-grid.html")


def blog_overview(request):
    return render(request, "velzon/pages/pages-blog-overview.html")


def landing(request):
    return render(request, "velzon/pages/pages-landing.html")


def nft_landing(request):
    return render(request, "velzon/pages/pages-nft-landing.html")


def job_landing(request):
    return render(request, "velzon/pages/pages-job-landing.html")
