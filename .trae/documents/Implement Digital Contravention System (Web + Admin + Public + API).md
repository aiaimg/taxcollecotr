## Current State Summary

* App `contraventions` is installed with core models, migrations and business services implemented.

* `urls.py` and `views.py` are placeholders; admin is not configured; templates/JS/CSS and API endpoints are not present.

* Forms have been introduced for contraventions, contestations and admin models.

## Goals

* Deliver a working end-to-end contravention system: creation by agents, public viewing via QR, payments, contestations, fourrière flows, admin management, REST API, scheduled jobs, and tests.

## Phase 1: Admin & Configuration

1. Register all models in Django admin with robust `ModelAdmin` configuration.
2. Use admin forms for TypeInfraction, ConfigurationSysteme and DossierFourriere.
3. Add inlines (photos, contestations, audit logs) and filters/search.
4. Define granular permissions and groups aligned with roles (agent, supervisor, admin).

## Phase 2: Web (Agent) Views & URLs

1. `ContraventionCreateView` (form-based) that delegates to `ContraventionService.creer_contravention`.
2. `ContraventionListView` with pagination, filters and restricted to logged-in agent’s scope.
3. `ContraventionDetailView` showing photos, audit history, actions (cancel within rules).
4. Fourrière views: create, detail (fees calculation), restitution (QR-enabled receipt).
5. Add AJAX endpoints for vehicle/driver live search and dynamic amount calculation.
6. Wire URLs in `contraventions/urls.py` and include them in project `urls.py`.

## Phase 3: Public Views (QR / Payment / Contestation)

1. `ContraventionPublicDetailView` accessible via PV number or QR token, shows status and payable amount including penalties.
2. `ContraventionPaymentView` routing to MVola/Stripe/Cash via `PaiementAmendeService` with callbacks and receipt.
3. `ContestationPublicView` to submit contestations with multiple document uploads.
4. Public URLs without auth but rate-limited and secured.

## Phase 4: Templates, JS, CSS

1. Agent templates: form, list, detail, fourrière.
2. Public templates: detail, payment select/success, contestation form.
3. Admin templates (optional custom dashboards as needed).
4. JS: `contravention-form.js` (AJAX live search, amount calc, validation), `photo-upload.js`, `signature-pad.js`, `payment-integration.js`.
5. CSS: scoped styles for contraventions and components, aligned with Velzon theme.

## Phase 5: REST API (DRF)

1. Serializers: TypeInfraction, Contravention (nested), Conducteur, PhotoContravention.
2. CRUD endpoints for contraventions with filters; search endpoints for vehicle, driver, infractions, recidive.
3. Photo upload/delete endpoints.
4. Offline sync endpoints and JWT auth integration.

## Phase 6: Commands & Scheduled Tasks

1. Management command `setup_contravention_permissions` for groups/permissions.
2. Management command `calculate_penalties` to apply daily late fees and log.
3. Celery tasks: `calculer_penalites_retard`, `envoyer_rappels_paiement`, `generer_rapport_quotidien` with Celery Beat schedule.

## Phase 7: Routing & Integration

1. Configure app URLs (agent, public, admin) and API URLs.
2. Connect QRCode data to public verification routes.
3. Ensure `PaiementTaxe` linkages are consistent and update flows on payment confirmation.

## Phase 8: Testing

1. Unit tests for models (amount calc, PV generation, recidive, fourrière fees, audit hash).
2. Service tests for creation/recidive/import/payment confirmation/contestation lifecycle.
3. Form tests for validations (CIN, clean logic).
4. View tests for agent create/list/detail, public detail, API with JWT.
5. Integration tests across creation → payment → receipt; and creation → fourrière → restitution.

## Phase 9: Security & Compliance

1. Enforce permissions at views and API; audit every sensitive action.
2. Rate-limit public endpoints; validate inputs and sanitize uploads.
3. No secrets in code; rely on env; adhere to logging policy.

## Delivery Plan (Implementation Order)

1. Admin registration + permissions.
2. Agent views + URLs + templates.
3. Public views + payment flow.
4. API serializers/endpoints + JWT.
5. Commands + Celery Beat.
6. JS/CSS enhancements.
7. Comprehensive tests.

## Acceptance Criteria

* Agents can create, list and view contraventions with business rules enforced.

* Public can view contraventions via QR and pay; receipts generated.

* Contestations can be submitted and adjudicated; delays suspended/resumed accordingly.

* Fourrière flows compute fees and allow restitution under rules.

* Admin has full management capabilities with audit logging.

* API provides CRUD/search/sync with JWT; scheduled tasks run daily.

## Notes

* All commands and server runs will be executed within the project’s Python virtual environment.

* We will reuse existing services to avoid duplicating logic and ensure consistency.

* We will follow Velzon UI conventions and existing security practices.

