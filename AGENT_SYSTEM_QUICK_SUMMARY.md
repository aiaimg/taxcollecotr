# Agent System - Quick Summary

## Current State

### ✅ What Exists

1. **AgentPartenaireProfile** (payments/models.py)
   - For partner agents who collect cash payments
   - Has commission tracking, collection locations
   - Used in cash payment system

2. **AgentVerification** (administration/models.py)
   - For government agents who verify QR codes
   - Has badge numbers, zones
   - Logs verifications in VerificationQR model

3. **QRCode Model** (payments/models.py)
   - Uses `token` field (not `code`)
   - Tracks scans, expiration, status

### ❌ Issues Found

1. **BUG**: QRCodeVerifyView uses `code=code` but should use `token=code`
2. **Missing**: Unified agent authentication/authorization
3. **Missing**: API endpoints for agent operations
4. **Missing**: Agent-specific login views
5. **Missing**: QR verification dashboard for government agents

## Proposed Solution

### Phase 1: Fix Critical Bug (URGENT)
- Fix QRCodeVerifyView to use `token` instead of `code`
- Fix QRCodeVerifyAPIView
- Update URL patterns

### Phase 2: Unified Agent System
- Create utility functions: `is_agent_partenaire()`, `is_agent_government()`
- Create permission classes for API
- Create mixins for views

### Phase 3: Agent Authentication
- Create AgentPartenaireLoginView
- Create AgentGovernmentLoginView
- Create login templates

### Phase 4: QR Verification System
- Create QR verification dashboard
- Create mobile-friendly QR scanner
- Add GPS tracking

### Phase 5: API Endpoints
- AgentPartenaireViewSet (cash payments, sessions)
- AgentGovernmentViewSet (QR verification)

### Phase 6: Admin Interface
- Agent management views
- Agent statistics and reporting

### Phase 7: Testing & Documentation
- Unit tests
- Integration tests
- API documentation

## Key Decisions

### Agent Type Identification
**Recommended**: Keep profiles separate, add utility functions
- More flexible
- No database migration needed
- Allows future expansion

### Authentication Flow
- Separate login views for each agent type
- Redirect to appropriate dashboard after login
- Clear error messages for unauthorized access

### API Design
- RESTful endpoints for agent operations
- Proper permission classes
- Comprehensive serializers

## Implementation Priority

1. **HIGH**: Fix QR code verification bug
2. **HIGH**: Create agent authentication
3. **MEDIUM**: Create API endpoints
4. **MEDIUM**: Create QR verification dashboard
5. **LOW**: Admin interface enhancements
6. **LOW**: Advanced features

## Files to Modify

### Core Changes
- `payments/views.py` (fix QR verification bug)
- `payments/urls.py` (update URL patterns)
- `administration/auth_views.py` (add agent login views)
- `administration/mixins.py` (add agent mixins)
- `administration/permissions.py` (NEW - create permission classes)
- `core/utils.py` (NEW - add agent utility functions)

### API Changes
- `api/v1/views.py` (add agent viewsets)
- `api/v1/serializers.py` (add agent serializers)
- `api/v1/urls.py` (add agent routes)

### Templates
- `templates/administration/auth/agent_partenaire_login.html` (NEW)
- `templates/administration/auth/agent_government_login.html` (NEW)
- `templates/payments/qr_verification_dashboard.html` (NEW)

## Next Steps

1. Review this plan
2. Approve implementation approach
3. Start with Phase 1 (fix critical bug)
4. Iterate through phases
5. Test thoroughly
6. Deploy incrementally

## Questions to Consider

1. Should agents have separate user types or use profiles?
2. Should agents be able to access both systems?
3. What level of GPS tracking is needed?
4. Should there be commission automation?
5. Do we need a mobile app for agents?

