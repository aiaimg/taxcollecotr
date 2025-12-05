# OTP + Badge Verification Authentication (Spec)

## Summary
- Unify authentication with phone-based OTP for all users.
- Require a second‑factor badge verification for Government Scan Agents only.
- Keep role-based permissions intact post-login.

## Goals
- Simple UX: login by phone for everyone; extra badge step only for government.
- Secure: hash OTPs, short TTL, rate limiting, and intermediate token for badge step.
- Compatible with current Django API structure (`api/v1`) and mobile app.

## Roles
- Government Scan Agent (`AgentType.GOVERNMENT`): must verify badge after OTP.
- Partner Collector (`AgentType.PARTENAIRE`): OTP only, no badge required.

## User Experience Flow
1. Request OTP
   - User enters phone (`+261…`) and taps “Envoyer OTP”.
   - System sends a 6‑digit OTP via SMS.
2. Verify OTP
   - User enters the 6‑digit code and taps “Se connecter”.
   - If user is a Partner Collector → issue JWT and complete login.
   - If user is a Government Agent → return `requires_badge = true` and a short‑lived `intermediate_token`.
3. Verify Badge (Government only)
   - App prompts for `Numéro de badge`.
   - App calls badge verification with the `intermediate_token`.
   - If badge is valid → issue full JWT (access + refresh), return agent profile and permissions.

## API Design
All endpoints are under `api/v1`.

### 1) POST `/api/v1/auth/request-otp`
- Body: `{ "phone": "+261xxxxxxxxx" }`
- Behavior:
  - Validate phone format (`UserProfile.telephone` matches).
  - Create an OTP entry: `otp_hash`, `expires_at` (+5 min), `attempts = 0`, `last_sent_at`.
  - Enforce resend cooldown (e.g., 60–90s), throttle per phone.
  - Send SMS: "Votre code de connexion est: 123456. Expire dans 5 minutes."
- Response: `{ "success": true }`

### 2) POST `/api/v1/auth/verify-otp`
- Body: `{ "phone": "+261…", "otp": "123456" }`
- Behavior:
  - Validate and consume OTP (increment attempts, enforce max 5).
  - Resolve `User` via `User.profile.telephone`.
  - Determine role:
    - Government if `user.agent_verification` exists.
    - Partner if `user.agent_partenaire_profile` exists.
  - If Partner:
    - Issue JWT (access, refresh) and return `agent` payload + permissions.
  - If Government:
    - Return `{ requires_badge: true, intermediate_token }`.
      - `intermediate_token`: short‑lived (e.g., 5–10 min), scoped token allowing only badge verification.
- Response (Partner):
  ```json
  {
    "success": true,
    "data": {
      "access": "<jwt>",
      "refresh": "<jwt>",
      "agent": { "type": "agent_partenaire", "permissions": ["process_payment", "manage_cash_session", ...] }
    }
  }
  ```
- Response (Government):
  ```json
  {
    "success": true,
    "data": { "requires_badge": true, "intermediate_token": "<short-lived-token>" }
  }
  ```

### 3) POST `/api/v1/agent-government/verify-badge`
- Body: `{ "badge_id": "AG7552", "intermediate_token": "<token>" }`
- Behavior:
  - Validate `intermediate_token` (not expired, correct scope, bound to user id and phone).
  - Lookup `AgentVerification` by `numero_badge` and match to `user`.
  - If valid → issue full JWT (access + refresh) and return `agent` payload + permissions.
- Response:
  ```json
  {
    "success": true,
    "data": {
      "access": "<jwt>",
      "refresh": "<jwt>",
      "agent": { "type": "agent_government", "permissions": ["scan_qr", "scan_license_plate", ...] }
    }
  }
  ```

## Data Model
### `LoginOTP` (DB or Redis)
- `phone`: string
- `otp_hash`: string (HMAC or salted hash; never store plaintext OTP)
- `expires_at`: datetime (TTL ~5 minutes)
- `attempts`: int (max 5)
- `last_sent_at`: datetime (cooldown enforcement)
- `user_id`: FK or reference to bound user (set after resolving phone)

### Intermediate Token
- JWT or signed token with claims:
  - `user_id`, `phone`, `scope = "badge_verification"`, `exp` ~ 5–10 minutes
  - Not usable for other endpoints.

## Security
- OTP hashing: use HMAC or salted hash; compare securely.
- Rate limiting: throttle OTP requests and verifications (`AuthThrottle`).
- Resend cooldown: 60–90 seconds.
- Attempt limits: 5 attempts per OTP.
- Intermediate token: short TTL, scoped, bound to user and phone, single‑use.
- Audit logging: record OTP verify attempts, badge verification success/failure.
- SMS content: avoid sensitive info; include expiry only.

## Error Handling
- `validation_error`: invalid phone format, missing fields.
- `otp_invalid`: wrong or expired code; include remaining attempts.
- `otp_rate_limited`: resend cooldown not met.
- `badge_invalid`: badge not found or mismatch with user.
- `token_invalid`: intermediate token invalid or expired.

## Mobile App Changes
- LoginScreen: two-step OTP UI
  - Step 1: phone input (`+261…`), "Envoyer OTP" button, resend link with countdown.
  - Step 2: OTP input, "Se connecter" button.
  - If `requires_badge`: show badge input screen → submit badge with `intermediate_token`.
- Services:
  - `requestOtp(phone)` → `/auth/request-otp`
  - `verifyOtp(phone, otp)` → `/auth/verify-otp`
  - `verifyBadge(badgeId, intermediateToken)` → `/agent-government/verify-badge`
- State: on government flow, store `intermediate_token` until badge step.
- Permissions: identical to current mapping in `auth.types.ts`.

## Migration Plan
- Ensure `UserProfile.telephone` is populated and validated (`+261` regex already present).
- For all government agents, confirm phone numbers and badge linkage (`AgentVerification.numero_badge`).
- Rollout: enable OTP endpoints, update app, communicate new login method via SMS.

## Testing
- Unit: OTP generation, hashing/validation, cooldown and attempt limits.
- Integration: full Partner and Government flows, intermediate token expiry.
- Edge cases: wrong phone, expired OTP, wrong badge, multiple resend attempts.
- Load: throttle behavior and SMS sending capacity.

## Monitoring
- Metrics: OTP requests, verify success rate, badge verification failures, throttle hits.
- Alerts: spikes in invalid OTPs or badge failures.

## Example Payloads
### Request OTP
```json
POST /api/v1/auth/request-otp
{ "phone": "+261345678901" }
```

### Verify OTP (Partner)
```json
POST /api/v1/auth/verify-otp
{ "phone": "+261345678901", "otp": "123456" }
```

### Verify OTP (Government response)
```json
{
  "success": true,
  "data": { "requires_badge": true, "intermediate_token": "<token>" }
}
```

### Verify Badge
```json
POST /api/v1/agent-government/verify-badge
{ "badge_id": "AG7552", "intermediate_token": "<token>" }
```

## Implementation Notes (Django API)
- Add actions to `AuthViewSet`: `request_otp`, `verify_otp`.
- Add a `verify_badge` action to `AgentGovernmentViewSet`.
- Use `ConfigurationSysteme.get_config("sms_api_key")` for SMS provider config.
- Reuse existing JWT issuance flow from `AuthViewSet.login`.

## Rollout Checklist
- [ ] Configure SMS provider and API key.
- [ ] Create `LoginOTP` storage (model or Redis) and migrations if needed.
- [ ] Implement endpoints and throttling.
- [ ] Update mobile app screens and services.
- [ ] QA both flows and edge cases.
- [ ] Monitor metrics post-deploy.