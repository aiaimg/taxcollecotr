# Agent System Analysis and Implementation Plan

## Executive Summary

This document analyzes the current agent system implementation and proposes a comprehensive solution for managing two types of agents:
1. **Agent Partenaire** - Partner agents who help users pay taxes (cash collection)
2. **Agent Gouvernement** - Government agents who scan and verify QR codes

## Current State Analysis

### 1. Existing Models

#### AgentPartenaireProfile (payments/models.py)
- **Purpose**: Partner agents who collect cash payments from users
- **Fields**:
  - `user` (OneToOneField to User)
  - `agent_id` (unique identifier)
  - `full_name`, `phone_number`
  - `collection_location` (where they collect payments)
  - `commission_rate` (custom commission rate)
  - `use_default_commission` (boolean)
  - `is_active` (boolean)
  - `created_by` (User who created the agent)
- **Related Models**:
  - `PaiementTaxe.collected_by` (ForeignKey to AgentPartenaireProfile)
  - `CashSession` (tracks cash collection sessions)
- **Mixin**: `AgentPartenaireMixin` (checks for active profile and group membership)

#### AgentVerification (administration/models.py)
- **Purpose**: Government agents who verify QR codes
- **Fields**:
  - `user` (OneToOneField to User)
  - `numero_badge` (unique badge number)
  - `zone_affectation` (assigned zone)
  - `est_actif` (boolean)
- **Related Models**:
  - `VerificationQR` (logs QR code verifications)
    - Fields: `agent`, `qr_code`, `statut_verification`, `date_verification`, `localisation_gps`, `notes`

### 2. User Types (core/models.py)
Current user types:
- `individual` - Individual Citizen
- `company` - Company/Business
- `emergency` - Emergency Service Provider
- `government` - Government Administrator
- `law_enforcement` - Law Enforcement Officer

**Note**: No specific user types for agents. Agents are identified through their profiles.

### 3. QR Code System

#### QRCode Model (payments/models.py)
- **Fields**:
  - `vehicule_plaque` (ForeignKey to Vehicule)
  - `annee_fiscale` (year)
  - `token` (unique token for verification) ⚠️ **IMPORTANT: Uses `token`, not `code`**
  - `date_generation`, `date_expiration`
  - `est_actif` (boolean)
  - `nombre_scans` (scan counter)
  - `derniere_verification` (last verification timestamp)

#### QR Code Verification Views
- **QRCodeVerifyView** (payments/views.py:878)
  - **BUG**: Uses `QRCode.objects.get(code=code)` but should use `token=code`
  - Checks for `request.user.agent_verification` to log verifications
  - Increments scan count and updates last verification time

- **QRCodeVerifyAPIView** (payments/views.py)
  - Similar functionality, returns JSON response
  - Same bug as above

- **API Endpoint** (api/v1/views.py)
  - `QRCodeViewSet.verify()` action
  - Uses `token` correctly in API

### 4. Authentication & Authorization

#### Current Checks
- **AgentPartenaire**: 
  - `AgentPartenaireMixin` checks for `agent_partenaire_profile` and group membership
  - Requires user to be in "Agent Partenaire" group OR staff/superuser

- **AgentVerification**:
  - No dedicated mixin
  - Views check `hasattr(request.user, 'agent_verification')`
  - No permission classes for API endpoints

#### Issues
1. ❌ No unified way to check if user is any type of agent
2. ❌ QR code verification views have bug (use `code` instead of `token`)
3. ❌ No dedicated authentication flow for agents
4. ❌ Agent verification doesn't have proper permission checks
5. ❌ No API endpoints for agent-specific operations

### 5. Cash Payment System

#### Existing Features
- `CashSession` model (tracks cash collection sessions)
- `CashSessionOpenView`, `CashSessionCloseView`
- `CashPaymentCreateView` (for agent partenaire to create payments)
- `CashSystemConfig` (system configuration for cash payments)

#### Workflow
1. Agent Partenaire opens a cash session
2. User pays cash to agent
3. Agent creates payment record with `collected_by` set
4. Agent closes session and reconciles

## Proposed Solution

### Phase 1: Fix Critical Bugs

#### 1.1 Fix QR Code Verification Bug
**Issue**: `QRCodeVerifyView` and `QRCodeVerifyAPIView` use `code=code` but QRCode model uses `token`

**Fix**:
- Change `QRCode.objects.get(code=code)` to `QRCode.objects.get(token=code)`
- Update URL patterns to use `token` instead of `code` for clarity
- Update templates and API documentation

**Files to modify**:
- `payments/views.py` (QRCodeVerifyView, QRCodeVerifyAPIView)
- `payments/urls.py` (update URL patterns)
- `api/v1/views.py` (if needed)

### Phase 2: Unified Agent System

#### 2.1 Create Agent Type Enumeration
Add agent types to UserProfile or create separate agent type field:

**Option A**: Add to UserProfile.USER_TYPE_CHOICES
```python
USER_TYPE_CHOICES = [
    ('individual', 'Individual Citizen'),
    ('company', 'Company/Business'),
    ('emergency', 'Emergency Service Provider'),
    ('government', 'Government Administrator'),
    ('law_enforcement', 'Law Enforcement Officer'),
    ('agent_partenaire', 'Agent Partenaire'),  # NEW
    ('agent_government', 'Agent Gouvernement'),  # NEW
]
```

**Option B**: Keep profiles separate but add unified checking functions
```python
# core/utils.py or administration/utils.py
def is_agent_partenaire(user):
    return hasattr(user, 'agent_partenaire_profile') and user.agent_partenaire_profile.is_active

def is_agent_government(user):
    return hasattr(user, 'agent_verification') and user.agent_verification.est_actif

def is_any_agent(user):
    return is_agent_partenaire(user) or is_agent_government(user)
```

**Recommendation**: Option B (keep profiles separate, add utility functions)
- More flexible
- Doesn't require migration of existing user types
- Allows users to have both profiles if needed (future use case)

#### 2.2 Create Agent Permission Classes
```python
# administration/permissions.py
from rest_framework import permissions

class IsAgentPartenaire(permissions.BasePermission):
    """Permission for Agent Partenaire"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'agent_partenaire_profile') and
            request.user.agent_partenaire_profile.is_active
        )

class IsAgentGovernment(permissions.BasePermission):
    """Permission for Agent Gouvernement"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'agent_verification') and
            request.user.agent_verification.est_actif
        )

class IsAnyAgent(permissions.BasePermission):
    """Permission for any type of agent"""
    def has_permission(self, request, view):
        return (
            IsAgentPartenaire().has_permission(request, view) or
            IsAgentGovernment().has_permission(request, view)
        )
```

#### 2.3 Create Agent Mixins
```python
# administration/mixins.py (extend existing)
class AgentPartenaireRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for views that require Agent Partenaire"""
    login_url = reverse_lazy('core:login')
    
    def test_func(self):
        from core.utils import is_agent_partenaire
        return is_agent_partenaire(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, _('Accès refusé. Vous devez être un Agent Partenaire.'))
        return redirect('core:dashboard')

class AgentGovernmentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for views that require Agent Gouvernement"""
    login_url = reverse_lazy('core:login')
    
    def test_func(self):
        from core.utils import is_agent_government
        return is_agent_government(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, _('Accès refusé. Vous devez être un Agent Gouvernement.'))
        return redirect('core:dashboard')
```

### Phase 3: Agent Authentication & Login

#### 3.1 Create Agent Login Views
```python
# administration/auth_views.py (extend existing)
class AgentPartenaireLoginView(LoginView):
    """Login view for Agent Partenaire"""
    template_name = 'administration/auth/agent_partenaire_login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('payments:cash_session_open')
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'agent_partenaire_profile') and user.agent_partenaire_profile.is_active:
                login(self.request, user)
                messages.success(self.request, _('Connexion Agent Partenaire réussie'))
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, _('Accès refusé. Compte Agent Partenaire non actif.'))
                return self.form_invalid(form)
        else:
            messages.error(self.request, _('Nom d\'utilisateur ou mot de passe incorrect'))
            return self.form_invalid(form)

class AgentGovernmentLoginView(LoginView):
    """Login view for Agent Gouvernement"""
    template_name = 'administration/auth/agent_government_login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('payments:qr_verify_dashboard')  # New dashboard for QR verification
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'agent_verification') and user.agent_verification.est_actif:
                login(self.request, user)
                messages.success(self.request, _('Connexion Agent Gouvernement réussie'))
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, _('Accès refusé. Compte Agent Gouvernement non actif.'))
                return self.form_invalid(form)
        else:
            messages.error(self.request, _('Nom d\'utilisateur ou mot de passe incorrect'))
            return self.form_invalid(form)
```

#### 3.2 Add URL Routes
```python
# administration/urls.py
urlpatterns = [
    # ... existing patterns ...
    path('agent-partenaire/login/', auth_views.AgentPartenaireLoginView.as_view(), name='agent_partenaire_login'),
    path('agent-government/login/', auth_views.AgentGovernmentLoginView.as_view(), name='agent_government_login'),
]
```

### Phase 4: QR Code Verification System

#### 4.1 Fix QR Code Verification Views
- Fix bug in `QRCodeVerifyView` and `QRCodeVerifyAPIView`
- Add proper permission checks
- Add GPS location tracking
- Add verification history

#### 4.2 Create QR Verification Dashboard
```python
# payments/views.py
class QRVerificationDashboardView(AgentGovernmentRequiredMixin, TemplateView):
    """Dashboard for government agents to verify QR codes"""
    template_name = 'payments/qr_verification_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.request.user.agent_verification
        
        # Get recent verifications
        recent_verifications = VerificationQR.objects.filter(
            agent=agent
        ).select_related('qr_code', 'qr_code__vehicule_plaque').order_by('-date_verification')[:10]
        
        # Get statistics
        today_verifications = VerificationQR.objects.filter(
            agent=agent,
            date_verification__date=timezone.now().date()
        ).count()
        
        context.update({
            'agent': agent,
            'recent_verifications': recent_verifications,
            'today_verifications': today_verifications,
        })
        return context
```

#### 4.3 Create QR Code Scanner Interface
- Mobile-friendly QR code scanner
- Real-time verification
- GPS location capture
- Photo capture (optional, for evidence)

### Phase 5: API Endpoints for Agents

#### 5.1 Agent Partenaire API
```python
# api/v1/views.py
class AgentPartenaireViewSet(viewsets.ModelViewSet):
    """API for Agent Partenaire operations"""
    permission_classes = [IsAuthenticated, IsAgentPartenaire]
    
    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """Get current agent's cash sessions"""
        agent = request.user.agent_partenaire_profile
        sessions = CashSession.objects.filter(agent=agent)
        serializer = CashSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_cash_payment(self, request):
        """Create cash payment (agent partenaire only)"""
        # Implementation
        pass
```

#### 5.2 Agent Government API
```python
# api/v1/views.py
class AgentGovernmentViewSet(viewsets.ViewSet):
    """API for Agent Gouvernement operations"""
    permission_classes = [IsAuthenticated, IsAgentGovernment]
    
    @action(detail=False, methods=['post'])
    def verify_qr_code(self, request):
        """Verify QR code (agent government only)"""
        token = request.data.get('token')
        gps_location = request.data.get('gps_location')  # Optional
        notes = request.data.get('notes')  # Optional
        
        try:
            qr_code = QRCode.objects.get(token=token)
            agent = request.user.agent_verification
            
            # Determine status
            now = timezone.now()
            if not qr_code.est_actif:
                statut = 'invalide'
            elif qr_code.date_expiration < now.date():
                statut = 'expire'
            else:
                statut = 'valide'
            
            # Create verification log
            verification = VerificationQR.objects.create(
                agent=agent,
                qr_code=qr_code,
                statut_verification=statut,
                localisation_gps=gps_location,
                notes=notes
            )
            
            # Update QR code
            qr_code.nombre_scans += 1
            qr_code.derniere_verification = now
            qr_code.save()
            
            return Response({
                'success': True,
                'verification': VerificationQRSerializer(verification).data,
                'qr_code': QRCodeSerializer(qr_code).data,
            })
        except QRCode.DoesNotExist:
            return Response({
                'success': False,
                'error': 'QR code not found'
            }, status=404)
    
    @action(detail=False, methods=['get'])
    def my_verifications(self, request):
        """Get current agent's verifications"""
        agent = request.user.agent_verification
        verifications = VerificationQR.objects.filter(agent=agent).order_by('-date_verification')
        serializer = VerificationQRSerializer(verifications, many=True)
        return Response(serializer.data)
```

#### 5.3 Add API Routes
```python
# api/v1/urls.py
router.register(r'agent-partenaire', views.AgentPartenaireViewSet, basename='agent-partenaire')
router.register(r'agent-government', views.AgentGovernmentViewSet, basename='agent-government')
```

### Phase 6: Admin Management Interface

#### 6.1 Agent Management Views
- List all agents (partenaire and government)
- Create/edit/delete agents
- Activate/deactivate agents
- View agent statistics and activity

#### 6.2 Agent Statistics
- Payments collected by agent partenaire
- QR codes verified by agent government
- Commission calculations
- Performance metrics

### Phase 7: Testing & Documentation

#### 7.1 Unit Tests
- Test agent authentication
- Test QR code verification
- Test cash payment creation
- Test permission classes
- Test API endpoints

#### 7.2 Integration Tests
- Test complete agent workflows
- Test agent interactions with users
- Test agent reporting

#### 7.3 Documentation
- API documentation for agent endpoints
- User guides for agents
- Admin guides for agent management

## Implementation Checklist

### Phase 1: Critical Bugs
- [ ] Fix QRCodeVerifyView bug (use `token` instead of `code`)
- [ ] Fix QRCodeVerifyAPIView bug
- [ ] Update URL patterns
- [ ] Test QR code verification

### Phase 2: Unified Agent System
- [ ] Create utility functions for agent checks
- [ ] Create permission classes
- [ ] Create agent mixins
- [ ] Update existing views to use new mixins

### Phase 3: Authentication
- [ ] Create AgentPartenaireLoginView
- [ ] Create AgentGovernmentLoginView
- [ ] Create login templates
- [ ] Add URL routes
- [ ] Test authentication flows

### Phase 4: QR Verification
- [ ] Create QR verification dashboard
- [ ] Create QR scanner interface
- [ ] Add GPS location tracking
- [ ] Add verification history
- [ ] Create mobile-friendly interface

### Phase 5: API Endpoints
- [ ] Create AgentPartenaireViewSet
- [ ] Create AgentGovernmentViewSet
- [ ] Create serializers
- [ ] Add API routes
- [ ] Test API endpoints

### Phase 6: Admin Interface
- [ ] Create agent management views
- [ ] Create agent statistics views
- [ ] Add agent reporting
- [ ] Test admin interface

### Phase 7: Testing & Documentation
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create API documentation
- [ ] Create user guides
- [ ] Create admin guides

## Database Changes

### No New Models Required
All necessary models already exist:
- `AgentPartenaireProfile` ✅
- `AgentVerification` ✅
- `VerificationQR` ✅
- `QRCode` ✅
- `PaiementTaxe` ✅

### Potential Migrations
- None required if using Option B (utility functions)
- If using Option A (user types), need migration to add agent types

## Security Considerations

1. **Agent Authentication**: Ensure agents can only access their designated functions
2. **QR Code Verification**: Prevent unauthorized QR code verification
3. **Cash Payment**: Ensure only authorized agents can create cash payments
4. **GPS Tracking**: Ensure GPS data is properly secured and not exposed
5. **Commission Calculations**: Ensure commission calculations are accurate and secure

## Performance Considerations

1. **QR Code Lookups**: Index on `token` field (already exists)
2. **Verification Logs**: Consider archiving old verification logs
3. **Agent Statistics**: Cache frequently accessed statistics
4. **API Rate Limiting**: Apply rate limiting to agent API endpoints

## Future Enhancements

1. **Mobile App**: Native mobile app for agents
2. **Offline Mode**: Support for offline QR code verification
3. **Biometric Authentication**: Add fingerprint/face recognition for agents
4. **Multi-language Support**: Support for multiple languages in agent interfaces
5. **Advanced Analytics**: Advanced analytics and reporting for agents
6. **Commission Automation**: Automated commission calculation and payment
7. **Agent Training**: In-app training and certification for agents

## Conclusion

This plan provides a comprehensive solution for managing two types of agents in the Tax Collector system. The implementation is divided into phases to allow for incremental development and testing. The solution leverages existing models and adds the necessary utilities, permissions, and interfaces to support both agent types effectively.

## Financial Projection

### Assumptions
- Target workload: `X` cash payments/day, `Y` QR verifications/day, `Z` active agents
- Average cash payment amount: `A` (local currency)
- Agent commission rate: `r%` (configurable per agent)
- System transaction fee (if applicable): `f%` per payment
- Cloud region and pricing may vary; values below are indicative

### Revenue Model (example)
- Commission revenue per month:
  - `monthly_payments = X * 30`
  - `commission_revenue = monthly_payments * A * (r / 100)`
- Transaction fee revenue (optional):
  - `fee_revenue = monthly_payments * A * (f / 100)`
- Total monthly revenue: `total_revenue = commission_revenue + fee_revenue`

### Operating Costs (monthly, indicative)
- Application servers: 2× `t3.medium`-equivalent (2 vCPU, 4–8 GB RAM)
- Database: Managed PostgreSQL `db.t3.medium`-equivalent
- Cache/Queue: Managed Redis (or single small node)
- Object storage: S3 or MinIO (depending on deployment)
- Networking: Load balancer, bandwidth, DNS
- Observability: Logging, metrics, error monitoring (Sentry)
- CI/CD: Build minutes and artifacts storage

Example cost ranges (cloud, per month; adjust by provider/region):
- App servers: `~$60–$120` (two nodes)
- Managed PostgreSQL: `~$50–$150`
- Managed Redis: `~$15–$60`
- Object storage: `~$5–$30` (depends on volume)
- Load balancer + bandwidth: `~$20–$80`
- Monitoring/alerts: `~$0–$50`
- Total infra estimate: `~$150–$490` per month

### Net Projection (example)
- `net = total_revenue − total_infra_cost − other_ops_costs`
- Sensitivity analysis: vary `X, A, r, f` to produce low/base/high scenarios

### Notes
- For on‑prem deployments, replace cloud line items with server amortization, power, and connectivity.
- Consider reserved instances or savings plans to reduce compute/DB costs for stable workloads.

## Server Infrastructure & Deployment

### Architecture Overview
- Web tier: `Django + Gunicorn` behind `Nginx` (reverse proxy/SSL)
- Data tier: `PostgreSQL` (transactions, reporting); regular backups and PITR
- Cache/queue: `Redis` for caching, sessions, and Celery broker
- Background workers: `Celery` for async jobs (notifications, OCR, reports)
- Storage: Object storage for documents/QR exports (`S3` or `MinIO`)
- Observability: Centralized logs, metrics (Prometheus/Grafana or hosted), error tracking (Sentry)

### Capacity & Sizing (initial)
- App servers: 2× `2 vCPU / 4–8 GB RAM` for redundancy and rolling deploys
- Database: `4 vCPU / 8–16 GB RAM`, fast SSD storage, `~100–500 GB` as starting point
- Redis: small node with persistence off for cache-only, on for queue if needed
- Expected throughput: comfortably supports `~50–150 req/sec` with proper caching

### Scaling Strategy
- Horizontal scale app tier (`N+1` nodes) via autoscaling
- Read replicas for PostgreSQL (analytics/reporting) if needed
- Redis clustering or dedicated queue (e.g., RabbitMQ) for high-volume tasks
- CDN for static assets to offload bandwidth

### Deployment Options
- Docker Compose for local/dev (already present)
- Production: Docker with:
  - Option A: Managed DB + single LB + autoscaled app nodes
  - Option B: Kubernetes (EKS/GKE) when team/scale justify it
- Secrets via environment variables or secret manager (AWS SSM/Secrets Manager)

### Resilience & Operations
- Availability target: `99.9%`+ (redundant app tier, managed DB)
- Backups: daily snapshots, weekly retention, tested restores
- Security: TLS everywhere, least-privilege IAM, regular patching
- Incident response: alerts on error rates, latency, resource exhaustion

### Monitoring & Alerts
- Metrics: request rate, latency (p95/p99), error rate, DB connections, cache hit rate
- Logs: structured app logs with correlation IDs
- Alerts: on SLO breaches, job failures, queue backlog, disk usage

## Action Items to Finalize These Sections
- Fill real values for `X, Y, Z, A, r, f` and local currency
- Choose cloud vs. on‑prem and update cost lines accordingly
- Confirm production deployment path (managed DB vs. self‑hosted, Kubernetes vs. VM)
- Define backup RPO/RTO and verify restore drills quarterly

