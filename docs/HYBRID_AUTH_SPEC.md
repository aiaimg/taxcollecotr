# Hybrid Authentication: Classic + OTP (with Badge for Government)

## Summary
- Offer two authentication modes side-by-side: Classic (email/password or badge+PIN) and OTP by phone.
- Keep a second-step badge verification for Government Scan Agents when using OTP, and optionally enforce badge for classic login too.
- Reuse platform-agnostic backend endpoints so both mobile and web can implement the same flows.

## Goals
- Flexible login that fits both Partner Collectors (no badge) and Government Agents (badge-based identity).
- Minimal disruption to existing classic auth (`/api/v1/auth/login`).
- Strong security with rate limiting, hashed OTPs, and scoped intermediate tokens.

## Roles
- Government Scan Agent (`agent_government`): may require badge verification depending on chosen mode/policy.
- Partner Collector (`agent_partenaire`): can use classic or OTP; no badge required.

## Modes & Policies
- Classic mode
  - Partner: `email + password` (existing) → issue JWT.
  - Government: choose one of:
    1) `email + password` → issue JWT (simplest), or
    2) `badge + PIN` → dedicated endpoint → issue JWT, or
    3) `email + password` plus a second-step `badge` verification for elevated actions (optional policy).
- OTP mode
  - Partner: `phone → OTP` → issue JWT.
  - Government: `phone → OTP` → returns `requires_badge = true` with `intermediate_token` → `badge` verification → issue JWT.

## Backend Endpoints
All under `api/v1`.

- Classic (existing)
  - `POST /api/v1/auth/login`
    - Body: `{ "email": "user@example.com", "password": "secret" }`
    - Response: `{ success, data: { access, refresh, user } }`

- Classic (government badge+PIN, optional)
  - `POST /api/v1/agent-government/login-badge`
    - Body: `{ "badge_id": "AG7552", "pin": "1234" }`
    - Behavior: validate `AgentVerification.numero_badge` and hashed PIN; issue JWT.

- OTP (shared)
  - `POST /api/v1/auth/request-otp`
    - Body: `{ "phone": "+261xxxxxxxxx" }`
    - Behavior: rate-limit, create hashed OTP, send SMS, cooldown.
  - `POST /api/v1/auth/verify-otp`
    - Body: `{ "phone": "+261…", "otp": "123456" }`
    - Behavior:
      - Resolve `User` by `UserProfile.telephone`.
      - If Partner: issue JWT; return `agent_partenaire` + permissions.
      - If Government: return `{ requires_badge: true, intermediate_token }`.
  - `POST /api/v1/agent-government/verify-badge`
    - Body: `{ "badge_id": "AG7552", "intermediate_token": "<token>" }`
    - Behavior: validate scoped, short-lived token bound to user/phone; verify badge; issue JWT.

## Mobile UI
- LoginScreen: mode selector (tabs or segmented control): `OTP` and `Classique`.
- OTP tab
  - Step 1: input `Téléphone (+261…)` → `Envoyer OTP` with resend countdown.
  - Step 2: input `Code OTP` → `Se connecter`.
  - If response `requires_badge`: show `Numéro de badge` form and submit with `intermediate_token`.
- Classic tab
  - Role toggle: `Agent Gouvernement` vs `Agent Partenaire`.
  - Partner: `Email` + `Mot de passe` → `/auth/login`.
  - Government: choose policy:
    - `Email` + `Mot de passe` → `/auth/login`, or
    - `Badge` + `PIN` → `/agent-government/login-badge`.
- After login: set `AgentType` and load permitted features (scanning vs payment/session).

## Web UI (Server-rendered or SPA)
- Reuse the same endpoints.
- Server-rendered Django:
  - Add views: `RequestOTPView`, `VerifyOTPView`, `VerifyBadgeView`, optional `LoginBadgeView`.
  - Templates mirror mobile steps; create Django session on success.
- SPA:
  - Call endpoints directly; manage `access/refresh` tokens (prefer `httpOnly` cookies or memory), mirror mobile two-step flow.

## Data Model & Security
- `LoginOTP` storage (DB or Redis): `phone`, `otp_hash`, `expires_at` (~5 mins), `attempts`, `last_sent_at`, `user_id`.
- Intermediate token for government OTP: short-lived (5–10 mins), scoped claim `scope=badge_verification`, bound to `user_id` + `phone`, single-use.
- Hash OTPs; secure comparison; throttle via `AuthThrottle`.
- Optional policy: enforce badge verification even after classic login for government (e.g., before scanning actions).

## Error Handling
- `validation_error`: bad input.
- `otp_invalid`, `otp_expired`, `otp_rate_limited`.
- `badge_invalid`, `token_invalid`.
- Standard JWT errors from existing flow (`token_invalid`, `authentication_failed`).

## Configuration Flags
- `AUTH_ENABLE_CLASSIC=true/false`.
- `AUTH_ENABLE_OTP=true/false`.
- `AUTH_GOVERNMENT_REQUIRE_BADGE_ON_OTP=true` (default true).
- `AUTH_GOVERNMENT_REQUIRE_BADGE_ON_CLASSIC=false/true` (optional).
- SMS provider configs via `ConfigurationSysteme`.

## Implementation Plan
- Backend
  1) Implement OTP endpoints and intermediate token issuance.
  2) Add `login-badge` endpoint (optional) with PIN hashing.
  3) Add throttling, resend cooldown, and logging.
  4) Expose config flags.
- Mobile
  1) Add mode selector and role toggle.
  2) Implement OTP steps and badge verification.
  3) Implement classic flows (email/password; badge+PIN optional).
  4) Persist tokens; set `AgentType`; gate features by permissions.
- Web
  1) Add views/templates or SPA components mirroring mobile.
  2) Session or token management.

## Testing & Monitoring
- Unit tests: OTP gen/validate, cooldown, badge verify, PIN hashing.
- Integration: full Partner and Government flows across both modes.
- Metrics: OTP request/verify rates, badge failures, throttle hits.
- Alerts for spikes in invalid OTPs or login failures.

## Example Payloads
- Classic (Partner)
  ```json
  POST /api/v1/auth/login
  { "email": "collector@example.com", "password": "s3curePass!" }
  ```
- Classic (Government badge+PIN)
  ```json
  POST /api/v1/agent-government/login-badge
  { "badge_id": "AG7552", "pin": "1234" }
  ```
- OTP (request)
  ```json
  POST /api/v1/auth/request-otp
  { "phone": "+261345678901" }
  ```
- OTP (verify partner)
  ```json
  POST /api/v1/auth/verify-otp
  { "phone": "+261345678901", "otp": "123456" }
  ```
- OTP (verify government badge)
  ```json
  POST /api/v1/agent-government/verify-badge
  { "badge_id": "AG7552", "intermediate_token": "<token>" }
  ```