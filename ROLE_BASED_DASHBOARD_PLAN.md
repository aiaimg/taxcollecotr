# Role-Based Dashboard & Sidebar Implementation Plan

## Overview
This plan outlines the implementation of separate dashboards, sidebars, and access controls for different user types in the Tax Collector system.

## User Types & Roles

### 1. **Client/Individual Users** (`user_type='individual'`)
- Regular citizens who own vehicles
- Can register vehicles, make payments, view history
- Access to: Personal dashboard, vehicles, payments, profile

### 2. **Company Users** (`user_type='company'`)
- Businesses with fleets of vehicles
- Access to: Fleet dashboard, batch payments, fleet management
- Same as individual but with fleet features

### 3. **Agent Partenaire** (`has AgentPartenaireProfile`)
- Partner agents who collect cash payments
- Access to: Cash collection dashboard, sessions, payments, commissions
- Cannot access admin features

### 4. **Agent Gouvernement** (`has AgentVerification`)
- Government agents who verify QR codes
- Access to: QR verification dashboard, verification history, statistics
- Cannot access admin or collection features

### 5. **Administration Staff** (`is_staff=True` or `is_superuser=True`)
- System administrators with different roles:
  - **Super Admin** (`is_superuser=True`): Full access
  - **Admin Staff** (`is_staff=True`): Limited admin access based on permissions
  - **Finance Staff**: Payment management, reconciliation
  - **Vehicle Management Staff**: Vehicle registration, verification
  - **User Management Staff**: User management, agent management
  - **Analytics Staff**: Reports, analytics only

---

## Implementation Plan

### Phase 1: Context Processor Enhancement

#### 1.1 Update `core/context_processors.py`
**File:** `core/context_processors.py`

**Changes:**
- Add comprehensive user role detection
- Detect agent types (partenaire, government)
- Detect admin roles and permissions
- Provide role flags for templates

**New Context Variables:**
```python
{
    'user_type': 'individual' | 'company' | 'agent_partenaire' | 'agent_government' | 'admin',
    'is_agent_partenaire': bool,
    'is_agent_government': bool,
    'is_any_agent': bool,
    'is_admin_user': bool,
    'is_superuser': bool,
    'admin_permissions': {
        'can_manage_users': bool,
        'can_manage_vehicles': bool,
        'can_manage_payments': bool,
        'can_manage_agents': bool,
        'can_view_analytics': bool,
        'can_manage_finance': bool,
    },
    'user_role_display': str,  # Human-readable role name
}
```

---

### Phase 2: Dashboard Views

#### 2.1 Client/Individual Dashboard
**File:** `core/views.py` → `ClientDashboardView`

**Features:**
- Personal vehicle list (count, status)
- Payment history summary
- Upcoming tax due dates
- Quick actions (register vehicle, make payment)
- Recent activity feed
- Statistics (total vehicles, total paid, pending payments)

**URL:** `/dashboard/client/` or `/dashboard/` (default for individual users)

**Template:** `templates/core/dashboards/client_dashboard.html`

---

#### 2.2 Company/Fleet Dashboard
**File:** `core/views.py` → `CompanyDashboardView` (exists as `FleetDashboardView`)

**Features:**
- Fleet overview (total vehicles, active, inactive)
- Batch payment options
- Fleet statistics
- Vehicle registration status
- Payment history by vehicle
- Export options

**URL:** `/dashboard/fleet/` or `/fleet/`

**Template:** `templates/fleet/dashboard.html` (exists)

---

#### 2.3 Agent Partenaire Dashboard
**File:** `payments/cash_views.py` → `CollectorDashboardView` (exists)

**Features:**
- Active session status
- Today's transactions (count, total)
- Today's commission
- Quick actions (open session, create payment)
- Recent transactions
- Session history
- Commission summary

**URL:** `/payments/cash/dashboard/`

**Template:** `templates/payments/cash/agent_dashboard.html` (exists)

**Enhancements Needed:**
- Add more statistics
- Add commission charts
- Add session performance metrics

---

#### 2.4 Agent Gouvernement Dashboard
**File:** `payments/views.py` → `QRVerificationDashboardView` (exists)

**Features:**
- Today's verifications (count, valid/invalid)
- Weekly verification statistics
- Recent verifications list
- Quick actions (scan QR, manual token)
- Verification status breakdown
- Agent information (badge, zone)

**URL:** `/payments/qr/verification/dashboard/`

**Template:** `templates/payments/qr_verification_dashboard.html` (exists)

**Enhancements Needed:**
- Add verification trends
- Add zone-based statistics
- Add performance metrics

---

#### 2.5 Administration Dashboard
**File:** `administration/views.py` → `dashboard_view` (exists)

**Features:**
- System-wide statistics
- User management overview
- Vehicle management overview
- Payment management overview
- Cash collection overview
- QR verification overview
- Recent activities
- System alerts

**URL:** `/administration/dashboard/`

**Template:** `templates/administration/dashboard.html` (exists)

**Enhancements Needed:**
- Role-based data filtering
- Permission-based widget visibility
- Staff-specific views

---

### Phase 3: Sidebar Templates

#### 3.1 Client/Individual Sidebar
**File:** `templates/velzon/partials/sidebar_client.html` (NEW)

**Menu Items:**
- Dashboard
- My Vehicles
  - Vehicle List
  - Register Vehicle
- Payments
  - Payment History
  - Make Payment
  - QR Code Verification
- Notifications
- Profile
- Settings
- Logout

---

#### 3.2 Company/Fleet Sidebar
**File:** `templates/velzon/partials/sidebar_company.html` (NEW)

**Menu Items:**
- Fleet Dashboard
- Fleet Management
  - All Vehicles
  - Register Vehicle
  - Vehicle Status
- Payments
  - Payment History
  - Batch Payment
  - Payment Reports
- Data Export
  - Export CSV
  - Export Excel
  - Export PDF
- Notifications
- Profile
- Settings
- Logout

---

#### 3.3 Agent Partenaire Sidebar
**File:** `templates/velzon/partials/sidebar_agent_partenaire.html` (NEW)

**Menu Items:**
- Dashboard
- Cash Collection
  - Open Session
  - Active Session
  - Payment Create
  - Session History
- Commissions
  - My Commissions
  - Commission History
- Receipts
  - Print Receipt
  - Receipt History
- Notifications
- Profile
- Settings
- Logout

---

#### 3.4 Agent Gouvernement Sidebar
**File:** `templates/velzon/partials/sidebar_agent_government.html` (NEW)

**Menu Items:**
- Dashboard
- QR Verification
  - Scan QR Code
  - Manual Verification
  - Verification History
- Statistics
  - Today's Verifications
  - Weekly Report
  - Monthly Report
- Notifications
- Profile
- Settings
- Logout

---

#### 3.5 Administration Sidebar
**File:** `templates/velzon/partials/sidebar_administration.html` (EXISTS - needs enhancement)

**Menu Items:**
- Dashboard
- Vehicle Management (if permission)
  - Vehicle List
  - Add Vehicle
  - Advanced Search
  - Vehicle Types
  - Vehicle Documents
- User Management (if permission)
  - User List
  - Agent Partenaire
  - Agent Gouvernement
  - User Permissions
- Payment Management (if permission)
  - Payment List
  - Payment Gateways
  - Stripe Settings
- Cash Collection Admin (if permission)
  - Agents Partenaires
  - Approvals
  - Reconciliation
  - Reports
  - System Config
- Price Grids (if permission)
- Analytics (if permission)
- System Settings (superuser only)
- Profile
- Logout

---

### Phase 4: Base Template Updates

#### 4.1 Update `templates/base_velzon.html`
**File:** `templates/base_velzon.html`

**Changes:**
- Update sidebar block to use role-based sidebar selection
- Add logic to select appropriate sidebar based on user type
- Update dashboard redirect logic

**New Sidebar Selection Logic:**
```django
{% block sidebar %}
    {% if user.is_superuser or user.is_staff %}
        {% include "velzon/partials/sidebar_administration.html" %}
    {% elif user|is_agent_government %}
        {% include "velzon/partials/sidebar_agent_government.html" %}
    {% elif user|is_agent_partenaire %}
        {% include "velzon/partials/sidebar_agent_partenaire.html" %}
    {% elif user.profile.user_type == 'company' %}
        {% include "velzon/partials/sidebar_company.html" %}
    {% else %}
        {% include "velzon/partials/sidebar_client.html" %}
    {% endif %}
{% endblock sidebar %}
```

---

### Phase 5: Template Tags

#### 5.1 Create Role Detection Template Tags
**File:** `core/templatetags/role_tags.py` (NEW)

**Tags:**
- `is_agent_partenaire`
- `is_agent_government`
- `is_any_agent`
- `is_admin_user`
- `has_admin_permission`

---

### Phase 6: URL Routing & Redirects

#### 6.1 Update Login Redirects
**File:** `core/views.py` → `CustomLoginView`

**Changes:**
- Redirect based on user type after login
- Agent Partenaire → Cash Dashboard
- Agent Gouvernement → QR Verification Dashboard
- Admin → Administration Dashboard
- Client → Client Dashboard
- Company → Fleet Dashboard

#### 6.2 Update Dashboard URLs
**File:** `core/urls.py`

**New URLs:**
```python
path('dashboard/', views.ClientDashboardView.as_view(), name='client_dashboard'),
path('dashboard/fleet/', views.CompanyDashboardView.as_view(), name='company_dashboard'),
```

#### 6.3 Update Administration URLs
**File:** `administration/urls.py`

**Keep existing:** `/administration/dashboard/`

---

### Phase 7: Administration Role-Based Access

#### 7.1 Create Permission System
**File:** `administration/models.py` (NEW - if needed)

**Options:**
1. Use Django Groups and Permissions
2. Create custom AdminRole model
3. Use UserProfile with permission flags

**Recommended:** Use Django Groups with custom permissions

#### 7.2 Create Admin Permission Decorators/Mixins
**File:** `administration/mixins.py` (EXISTS - enhance)

**New Mixins:**
- `FinanceStaffRequiredMixin`
- `VehicleManagementStaffRequiredMixin`
- `UserManagementStaffRequiredMixin`
- `AnalyticsStaffRequiredMixin`
- `AgentManagementStaffRequiredMixin`

#### 7.3 Update Administration Views
**File:** `administration/views.py`

**Changes:**
- Add permission checks to all views
- Filter data based on permissions
- Show/hide menu items based on permissions

---

### Phase 8: Commission Template Fix

#### 8.1 Fix `sum_commission` Filter
**File:** `administration/templatetags/currency_filters.py` or create new filter

**Solution Options:**
1. Create `sum_commission` template filter
2. Calculate sum in view and pass to template
3. Use Django template `|add` filter with loop

**Recommended:** Calculate in view and pass as context variable

**File:** `payments/cash_views.py` → `CollectorCommissionView`

**Changes:**
- Calculate total commission in view
- Add `total_commission_sum` to context
- Update template to use context variable instead of filter

---

## Implementation Steps

### Step 1: Fix Immediate Issues
1. ✅ Fix `sum_commission` filter error in commission list
2. ✅ Fix namespace issues (already done)

### Step 2: Enhance Context Processor
1. Update `core/context_processors.py`
2. Add agent detection logic
3. Add admin permission detection
4. Test context variables

### Step 3: Create Template Tags
1. Create `core/templatetags/role_tags.py`
2. Add role detection tags
3. Register tags
4. Test in templates

### Step 4: Create Sidebar Templates
1. Create `sidebar_client.html`
2. Create `sidebar_company.html`
3. Create `sidebar_agent_partenaire.html`
4. Create `sidebar_agent_government.html`
5. Update `sidebar_administration.html` with permissions

### Step 5: Update Base Template
1. Update `base_velzon.html` sidebar block
2. Add role-based sidebar selection
3. Test all user types

### Step 6: Create/Update Dashboards
1. Create `ClientDashboardView`
2. Update `CompanyDashboardView` (FleetDashboardView)
3. Enhance `CollectorDashboardView`
4. Enhance `QRVerificationDashboardView`
5. Enhance `AdministrationDashboardView`

### Step 7: Update URL Routing
1. Update login redirects
2. Add dashboard URLs
3. Update navigation links
4. Test all redirects

### Step 8: Implement Admin Permissions
1. Create Django groups for admin roles
2. Create permission mixins
3. Update administration views
4. Test permission-based access

### Step 9: Testing
1. Test all user types can access their dashboards
2. Test sidebars show correct menu items
3. Test permission-based access in administration
4. Test redirects after login
5. Test navigation between pages

### Step 10: Documentation
1. Document user roles and permissions
2. Document dashboard features
3. Document sidebar structure
4. Create user guide for each role

---

## File Structure

```
core/
├── context_processors.py (UPDATE)
├── templatetags/
│   ├── role_tags.py (NEW)
│   └── currency_filters.py (UPDATE - add sum_commission)
├── views.py (UPDATE - add ClientDashboardView)
└── urls.py (UPDATE - add dashboard URLs)

payments/
├── cash_views.py (UPDATE - fix commission sum)
└── views.py (EXISTS - QRVerificationDashboardView)

administration/
├── mixins.py (UPDATE - add permission mixins)
├── views.py (UPDATE - add permission checks)
└── models.py (NEW - if custom permissions needed)

templates/
├── base_velzon.html (UPDATE - sidebar selection)
├── velzon/partials/
│   ├── sidebar_client.html (NEW)
│   ├── sidebar_company.html (NEW)
│   ├── sidebar_agent_partenaire.html (NEW)
│   ├── sidebar_agent_government.html (NEW)
│   └── sidebar_administration.html (UPDATE - permissions)
└── core/dashboards/
    └── client_dashboard.html (NEW)
```

---

## Priority Order

### High Priority (Immediate)
1. ✅ Fix `sum_commission` filter error
2. Create role-based sidebar templates
3. Update base template sidebar selection
4. Create client dashboard

### Medium Priority (Next)
1. Enhance context processor
2. Create template tags
3. Update login redirects
4. Enhance existing dashboards

### Low Priority (Later)
1. Admin permission system
2. Advanced analytics
3. Performance optimization
4. Documentation

---

## Testing Checklist

### Client/Individual User
- [ ] Can access client dashboard
- [ ] Sees client sidebar
- [ ] Can navigate to vehicles
- [ ] Can navigate to payments
- [ ] Cannot access admin features
- [ ] Cannot access agent features

### Company User
- [ ] Can access fleet dashboard
- [ ] Sees company sidebar
- [ ] Can access fleet management
- [ ] Can access batch payments
- [ ] Cannot access admin features

### Agent Partenaire
- [ ] Can access cash dashboard
- [ ] Sees agent partenaire sidebar
- [ ] Can access cash collection features
- [ ] Can access commission features
- [ ] Cannot access admin features
- [ ] Cannot access QR verification

### Agent Gouvernement
- [ ] Can access QR verification dashboard
- [ ] Sees agent government sidebar
- [ ] Can access QR verification features
- [ ] Cannot access admin features
- [ ] Cannot access cash collection

### Administration Staff
- [ ] Can access admin dashboard
- [ ] Sees admin sidebar
- [ ] Can access features based on permissions
- [ ] Cannot access features without permissions
- [ ] Superuser has full access

---

## Notes

1. **Backward Compatibility**: Ensure existing functionality continues to work
2. **Security**: All permission checks must be server-side, not just template-side
3. **Performance**: Minimize database queries in context processor
4. **User Experience**: Smooth transitions between different user types
5. **Maintainability**: Keep code DRY, use mixins and template tags
6. **Scalability**: Design for future user types and permissions

---

## Estimated Time

- **Phase 1-2**: 2-3 days (Context processor, template tags)
- **Phase 3-4**: 2-3 days (Sidebar templates, base template)
- **Phase 5-6**: 2-3 days (Dashboards, URL routing)
- **Phase 7**: 3-4 days (Admin permissions)
- **Phase 8**: 1 day (Commission fix)
- **Testing**: 2-3 days
- **Total**: 12-17 days

---

## Next Steps

1. Review and approve this plan
2. Start with Phase 1 (Context Processor)
3. Fix immediate issues (commission filter)
4. Implement sidebars one by one
5. Test each phase before moving to next

