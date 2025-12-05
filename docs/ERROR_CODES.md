# TaxCollector API Error Codes

This reference lists standardized error codes returned in RFC 7807 Problem Details responses.

## Format
- Content-Type: `application/problem+json`
- Fields: `type`, `title`, `status`, `detail`, `instance`, `code`, `correlationId`, optional `errors`

## Codes

- `validation_error` (400)
  - fr: Erreur de validation
  - mg: Hadisoana fanamarinana
  - en: Validation Error

- `authentication_error` (401)
  - fr: Authentification requise
  - mg: Tsy nahomby ny fankatoavana
  - en: Authentication Required

- `permission_denied` (403)
  - fr: Accès refusé
  - mg: Tsy azo idirana
  - en: Access Denied

- `not_found` (404)
  - fr: Ressource introuvable
  - mg: Tsy hita ny loharano
  - en: Resource Not Found

- `rate_limit` (429)
  - fr: Limite de requêtes dépassée
  - mg: Be loatra ny fangatahana
  - en: Rate Limit Exceeded

- `bad_request` (400)
  - fr: Requête invalide
  - mg: Fangatahana diso
  - en: Bad Request

- `internal_error` (500)
  - fr: Erreur interne du serveur
  - mg: Hadisoana anatiny amin'ny lohamilina
  - en: Internal Server Error

