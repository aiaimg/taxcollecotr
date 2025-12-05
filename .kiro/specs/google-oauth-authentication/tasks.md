# Implementation Plan

## 1. Configure Google OAuth Provider in Django Settings

- [x] 1.1 Add Google provider to INSTALLED_APPS
  - Add `'allauth.socialaccount.providers.google'` to INSTALLED_APPS in settings.py
  - _Requirements: 5.1_
  - **Status**: Already implemented in taxcollector_project/settings.py

- [x] 1.2 Configure SOCIALACCOUNT_PROVIDERS settings
  - Add Google OAuth configuration with scopes ['profile', 'email']
  - Enable OAUTH_PKCE for enhanced security
  - Configure AUTH_PARAMS for access_type
  - _Requirements: 5.1, 8.3_
  - **Status**: Already implemented in taxcollector_project/settings.py

- [x] 1.3 Add environment variables for Google OAuth credentials
  - Add GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET to settings
  - Update .env.example with placeholder values
  - _Requirements: 5.1, 5.2_
  - **Status**: Already implemented in settings.py and .env.example

- [x] 1.4 Create database migration for SocialApp
  - Create data migration to add Google SocialApp entry
  - Link SocialApp to Site (SITE_ID=1)
  - _Requirements: 5.1_
  - **Status**: Already implemented in core/migrations/0005_add_google_socialapp.py

## 2. Implement Custom Google OAuth Adapter

- [x] 2.1 Create CustomGoogleOAuth2Adapter class
  - Extend GoogleOAuth2Adapter from allauth
  - Override complete_login to mark email as verified
  - Handle profile data extraction from Google response
  - _Requirements: 1.2, 1.3_
  - **Status**: Already implemented in core/social_adapters.py

- [ ]* 2.2 Write property test for Google OAuth registration
  - **Property 1: Google OAuth Registration Creates Verified User**
  - **Validates: Requirements 1.2, 1.3**

- [x] 2.3 Create CustomSocialAccountAdapter class
  - Extend DefaultSocialAccountAdapter
  - Implement pre_social_login for email conflict detection
  - Implement authentication_error for error handling
  - _Requirements: 1.4, 1.5, 2.4_
  - **Status**: Already implemented in core/social_adapters.py

- [ ]* 2.4 Write property test for email uniqueness
  - **Property 2: Email Uniqueness on OAuth Registration**
  - **Validates: Requirements 1.4**

## 3. Implement Signal Handlers for Social Account Events

- [x] 3.1 Create signal handler for social_account_added
  - Create UserProfile if not exists for new OAuth users
  - Set default user_type based on registration context
  - Mark email as verified for Google accounts
  - _Requirements: 1.2, 1.3, 3.3_
  - **Status**: Already implemented in core/social_signals.py

- [ ]* 3.2 Write property test for account linking
  - **Property 5: Account Linking Creates SocialAccount**
  - **Validates: Requirements 3.3**

- [x] 3.3 Create signal handler for social_account_removed
  - Verify user has usable password before allowing removal
  - Log account unlinking for audit trail
  - _Requirements: 4.2, 4.3_
  - **Status**: Already implemented in core/social_signals.py with pre_delete guard

- [ ]* 3.4 Write property test for unlink requirements
  - **Property 7: Unlink Requires Password**
  - **Validates: Requirements 4.2**

- [ ]* 3.5 Write property test for unlink action
  - **Property 8: Unlink Removes SocialAccount**
  - **Validates: Requirements 4.3**

## 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## 5. Update Login and Registration Templates with Google Buttons

- [x] 5.1 Add Google Sign-In button to login.html
  - Add button with official Google branding/icon
  - Use {% provider_login_url 'google' %} for URL
  - Add proper ARIA labels for accessibility
  - Position button prominently with "ou" separator
  - _Requirements: 6.1, 6.4_
  - **Status**: Already implemented in templates/account/login.html

- [x] 5.2 Add conditional display based on credentials availability
  - Check if Google OAuth is configured before showing button
  - Hide button if credentials are missing
  - _Requirements: 5.3_
  - **Status**: Already implemented with GOOGLE_OAUTH_CONFIGURED context variable

- [ ]* 5.3 Write property test for missing credentials
  - **Property 9: Missing Credentials Disables Google Auth**
  - **Validates: Requirements 5.3**

- [x] 5.4 Add Google Sign-Up button to signup.html
  - Add button with official Google branding/icon
  - Position button prominently with separator ("ou")
  - Add proper ARIA labels for accessibility
  - _Requirements: 6.2, 6.4_
  - **Status**: Already implemented in templates/account/signup.html

- [x] 5.5 Add translations for Google button text
  - Add French translation: "Se connecter avec Google" / "Continuer avec Google"
  - Add Malagasy translation: "Miditra amin'ny Google"
  - _Requirements: 6.3_
  - **Status**: Translations already exist in locale/fr and locale/mg

## 6. Implement Social Account Management Views

- [x] 6.1 Create SocialAccountManageView
  - Create view to list user's linked social accounts
  - Add context for can_disconnect (has usable password)
  - Handle GET request to display accounts
  - _Requirements: 7.1, 7.2, 7.3_
  - **Status**: Already implemented in core/views.py

- [x] 6.2 Create social_accounts.html template
  - Display list of linked social accounts with provider info
  - Show Google email for linked Google accounts
  - Add link/unlink buttons based on state
  - _Requirements: 7.1, 7.2, 7.3_
  - **Status**: Already implemented in templates/core/social_accounts.html

- [x] 6.3 Add URL routes for social account management
  - Add path to core/urls.py
  - Link from profile page
  - _Requirements: 7.1_
  - **Status**: Already implemented in core/urls.py

- [ ]* 6.4 Write property test for linked account display
  - **Property: Linked Google account displays email**
  - **Validates: Requirements 7.2**

## 7. Implement Account Unlinking Flow

- [x] 7.1 Create account unlinking view
  - Verify user has usable password before allowing unlink
  - Require confirmation before unlinking
  - Remove SocialAccount on confirmation
  - _Requirements: 4.1, 4.2, 4.3_
  - **Status**: Already implemented in core/views.py (SocialAccountUnlinkView)

- [x] 7.2 Create unlink confirmation template
  - Show confirmation page before unlinking
  - Display warning if no password set
  - _Requirements: 4.2, 4.4_
  - **Status**: Already implemented in templates/core/social_account_unlink_confirm.html

- [x] 7.3 Add success/error messages for unlink
  - Display confirmation message on successful unlink
  - Display error message if unlink fails
  - _Requirements: 4.4_
  - **Status**: Already implemented in SocialAccountUnlinkView

## 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## 9. Add Localization Support

- [x] 9.1 Update French translations (django.po)
  - Add translations for all Google OAuth related strings
  - Include error messages and button labels
  - _Requirements: 6.3_
  - **Status**: Translations already exist in locale/fr/LC_MESSAGES/django.po

- [x] 9.2 Update Malagasy translations (django.po)
  - Add translations for all Google OAuth related strings
  - Include error messages and button labels
  - _Requirements: 6.3_
  - **Status**: Translations already exist in locale/mg/LC_MESSAGES/django.po

- [x] 9.3 Compile message files
  - Run compilemessages to generate .mo files
  - Verify translations work correctly
  - _Requirements: 6.3_
  - **Status**: Compiled successfully

## 10. Update Profile Page

- [x] 10.1 Add social accounts section to profile template
  - Display linked social accounts in profile view
  - Add link to social account management page
  - Show Google email if linked
  - _Requirements: 7.1, 7.2_
  - **Status**: Added to templates/core/profile.html

- [x] 10.2 Add helper methods to UserProfile model
  - Add has_google_account() method
  - Add get_google_email() method
  - _Requirements: 7.2_
  - **Status**: Added to core/models.py

## 11. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## 12. Documentation

- [x] 12.1 Update .env.example with Google OAuth variables
  - Add GOOGLE_OAUTH_CLIENT_ID placeholder
  - Add GOOGLE_OAUTH_CLIENT_SECRET placeholder
  - Add setup instructions as comments
  - _Requirements: 5.1, 5.2_
  - **Status**: Already implemented in .env.example

- [x] 12.2 Create Google OAuth setup guide
  - Document how to create Google Cloud project
  - Document how to configure OAuth consent screen
  - Document how to obtain client credentials
  - Document callback URL configuration
  - _Requirements: 5.1, 5.2_
  - **Status**: Already implemented in docs/google_oauth_setup.md

- [ ]* 12.3 Write integration tests for complete OAuth flow
  - Test registration flow end-to-end
  - Test login flow end-to-end
  - Test linking/unlinking flow end-to-end
  - _Requirements: All_
