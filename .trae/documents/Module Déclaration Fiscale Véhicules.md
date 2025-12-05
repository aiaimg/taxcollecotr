## Current Status

* Data models implemented: `TypeInfraction`, `AgentControleurProfile`, `Conducteur`, `Contravention`, `DossierFourriere`, `PhotoContravention`, `Contestation`, `ContraventionAuditLog`, `ConfigurationSysteme` (contraventions/models.py:18, 147, 217, 277, 516, 676, 775, 913, 1028).

* Business services complete: creation, recidive detection, amount calculation, QR code, audit, cancellation, unpaid queries (contraventions/services/contravention\_service.py:28, 136, 246, 266, 354, 507); fourrière lifecycle (contraventions/services/fourriere\_service.py:24); contestation lifecycle (contraventions/services/contestation\_service.py:27, 150); payments MVola/Stripe/Cash with receipts and notifications (contraventions/services/paiement\_amende\_service.py:31, 148, 272, 421).

* Web views built for agents, public and admin with templates and static assets (contraventions/views.py:37, 59, 97, 124, 172, 221, 250, 268, 325, 341; templates/contraventions/\*).

* Admin registration and dashboards implemented (contraventions/admin.py:65, 162, 199, 219, 246, 266).

* Tests exist for cancellation logic and unpaid retrieval (contraventions/tests.py:24, 214).

* Routing wired under `contraventions/` and `api/contraventions/` (taxcollector\_project/urls.py:34, 40).

## Gaps and Issues

* Serializers mismatch models (extra/missing fields; wrong relation names) (contraventions/serializers.py:10–78, 81–129, 131–168). Example: `TypeInfractionSerializer` references `description` which doesn't exist (models). `hasattr(obj, 'dossierfourriere')` should be `dossier_fourriere` (serializers.py:101 vs models).

* API views use inconsistent field names/statuses and stub payment handlers (contraventions/api\_views.py:23–47, 98–165, 254–293). Example: filters `date_infraction`/status `active`/`paid` vs model `date_heure_infraction`/`IMPAYEE`/`PAYEE`.

* QR verification uses `generate_qr_code_data()` which doesn't exist on `Contravention` (contraventions/serializers.py:196–216). Should verify via `payments.QRCode` data.

* Missing AJAX endpoints used by UI: `ajax_get_infraction_details`, `ajax_check_recidive` referenced in templates/JS but not defined in `urls.py` (templates/contraventions/contravention\_form.html:430, 460; contraventions/urls.py:28–32; views only define `search_*`, `check_recidive` without URL wiring).

* Public URL parameter mismatch: `urls.py` uses `numero_contravention` but view expects `numero_pv` (contraventions/urls.py:18–20 vs contraventions/views.py:226).

* Payment API should call `PaiementAmendeService` instead of returning canned responses (contraventions/api\_views.py:136–165; services exist at paiement\_amende\_service.py).

* Stats endpoints in API compute with wrong fields/statuses (contraventions/api\_views.py:260–283).

* API search endpoints reference non-existent model fields (`Vehicule.numero_plaque`, `Conducteur.prenom/email`) (contraventions/api\_views.py:311–319, 337–348).

## Plan

### 1) Serializer Alignment

* Rewrite serializers to match actual model fields and relations.

* Fix `ContraventionListSerializer`/`ContraventionDetailSerializer` relation names and computed fields.

### 2) API View Fixes

* Update filters and field names to model schema (`date_heure_infraction`, `statut` in `IMPAYEE|PAYEE|CONTESTEE|ANNULEE`).

* Replace stub payment handlers with calls to `PaiementAmendeService` methods; update `Contravention.statut` and audit logs.

* Fix vehicle/driver search to use `Vehicule.plaque_immatriculation`/`numero_chassis` and `Conducteur.nom_complet`/`cin`/`numero_permis`.

### 3) QR Verification

* Implement QR verification using `payments.QRCode` associated to `Contravention` and remove `generate_qr_code_data()` reference.

### 4) UI AJAX Endpoints

* Add `ajax/get-infraction-details` and `ajax/check-recidive` routes in `contraventions/urls.py` and wire to view functions that return the JSON the templates/JS expect.

### 5) URLs and Routing

* Align public routes to use `numero_pv` consistently; update `urls.py` parameters to match view `slug_url_kwarg`.

* Remove duplicated JWT endpoints from `contraventions/api_urls.py` if already provided globally.

### 6) Tests

* Add API tests for list/detail/create/payment/QR verification and for the new AJAX endpoints.

* Extend service tests for payment confirmations and fourrière release gating.

### 7) Documentation/Config

* Document status fields and API contracts in `API_DOCUMENTATION.md` section for contraventions.

* Ensure `ConfigurationSysteme` seeding in fixtures/migrations for defaults.

### 8) Verification

* Run unit tests; smoke test web views; validate API via Swagger (`/api/schema/swagger-ui/`).

* Verify the agent form page now populates amounts and recidive info via AJAX correctly and payments update statuses.

