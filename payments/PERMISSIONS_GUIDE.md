# Cash Payment System - Permissions Guide

This guide explains the permission system for the cash payment system, including groups, decorators, and how to assign permissions to users.

## Overview

The cash payment system uses Django's built-in permission system with two main user groups:

1. **Agent Partenaire** - Partner agents who collect cash payments
2. **Admin Staff** - Administrative staff who manage the system

## Permission Groups

### Agent Partenaire Group

Agent Partenaire users can:
- Open and close their own cash sessions
- Create cash transactions and receipts
- View their own commission records
- Search for customers and calculate taxes
- Print and reprint receipts
- View system configuration (read-only)

**Permissions:**
- `add_cashsession`, `view_cashsession`, `change_cashsession`
- `add_cashtransaction`, `view_cashtransaction`
- `add_cashreceipt`, `view_cashreceipt`
- `view_commissionrecord`
- `view_agentpartenaireprofile`
- `view_cashsystemconfig`

### Admin Staff Group

Admin Staff users have full access to:
- Manage Agent Partenaire profiles (create, edit, deactivate)
- View all cash sessions and transactions
- Approve high-value transactions
- Perform daily reconciliation
- Generate reports (collection, commission, discrepancy, audit)
- Configure system settings
- View audit trail

**Permissions:**
- Full CRUD on all cash payment models
- View-only access to audit logs (immutable)

## Setting Up Permissions

### 1. Create Permission Groups

Run the management command to create the groups and assign permissions:

```bash
python manage.py setup_cash_permissions
```

This command:
- Creates "Agent Partenaire" and "Admin Staff" groups
- Assigns appropriate permissions to each group
- Can be run multiple times safely (idempotent)

### 2. Assign Users to Groups

#### For Agent Partenaire:

```python
from django.contrib.auth.models import Group
from core.models import User
from payments.models import AgentPartenaireProfile

# Get or create the user
user = User.objects.get(username='agent_username')

# Create agent profile
agent_profile = AgentPartenaireProfile.objects.create(
    user=user,
    agent_id='AGT001',
    full_name='John Doe',
    phone_number='0340000000',
    collection_location='Antananarivo',
    is_active=True,
    created_by=admin_user
)

# Add user to Agent Partenaire group
agent_group = Group.objects.get(name='Agent Partenaire')
user.groups.add(agent_group)
```

#### For Admin Staff:

```python
from django.contrib.auth.models import Group
from core.models import User

# Get or create the user
user = User.objects.get(username='admin_username')

# Make user staff
user.is_staff = True
user.save()

# Add user to Admin Staff group
admin_group = Group.objects.get(name='Admin Staff')
user.groups.add(admin_group)
```

## Using Permission Decorators

The system provides three decorators for function-based views:

### 1. @agent_partenaire_required

Restricts access to active Agent Partenaire users:

```python
from payments.decorators import agent_partenaire_required

@agent_partenaire_required
def my_agent_view(request):
    # Only accessible by active Agent Partenaire users
    agent_profile = request.user.agent_partenaire_profile
    # ... view logic
    return render(request, 'template.html')
```

### 2. @admin_staff_required

Restricts access to Admin Staff users:

```python
from payments.decorators import admin_staff_required

@admin_staff_required
def my_admin_view(request):
    # Only accessible by Admin Staff users
    # ... view logic
    return render(request, 'template.html')
```

### 3. @agent_partenaire_or_admin_required

Allows access to both Agent Partenaire and Admin Staff:

```python
from payments.decorators import agent_partenaire_or_admin_required

@agent_partenaire_or_admin_required
def my_shared_view(request):
    # Accessible by both Agent Partenaire and Admin Staff
    # ... view logic
    return render(request, 'template.html')
```

## Using Permission Mixins

For class-based views, use the provided mixins:

### AgentPartenaireMixin

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from payments.cash_views import AgentPartenaireMixin
from django.views.generic import ListView

class MyAgentView(LoginRequiredMixin, AgentPartenaireMixin, ListView):
    """View accessible only by Agent Partenaire"""
    model = CashTransaction
    template_name = 'my_template.html'
    
    def get_queryset(self):
        # Get agent profile
        agent = self.get_agent_profile()
        # Filter by agent
        return super().get_queryset().filter(collector=agent)
```

### AdminStaffMixin

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from payments.cash_admin_views import AdminStaffMixin
from django.views.generic import ListView

class MyAdminView(LoginRequiredMixin, AdminStaffMixin, ListView):
    """View accessible only by Admin Staff"""
    model = AgentPartenaireProfile
    template_name = 'my_template.html'
```

## Permission Checks in Templates

Check user permissions in templates:

```django
{% if user.groups.all|join:", "|lower == "agent partenaire" %}
    <a href="{% url 'payments:session_open' %}">Open Session</a>
{% endif %}

{% if user.is_staff %}
    <a href="{% url 'payments:collector_list' %}">Manage Agents</a>
{% endif %}

{% if perms.payments.add_cashtransaction %}
    <button>Create Transaction</button>
{% endif %}
```

## Checking Permissions in Code

### Check if user is Agent Partenaire:

```python
def is_agent_partenaire(user):
    return (
        hasattr(user, 'agent_partenaire_profile') and
        user.agent_partenaire_profile.is_active and
        user.groups.filter(name='Agent Partenaire').exists()
    )
```

### Check if user is Admin Staff:

```python
def is_admin_staff(user):
    return (
        user.is_staff and
        (user.is_superuser or user.groups.filter(name='Admin Staff').exists())
    )
```

### Check specific permissions:

```python
# Check if user can add cash transactions
if user.has_perm('payments.add_cashtransaction'):
    # Allow transaction creation
    pass

# Check if user can change system config
if user.has_perm('payments.change_cashsystemconfig'):
    # Allow config changes
    pass
```

## Security Best Practices

1. **Always use LoginRequiredMixin** for class-based views or `@login_required` for function-based views
2. **Combine with role mixins/decorators** to enforce role-based access
3. **Check permissions at multiple levels**: URL, view, and template
4. **Use get_agent_profile()** in Agent Partenaire views to ensure proper agent context
5. **Validate ownership** - agents should only access their own sessions/transactions
6. **Log permission denials** for security auditing

## Troubleshooting

### User can't access Agent Partenaire views

Check:
1. User has an `AgentPartenaireProfile` with `is_active=True`
2. User is in "Agent Partenaire" group
3. User is authenticated

```python
user = User.objects.get(username='agent_username')
print(f"Has profile: {hasattr(user, 'agent_partenaire_profile')}")
print(f"Is active: {user.agent_partenaire_profile.is_active}")
print(f"In group: {user.groups.filter(name='Agent Partenaire').exists()}")
```

### User can't access Admin Staff views

Check:
1. User has `is_staff=True`
2. User is in "Admin Staff" group OR is superuser

```python
user = User.objects.get(username='admin_username')
print(f"Is staff: {user.is_staff}")
print(f"Is superuser: {user.is_superuser}")
print(f"In group: {user.groups.filter(name='Admin Staff').exists()}")
```

### Re-run permission setup

If permissions are missing or incorrect:

```bash
python manage.py setup_cash_permissions
```

This will reset all permissions for both groups.

## Testing Permissions

Run the permission tests:

```bash
python manage.py test payments.tests_permissions
```

This will verify:
- Permission groups exist
- Users are correctly assigned to groups
- Decorators work as expected
- Mixins enforce access control
