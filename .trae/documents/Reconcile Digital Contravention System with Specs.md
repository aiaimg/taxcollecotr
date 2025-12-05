## Current Status vs Specs
- App structure: Present (`contraventions/` with models, views, api_views, forms, services, admin, urls, api_urls, tasks, migrations). Templates exist under `templates/contraventions/`, not in `contraventions/templates/contraventions/` as the spec assumes.
- Models: Fully implemented per spec in `contraventions/models.py` (e.g., `Contravention` at contraventions/models.py:277; methods at contraventions/models.py:454, 472, 478, 482, 491). `PaiementTaxe` integrates contraventions in `payments/models.py:13,18,45`.
- Services: Implemented in `contraventions/services/*` (creation, recidive detection, fourrière, payments, contestations).
- Forms: Implemented in `contraventions/forms.py` with validation and service delegation (authority filtering minimal; see init at contraventions/forms.py:46–60).
- Views: Implemented for agent, public, admin in `contraventions/views.py` (e.g., class definitions at views.py:37, 59, 97, 221, 250, 325, 341, 393). One AJAX bug: `search_vehicle` uses a wrong model name at contraventions/views.py:428.
- URLs: Web routes in `contraventions/urls.py`; public routes use `numero_contravention` which mismatches `Contravention.slug` usage of `numero_pv` in views (urls.py:18–19 vs views.py:226–257). Project router includes web routes but not API routes.
- API & Serializers: Endpoints defined in `contraventions/api_urls.py` but fields/params mismatch models (e.g., `numero_contravention`, `date_infraction`, `montant_total_ariary` in `contraventions/serializers.py:92–95, 117–122, 218` vs model fields).
- Templates: Present in `templates/contraventions/` including agent, public, admin, and partials. One mismatch: view expects `contraventions/public_detail.html` (views.py:224) while file is `templates/contraventions/contravention_public_detail.html`.
- Celery: Tasks implemented (`contraventions/tasks.py`) but field names mismatch models (e.g., `numero_contravention`, `date_echeance`, `montant_total_ariary` at tasks.py:39–66). Celery Beat schedule missing in settings.
- JWT: Configured in `taxcollector_project/settings.py:288–321` and `401–417`; token endpoints exist in `contraventions/api_urls.py:9–10`.
- Project URLs: Missing inclusion of `contraventions.api_urls` (no match in `taxcollector_project/urls.py`; see include lines at taxcollector_project/urls.py:25–41).
- Tests: Minimal (`contraventions/tests.py` exists) but not the full suite proposed in specs.

## Proposed Fix Plan
### 1. Align Field Names Across API/Serializers/Tasks/URLs
- Update `contraventions/serializers.py` to use model-compliant fields:
  - `numero_contravention` → `numero_pv` (e.g., at serializers.py:92, 117, 218)
  - `date_infraction` → `date_heure_infraction`
  - `montant_total_ariary` → serializer method calling `obj.get_montant_total()`
  - `agent` → `agent_controleur`
- Update `contraventions/api_urls.py` and `contraventions/urls.py` route params to use `numero_pv` consistently; remove/replace duplicate web "api" routes with DRF endpoints.
- Fix Celery tasks to reference correct fields: `numero_pv`, `date_limite_paiement`, and `get_montant_total()` in `contraventions/tasks.py` (e.g., tasks.py:39–66, 191–199).

### 2. Fix AJAX Vehicle Search
- Correct `search_vehicle` to use `vehicles.Vehicule` and remove `VaiementTaxe` typo at `contraventions/views.py:428`.
- Ensure JS expects parameters matching the view (`plaque` and `cin`) and that responses map to UI (`static/js/contraventions.js`).

### 3. Template Name Alignment
- Update `ContraventionPublicDetailView.template_name` to `contraventions/contravention_public_detail.html` (views.py:224) or rename the template to match the view.
- Verify all other template names used in views exist and load required assets (`contraventions.css`, `contraventions.js`).

### 4. Router Inclusion
- Add `path('api/contraventions/', include('contraventions.api_urls'))` in `taxcollector_project/urls.py` (next to existing `api/` inclusions).

### 5. Celery Beat Configuration
- Add `CELERY_BEAT_SCHEDULE` in `taxcollector_project/settings.py` for payment reminders, fourrière processing, contestation reminders, and daily reports per spec.

### 6. Management Commands
- Implement missing commands under `contraventions/management/commands/`:
  - `setup_contravention_permissions.py`
  - `calculate_penalties.py`
  - `generate_daily_report.py`

### 7. Tests
- Add focused tests:
  - Models: numero PV generation, delay calculation, penalty computation
  - Services: create/recidive/annulation flows
  - API: CRUD endpoints with JWT
  - Views: public detail without auth, agent views permissions

### 8. Verification Pass
- Run URLs and API checks (ensure endpoints resolve and return expected payloads).
- Render views using existing templates; exercise JS interactions for search and payment selection.
- Validate Celery schedules load and tasks run in a sandbox.

If you approve, I will execute this plan, updating the mismatches, wiring the API URLs, configuring Celery Beat, adding the missing commands, and writing minimal tests to lock correctness.