## Objectives
- Add a government-only module for contravention management: record, view, process.
- Enforce role-based access for government departments and permissions.
- Implement offender verification, secure auth, audit logging, and data retention.
- Maintain existing UX patterns, framework, and testing standards.

## Architecture Fit
- Use current providers and navigator wired in `App.tsx` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/App.tsx:10).
- Integrate screens via the existing stack/tab setup in `AppNavigator` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/navigation/AppNavigator.tsx:69–97, 117–143) with the auth gate at (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/navigation/AppNavigator.tsx:101–106).
- Leverage `AuthContext` for auth state and permissions (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/context/AuthContext.tsx:111–140) and `storageService` for secure tokens (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/services/storageService.ts:10–33, 227–242).
- Reuse `apiService` for network calls and token refresh handling (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/services/apiService.ts:34–53, 55–106, 232–251).

## UI (Government Screens)
- Add screens under `src/screens/`:
  - `ContraventionListScreen` (search/filter, list view, government-only).
  - `ContraventionFormScreen` (record contravention: offense details, location, timestamp, evidence attach).
  - `ContraventionDetailScreen` (view/process: update status, add notes, view evidence).
- Gate screens by role/permission using `useAuth()` checks (`AgentType.GOVERNMENT` or `hasPermission`) consistent with existing gating in `ScannerScreen` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/screens/ScannerScreen.tsx:119–125).
- Follow StyleSheet-based design, Ionicons, cards/modals/status coloring established across screens.

## Data Model
- Create `src/types/contravention.types.ts`:
  - `Contravention`: id, offenderId, offenseDetails, location (lat/lng/address), timestamp, status, evidence[], createdBy, department.
  - `Evidence`: id, type (photo/video/doc), uri, hash, size, metadata.
  - `ContraventionStatus`: enum (Draft, Issued, Paid, Disputed, Voided).
- Extend auth permissions: add `issue_contravention`, `view_contraventions`, `process_contraventions` in `AgentPermissions` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/types/auth.types.ts:33–51).
- Optionally extend scanner types where relevant (e.g., `ScanRecord` with `contraventionIssued?: boolean`) in `src/types/scanner.types.ts`.

## Services & API
- Add `src/services/contraventionService.ts` using `apiService` patterns (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/services/apiService.ts:108–204):
  - `listContraventions(params)` with paging/search/filter.
  - `getContravention(id)`.
  - `createContravention(payload)` uploads metadata; evidence uploaded via `uploadEvidence(contraventionId, file)`.
  - `updateContravention(id, updates)` and `voidContravention(id, reason)`.
  - `verifyOffender(identifier)` integrates with government DB.
- Add endpoints under `API_ENDPOINTS.GOVERNMENT_AGENT.*` in `src/constants/api.constants.ts` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/constants/api.constants.ts:1–26) such as:
  - `CONTRAVENTIONS_LIST`, `CONTRAVENTIONS_DETAIL`, `CONTRAVENTIONS_CREATE`, `CONTRAVENTIONS_UPDATE`, `CONTRAVENTIONS_VOID`, `EVIDENCE_UPLOAD`, `OFFENDER_VERIFY`.
- Location capture via existing `expo-location` dependency; evidence handling via `expo-file-system` and platform pickers (photo/video) aligned with Expo.
- Offline-first notes: queue create/update/void actions if offline using a similar pattern to `scannerService` offline queue (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/services/scannerService.ts:220–267, 302–335).

## Authentication & RBAC
- Continue using `AuthContext` login/logout and token storage (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/context/AuthContext.tsx:64–94, 96–109; /Users/samoela/Projet/taxcollecotr/scan-agent-app/src/services/storageService.ts:10–33).
- Enforce department-specific access by extending `Agent` profile to include `department` and mapping permissions per department in `AuthContext.canAccessFeature` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/context/AuthContext.tsx:120–140).
- Guard endpoints via `authService.canAccessEndpoint` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/services/authService.ts:128–147).

## Security & Compliance
- Encryption in transit: HTTPS via `API_BASE_URL` and Axios; no plain HTTP in production (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/constants/api.constants.ts:1).
- Sensitive at-rest data:
  - Tokens/profile remain in `SecureStore` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/services/storageService.ts:10–33).
  - Avoid storing evidence locally; upload immediately and store only secure remote references.
  - If temporary local caching is needed, store non-sensitive metadata in `AsyncStorage` and purge per retention policy.
- Audit logging:
  - Add `src/services/auditService.ts` with `logAction(type, actor, resourceId, details)` sending to backend; buffer offline and sync later.
  - Log create/update/void/evidence-upload, including timestamps, agent id, department, device info from headers (`apiService` adds headers at /Users/samoela/Projet/taxcollecotr/scan-agent-app/src/services/apiService.ts:44–47).
- Data retention:
  - Implement scheduled purge of cached contravention metadata older than policy (e.g., 24–72h) via `storageService` keys and timestamps.
  - Rely on server-side retention for records; client keeps minimal local footprint.

## Navigation
- Add a government-only tab "Contraventions" with `ContraventionListScreen` and a stack route to `ContraventionDetailScreen`.
- Add a floating action in list to open `ContraventionFormScreen`.
- Register routes in `MainTabNavigator` and `RootStack` (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/navigation/AppNavigator.tsx:69–97, 126–143) and conditionally include based on `AgentType.GOVERNMENT`.

## Search & Filtering
- Server-side filtering via query params: date range, status, department, offenderId.
- Client-side quick filter (status chips) and search bar with debounce.

## Testing
- Extend unit tests under `__tests__/`:
  - `contravention.validators.test.ts` for form field validation using `utils/validators`.
  - `contravention.service.test.ts` mocking `apiService` responses and error paths.
  - `auth.permissions.test.ts` for new permission mapping in `AuthContext`.
  - `audit.service.test.ts` to ensure buffered logging and sync behavior.
- Reuse jest setup (`jest.config.js`:1–6, `jest.setup.js`:1–10) and TypeScript types.

## Internationalization
- Add keys to `utils/translations.ts` for government module labels, statuses, errors, and success messages (/Users/samoela/Projet/taxcollecotr/scan-agent-app/src/utils/translations.ts:151–168).

## Implementation Milestones
1) Types & Constants
- Add `contravention.types.ts`; extend `auth.types.ts` permissions and (optionally) `Agent.department`.
- Add API endpoint constants.

2) Services
- Implement `contraventionService` methods and evidence upload.
- Implement `auditService` with offline buffer and sync.

3) Auth & RBAC
- Extend `AuthContext` permission mapping; gate endpoints and screens.

4) UI Screens
- Build list, detail, and form screens; integrate location capture and evidence attachment.
- Add search and filter UI with server-side params.

5) Navigation
- Register routes; conditionally show tab for government agents.

6) Security & Retention
- Ensure immediate evidence upload and minimal local storage; add purge job.

7) Testing & i18n
- Add unit tests; update translations; run and fix coverage.

## Deliverables
- New screens: `ContraventionList`, `ContraventionForm`, `ContraventionDetail`.
- New types and services: `contravention.types.ts`, `contraventionService.ts`, `auditService.ts` with endpoints.
- Updated auth permissions and guarded navigation.
- Unit tests for validators/services/RBAC/audit.
- Translations for all new UI strings.
- Documented retention configuration in code comments and consts.