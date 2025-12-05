# Google OAuth Setup Guide

## Overview
- Integrates Google OAuth2 using Django Allauth.
- Requires a Google Cloud project with OAuth 2.0 Client ID (Web application).

## Prerequisites
- Google account with access to [Google Cloud Console](https://console.cloud.google.com/).
- Django environment configured with Allauth.

## Steps
1. Create a Google Cloud project
   - Go to Google Cloud Console → Select or create a project.

2. Enable APIs
   - Enable “Google Identity Services” / “OAuth consent screen”.

3. Configure OAuth Consent Screen
   - User type: External (for general users) or Internal.
   - App information: Name, support email.
   - Scopes: Add basic profile scopes: `profile`, `email`.
   - Test users: Add test emails if app is not published.

4. Create OAuth Client ID (Credentials → Create Credentials → OAuth client ID)
   - Application type: Web application.
   - Authorized JavaScript origins:
     - `http://localhost:8000`
   - Authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/`
   - Save and note `Client ID` and `Client Secret`.

5. Configure environment variables
   - In `.env` set:
     - `GOOGLE_OAUTH_CLIENT_ID=your-client-id`
     - `GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret`

6. Django settings
   - Ensure the following in `INSTALLED_APPS`:
     - `allauth`, `allauth.account`, `allauth.socialaccount`, `allauth.socialaccount.providers.google`
   - Provider config:
     - `SOCIALACCOUNT_PROVIDERS['google'] = { 'SCOPE': ['profile','email'], 'AUTH_PARAMS': {'access_type':'offline'}, 'OAUTH_PKCE': True }`

7. Database init (first-time)
   - Migrate and create SocialApp entry (automated by data migration). Verify in admin or via shell.

8. Callback URLs and One Tap (optional)
   - Token login endpoint (One Tap): `POST /accounts/google/login/token/` with CSRF cookie `g_csrf_token`.

## Verification
- Login page shows “Continue with Google” when credentials are set.
- Linking/unlinking available under “Comptes sociaux”.
- Tests cover CSRF validation, login, linking, unlinking, and token refresh.

## Troubleshooting
- Ensure `SITE_ID=1` and a `Site` exists with domain matching your environment.
- If provider URLs not found, include `allauth.urls` under `/accounts/`.
- For offline access/refresh tokens, ensure `AUTH_PARAMS={'access_type':'offline'}`.

