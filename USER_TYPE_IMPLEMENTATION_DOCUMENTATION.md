# User Type Implementation Documentation

**Version:** 1.0  
**Date:** December 2024  
**Project:** Digital Vehicle Tax Platform - Madagascar

## Table of Contents

1. [Overview](#overview)
2. [User Types Supported](#user-types-supported)
3. [Database Schema](#database-schema)
4. [Registration Flow](#registration-flow)
5. [Permissions and Access Control](#permissions-and-access-control)
6. [API Endpoints](#api-endpoints)
7. [Validation Rules and Business Logic](#validation-rules-and-business-logic)
8. [Implementation Type: Static vs Dynamic](#implementation-type-static-vs-dynamic)

---

## Overview

The system implements a multi-tier user type system with the following categories:

1. **Regular User Types** (selected during registration):
   - Individual user
   - Company user
   - Emergency Service Provider
   - Government Administrator
   - Law Enforcement Officer

2. **Agent Types** (created separately, not via registration):
   - Partner Agent (Agent Partenaire)
   - Government Agent (Agent Gouvernement)

3. **Staff Roles** (Django built-in):
   - Administrator (is_superuser)
   - Staff member (is_staff)

---

## User Types Supported

### 1. Individual User (`individual`)
- **Display Name:** "Particulier (Citoyen)" / "Individual Citizen"
- **Registration:** Available during signup
- **Purpose:** Regular citizens registering personal vehicles

### 2. Company User (`company`)
- **Display Name:** "Entreprise/Société" / "Company/Business"
- **Registration:** Available during signup
- **Purpose:** Businesses managing fleet vehicles

### 3. Emergency Service Provider (`emergency`)
- **Display Name:** "Service d'urgence" / "Emergency Service Provider"
- **Registration:** Available during signup
- **Purpose:** Emergency services (ambulance, fire, rescue)

### 4. Government Administrator (`government`)
- **Display Name:** "Administration publique" / "Government Administrator"
- **Registration:** Available during signup
- **Purpose:** Government administrators with system-wide access

### 5. Law Enforcement Officer (`law_enforcement`)
- **Display Name:** "Forces de l'ordre" / "Law Enforcement Officer"
- **Registration:** Available during signup
- **Purpose:** Law enforcement officers for verification

### 6. Partner Agent (Agent Partenaire)
- **Model:** `AgentPartenaireProfile` (in `payments/models.py`)
- **Registration:** NOT available during signup - created separately by administrators
- **Purpose:** Agents authorized to collect cash payments
- **Access:** Cash collection dashboard, payment processing

### 7. Government Agent (Agent Gouvernement)
- **Model:** `AgentVerification` (in `administration/models.py`)
- **Registration:** NOT available during signup - created separately by administrators
- **Purpose:** Government agents for QR code verification
- **Access:** QR verification dashboard, verification tools

### 8. Administrator
- **Type:** Django `is_superuser` flag
- **Registration:** NOT available during signup - created via Django admin or management commands
- **Purpose:** Full system administration

### 9. Staff Member
- **Type:** Django `is_staff` flag
- **Registration:** NOT available during signup - set via Django admin
- **Purpose:** Limited administrative access

---

## Database Schema

### Core User Profile Model

**File:** `core/models.py`

```python
class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('individual', 'Individual Citizen'),
        ('company', 'Company/Business'),
        ('emergency', 'Emergency Service Provider'),
        ('government', 'Government Administrator'),
        ('law_enforcement', 'Law Enforcement Officer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='individual')
    telephone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    langue_preferee = models.CharField(max_length=5, choices=[('fr', 'Français'), ('mg', 'Malagasy')], default='fr')
    est_entreprise = models.BooleanField(default=False)  # Legacy field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Points:**
- User type is stored as a CharField with predefined choices
- One-to-one relationship with Django User model
- Default user type is 'individual'
- Includes verification status tracking
- Legacy `est_entreprise` field maintained for backward compatibility

### Extended Profile Models

Each user type (except individual) has an optional extended profile model:

1. **IndividualProfile** (`core/models.py`)
   - Fields: `identity_number`, `date_of_birth`, `address`, `emergency_contact`
   - Relationship: OneToOne with `UserProfile`

2. **CompanyProfile** (`core/models.py`)
   - Fields: `company_name`, `tax_id` (unique), `business_registration_number`, `industry_sector`, `fleet_size`, `address`
   - Relationship: OneToOne with `UserProfile`

3. **EmergencyServiceProfile** (`core/models.py`)
   - Fields: `organization_name`, `service_type`, `official_license`, `department_contact`, `verification_document_url`
   - Relationship: OneToOne with `UserProfile`

4. **GovernmentAdminProfile** (`core/models.py`)
   - Fields: `department`, `position`, `employee_id`, `access_level` (1-5)
   - Relationship: OneToOne with `UserProfile`

5. **LawEnforcementProfile** (`core/models.py`)
   - Fields: `badge_number` (unique), `department`, `rank`, `jurisdiction`
   - Relationship: OneToOne with `UserProfile`

### Agent Models (Separate from User Types)

1. **AgentPartenaireProfile** (`payments/models.py`)
   - Fields: `agent_id` (unique), `full_name`, `phone_number`, `collection_location`, `commission_rate`, `is_active`
   - Relationship: OneToOne with `User` (NOT UserProfile)
   - Access: `user.agent_partenaire_profile`

2. **AgentVerification** (`administration/models.py`)
   - Fields: `numero_badge` (unique), `zone_affectation`, `est_actif`
   - Relationship: OneToOne with `User` (NOT UserProfile)
   - Access: `user.agent_verification`

### Staff Roles

- **Administrator:** Uses Django's `User.is_superuser` flag
- **Staff Member:** Uses Django's `User.is_staff` flag
- **AdminUserProfile** (`administration/models.py`): Extended profile for admins with 2FA, IP whitelisting, security features

### Database Indexes

The system includes indexes on:
- `user_type` field in `UserProfile`
- `telephone` field in `UserProfile`
- `verification_status` field in `UserProfile`
- `tax_id` field in `CompanyProfile`
- `badge_number` fields in agent models

---

## Registration Flow

### Registration Form

**File:** `core/forms.py`

```python
class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('individual', 'Particulier (Citoyen)'),
        ('company', 'Entreprise/Société'),
        ('emergency', 'Service d\'urgence'),
        ('government', 'Administration publique'),
        ('law_enforcement', 'Forces de l\'ordre'),
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        initial='individual',
        required=True
    )
```

**Key Points:**
- User type is a required field in the registration form
- Default selection is 'individual'
- All five regular user types are available during registration
- Agent types (Partner Agent, Government Agent) are NOT available in registration form

### Registration View

**File:** `core/views.py`

```python
class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('core:velzon_dashboard')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user._user_type = form.cleaned_data['user_type']  # Store temporarily
        user.save()
        # User is logged in automatically after registration
        login(self.request, user, backend=...)
        return redirect(self.success_url)
```

**Registration Process:**
1. User fills out `CustomUserCreationForm` with user type selection
2. Form saves User instance with `_user_type` attribute
3. Django signal (`notifications/signals.py`) creates `UserProfile` with user_type
4. User is automatically logged in
5. Welcome notification is created

### Signal Handler

**File:** `notifications/signals.py`

```python
@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'profile'):
            user_type = getattr(instance, '_user_type', 'individual')
            UserProfile.objects.create(user=instance, user_type=user_type)
```

**Key Points:**
- Signal automatically creates `UserProfile` when User is created
- Uses `_user_type` attribute from form
- Defaults to 'individual' if `_user_type` is not set
- Extended profile models (IndividualProfile, CompanyProfile, etc.) are NOT automatically created

### Registration Differences by User Type

**All user types follow the same registration flow:**
- Same form fields (username, password, email, first_name, last_name, user_type)
- Same validation rules
- Same UserProfile creation process
- No additional fields required during registration

**Extended profiles are created separately:**
- IndividualProfile, CompanyProfile, etc. are created after registration
- Not part of the initial registration flow
- Can be created via admin interface or separate forms

### Agent Registration

**Partner Agent and Government Agent are NOT registered through the signup form:**
- Created separately by administrators
- Require separate profile creation (`AgentPartenaireProfile` or `AgentVerification`)
- Have dedicated login views:
  - `/administration/agent-partenaire/login/` (AgentPartenaireLoginView)
  - `/administration/agent-government/login/` (AgentGovernmentLoginView)

---

## Permissions and Access Control

### User Type-Based Permissions

**File:** `core/models.py` - UserProfile methods

```python
@property
def can_register_vehicles(self):
    """Check if user can register vehicles"""
    return self.is_verified or self.user_type in ['individual', 'company']

def get_allowed_vehicle_categories(self):
    """Get allowed vehicle categories for this user type"""
    if self.user_type == 'individual':
        return ['Personnel']
    elif self.user_type == 'company':
        return ['Commercial', 'Transport']
    # ... etc
```

### Agent Permissions

**File:** `administration/permissions.py`

```python
class IsAgentPartenaire(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_agent_partenaire(request.user)

class IsAgentGovernment(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_agent_government(request.user)
```

**File:** `core/utils/agent_utils.py`

```python
def is_agent_partenaire(user):
    return (
        hasattr(user, 'agent_partenaire_profile') and
        user.agent_partenaire_profile.is_active
    )

def is_agent_government(user):
    return (
        hasattr(user, 'agent_verification') and
        user.agent_verification.est_actif
    )
```

### Staff/Admin Permissions

**File:** `core/views.py`, `administration/mixins.py`

```python
def is_admin_user(user):
    """Check if user is an admin (excluding agents)"""
    if not user.is_authenticated:
        return False
    
    # Agents are NOT considered admins
    if is_agent_partenaire(user) or is_agent_government(user):
        return False
    
    return user.is_superuser or user.is_staff
```

**Key Points:**
- Agents are explicitly excluded from admin status
- `is_superuser` = full administrator
- `is_staff` = limited administrative access
- Admin users have access to Django admin interface

### View-Level Access Control

**Mixin Examples:**

1. **AgentPartenaireRequiredMixin** (`administration/mixins.py`)
   - Requires active AgentPartenaireProfile
   - Used for cash collection views

2. **AgentPartenaireMixin** (`payments/cash_views.py`)
   - Checks for active AgentPartenaireProfile
   - Checks group membership ("Agent Partenaire" group)

3. **Admin-only views:**
   - Use `is_admin_user()` check
   - Redirect non-admin users

### Permission Hierarchy

1. **Superuser** (is_superuser=True)
   - Full system access
   - Django admin access
   - All CRUD operations

2. **Staff** (is_staff=True, not superuser)
   - Limited admin access
   - Django admin access (limited permissions)

3. **Government Administrator** (user_type='government')
   - System administration capabilities
   - User management
   - Tax rate updates

4. **Agent Gouvernement** (has AgentVerification)
   - QR code verification
   - Verification dashboard access

5. **Agent Partenaire** (has AgentPartenaireProfile)
   - Cash collection
   - Payment processing
   - Commission tracking

6. **Company User** (user_type='company')
   - Fleet management
   - Bulk operations
   - Commercial vehicle registration

7. **Individual User** (user_type='individual')
   - Personal vehicle registration
   - Personal tax status viewing

8. **Emergency Service / Law Enforcement**
   - Specialized vehicle registration
   - Verification tools access

---

## API Endpoints

### Agent Partenaire API

**File:** `api/v1/views.py`

**Base URL:** `/api/v1/agent-partenaire/`

**Endpoints:**
- `GET /api/v1/agent-partenaire/profile/` - Get current agent profile
- `GET /api/v1/agent-partenaire/my_sessions/` - Get cash sessions
- `GET /api/v1/agent-partenaire/statistics/` - Get agent statistics

**Permissions:** `IsAuthenticated`, `IsAgentPartenaire`

**Example Response:**
```json
{
  "success": true,
  "data": {
    "agent_id": "AG12345678",
    "full_name": "Agent Name",
    "commission_rate": 2.50
  }
}
```

### Agent Government API

**File:** `api/v1/views.py`

**Base URL:** `/api/v1/agent-government/`

**Endpoints:**
- `GET /api/v1/agent-government/profile/` - Get current agent profile
- `POST /api/v1/agent-government/verify_qr_code/` - Verify QR code

**Permissions:** `IsAuthenticated`, `IsAgentGovernment`

**Example Request:**
```json
{
  "token": "qr_code_token",
  "gps_location": {"lat": -18.8792, "lng": 47.5079},
  "notes": "Verification notes"
}
```

### User Type Registration API

**Note:** The registration API endpoints are not explicitly defined in the codebase. Registration appears to be handled through web forms only.

---

## Validation Rules and Business Logic

### Vehicle Registration Rules by User Type

**File:** `core/models.py` - UserProfile methods

```python
def get_allowed_vehicle_categories(self):
    """Get allowed vehicle categories for this user type"""
    if self.user_type == 'individual':
        return ['Personnel']
    elif self.user_type == 'company':
        return ['Commercial', 'Transport']
    elif self.user_type == 'emergency':
        return ['Ambulance', 'Sapeurs-pompiers', 'Secours']
    elif self.user_type == 'government':
        return ['Administratif', 'Personnel', 'Commercial', 'Transport', 'Ambulance', 'Sapeurs-pompiers']
    elif self.user_type == 'law_enforcement':
        return ['Police', 'Gendarmerie', 'Personnel']
    return []

def get_allowed_terrestrial_subtypes(self):
    """Get allowed terrestrial vehicle subtypes for this user type"""
    if self.user_type == 'individual':
        return ['moto', 'scooter', 'voiture']
    elif self.user_type == 'company':
        return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']
    elif self.user_type == 'emergency':
        return ['voiture', 'camion', 'bus', 'camionnette']
    elif self.user_type == 'government':
        return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']
    elif self.user_type == 'law_enforcement':
        return ['moto', 'scooter', 'voiture', 'camion']
    return []
```

### Vehicle Registration Eligibility

**File:** `core/models.py`

```python
@property
def can_register_vehicles(self):
    """Check if user can register vehicles"""
    return self.is_verified or self.user_type in ['individual', 'company']
```

**Rules:**
- Individual and Company users can register vehicles immediately (even if not verified)
- Other user types require verification before vehicle registration
- Verification status: 'pending', 'verified', 'rejected', 'under_review'

### Form Validation

**File:** `core/forms.py`

- Username: Required, Django's standard validation
- Password: Required, Django's password validation (min length, complexity)
- Email: Optional
- First Name: Optional
- Last Name: Optional
- User Type: Required, must be one of the predefined choices

### Agent Validation

**AgentPartenaireProfile:**
- `agent_id`: Auto-generated if not provided (format: 'AG' + 8 random alphanumeric)
- `is_active`: Must be True for access
- `commission_rate`: Optional, uses default if not set

**AgentVerification:**
- `numero_badge`: Required, unique
- `est_actif`: Must be True for access
- `zone_affectation`: Required

### Business Logic Constraints

1. **User Type Immutability:**
   - User type is set during registration
   - No evidence of user type change functionality in codebase
   - Changing user type would require manual database update

2. **Profile Creation:**
   - UserProfile is created automatically via signal
   - Extended profiles (IndividualProfile, CompanyProfile, etc.) are NOT created automatically
   - Must be created separately if needed

3. **Agent Creation:**
   - Agents cannot self-register
   - Must be created by administrators
   - Require separate User account creation first

4. **Verification Workflow:**
   - All users start with `verification_status='pending'`
   - Verification is manual (no automatic verification logic found)
   - Verified users have expanded permissions

---

## Implementation Type: Static vs Dynamic

### Current Implementation: **STATIC (Hardcoded)**

The user type implementation is **static/hardcoded** and requires code changes to modify:

#### Evidence of Static Implementation:

1. **Hardcoded Choices in Models:**
   ```python
   # core/models.py
   USER_TYPE_CHOICES = [
       ('individual', 'Individual Citizen'),
       ('company', 'Company/Business'),
       ('emergency', 'Emergency Service Provider'),
       ('government', 'Government Administrator'),
       ('law_enforcement', 'Law Enforcement Officer'),
   ]
   ```

2. **Hardcoded Choices in Forms:**
   ```python
   # core/forms.py
   USER_TYPE_CHOICES = [
       ('individual', 'Particulier (Citoyen)'),
       ('company', 'Entreprise/Société'),
       ('emergency', 'Service d\'urgence'),
       ('government', 'Administration publique'),
       ('law_enforcement', 'Forces de l\'ordre'),
   ]
   ```

3. **Hardcoded Business Logic:**
   - `get_allowed_vehicle_categories()` uses if/elif statements
   - `get_allowed_terrestrial_subtypes()` uses if/elif statements
   - No database-driven configuration found

4. **No Configuration Model:**
   - No `UserTypeConfig` or similar model found
   - No admin interface for managing user types dynamically
   - User types are defined in code only

#### To Add a New User Type:

1. Add choice to `UserProfile.USER_TYPE_CHOICES`
2. Add choice to `CustomUserCreationForm.USER_TYPE_CHOICES`
3. Update `get_allowed_vehicle_categories()` method
4. Update `get_allowed_terrestrial_subtypes()` method
5. Create extended profile model if needed
6. Update any view logic that checks user types
7. Update templates if needed
8. Run migrations if schema changes are needed

#### Configuration That IS Dynamic:

1. **Agent Status:**
   - `is_active` flag for agents can be toggled without code changes
   - Agent profiles can be created/deactivated via admin

2. **Verification Status:**
   - Can be changed via admin interface
   - No code changes needed

3. **Staff Flags:**
   - `is_staff` and `is_superuser` can be toggled via Django admin
   - No code changes needed

### Summary

- **User Types (individual, company, etc.):** STATIC - requires code changes
- **Agent Types:** STATIC - requires code changes to add new agent types
- **Staff Roles:** DYNAMIC - can be managed via Django admin
- **User Type Permissions:** STATIC - hardcoded in methods
- **Vehicle Category Rules:** STATIC - hardcoded in methods

---

## Additional Notes

### Legacy Support

- `est_entreprise` field in UserProfile maintained for backward compatibility
- `EntrepriseProfile` model exists but appears to be legacy (separate from CompanyProfile)

### Missing Features

1. **No automatic extended profile creation:**
   - IndividualProfile, CompanyProfile, etc. are not created during registration
   - Must be created separately if needed

2. **No user type change functionality:**
   - No UI or API to change user type after registration
   - Would require manual database update

3. **No user type-specific registration forms:**
   - All user types use the same registration form
   - Extended profile fields are not collected during registration

### File Locations Summary

- **Models:** `core/models.py`, `payments/models.py`, `administration/models.py`
- **Forms:** `core/forms.py`
- **Views:** `core/views.py`, `administration/auth_views.py`, `payments/cash_views.py`
- **API:** `api/v1/views.py`, `api/v1/serializers.py`
- **Permissions:** `administration/permissions.py`
- **Utils:** `core/utils/agent_utils.py`
- **Signals:** `notifications/signals.py`
- **Templates:** `templates/registration/register.html`

---

## Conclusion

The system implements a comprehensive but static user type system. User types are hardcoded in the codebase and require code changes to modify. The implementation supports multiple user categories with distinct permissions, vehicle registration rules, and access levels. Agent types and staff roles are separate from regular user types and have their own authentication and authorization mechanisms.

