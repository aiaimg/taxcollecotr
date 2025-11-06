from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Authentication URLs
    path('authentication/signin-basic/', views.signin_basic, name='authentication.signin_basic'),
    path('authentication/signin-cover/', views.signin_cover, name='authentication.signin_cover'),
    path('authentication/signup-basic/', views.signup_basic, name='authentication.signup_basic'),
    path('authentication/signup-cover/', views.signup_cover, name='authentication.signup_cover'),
    path('authentication/pass-reset-basic/', views.pass_reset_basic, name='authentication.pass_reset_basic'),
    path('authentication/pass-reset-cover/', views.pass_reset_cover, name='authentication.pass_reset_cover'),
    path('authentication/pass-change-basic/', views.pass_change_basic, name='authentication.pass_change_basic'),
    path('authentication/pass-change-cover/', views.pass_change_cover, name='authentication.pass_change_cover'),
    path('authentication/lockscreen-basic/', views.lockscreen_basic, name='authentication.lockscreen_basic'),
    path('authentication/lockscreen-cover/', views.lockscreen_cover, name='authentication.lockscreen_cover'),
    path('authentication/logout-basic/', views.logout_basic, name='authentication.logout_basic'),
    path('authentication/logout-cover/', views.logout_cover, name='authentication.logout_cover'),
    path('authentication/success-msg-basic/', views.success_msg_basic, name='authentication.success_msg_basic'),
    path('authentication/success-msg-cover/', views.success_msg_cover, name='authentication.success_msg_cover'),
    path('authentication/twostep-basic/', views.twostep_basic, name='authentication.twostep_basic'),
    path('authentication/twostep-cover/', views.twostep_cover, name='authentication.twostep_cover'),
    path('authentication/404-basic/', views.error_404_basic, name='authentication.404_basic'),
    path('authentication/404-cover/', views.error_404_cover, name='authentication.404_cover'),
    path('authentication/404-alt/', views.error_404_alt, name='authentication.404_alt'),
    path('authentication/500/', views.error_500, name='authentication.500'),
    path('authentication/offline/', views.offline, name='authentication.offline'),
    
    # Pages URLs
    path('starter/', views.starter, name='pages.starter'),
    path('profile/', views.profile, name='pages.profile'),
    path('profile-settings/', views.profile_settings, name='pages.profile_settings'),
    path('team/', views.team, name='pages.team'),
    path('timeline/', views.timeline, name='pages.timeline'),
    path('faqs/', views.faqs, name='pages.faqs'),
    path('pricing/', views.pricing, name='pages.pricing'),
    path('gallery/', views.gallery, name='pages.gallery'),
    path('maintenance/', views.maintenance, name='pages.maintenance'),
    path('coming-soon/', views.coming_soon, name='pages.coming_soon'),
    path('sitemap/', views.sitemap, name='pages.sitemap'),
    path('search-results/', views.search_results, name='pages.search_results'),
    path('privacy-policy/', views.privacy_policy, name='pages.privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='pages.terms_conditions'),
    path('blog-list/', views.blog_list, name='pages.blog_list'),
    path('blog-grid/', views.blog_grid, name='pages.blog_grid'),
    path('blog-overview/', views.blog_overview, name='pages.blog_overview'),
    path('landing/', views.landing, name='pages.landing'),
    path('nft-landing/', views.nft_landing, name='pages.nft_landing'),
    path('job-landing/', views.job_landing, name='pages.job_landing'),
]