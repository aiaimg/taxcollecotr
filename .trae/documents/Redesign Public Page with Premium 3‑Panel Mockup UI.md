## Goal

Create an ultra-clean, premium public page for the Tax Collector platform using Apple minimalism + Swiss/International Typographic Style.  strictly tax‑collection context.

## Scope

Redesign `templates/cms/public_home.html` (route `/`, `cms/urls.py:7-11`) while keeping `base_public.html` header/footer and CMS context intact (`cms/views.py:179-213`, `templates/cms/base_public.html:62-87`). Inject new CSS/JS via existing blocks (`templates/cms/base_public.html:41-43`, `95-97`).

## Files To Update/Add

* Update: `templates/cms/public_home.html`

* Add: `static/cms/css/public_premium.css` (visual system)

* Add: `static/cms/js/public_premium.js` (micro-animations/interactions)

* Leave: `templates/cms/base_public.html` and partials untouched

## Layout (3‑Panel)

1. Left Sidebar (Ultra‑thin)

* Minimal nav with uppercase labels and tiny line icons

* Active indicator: red accent line/dot `#FF2A2A`

* Items: Accueil, Paiement, Vérification QR, Paramètres

* Uses strong alignment, 1px dividers at 8–10% opacity

1. Main Workspace (Center)

* Top header:

  * Headline: “Payez vos taxes véhicules en quelques minutes.”

  * Subtext: official platform description; small uppercase tag: “Plateforme officielle — Madagascar”

* A) Input Card (Left):

  * Label: “Entrée”

  * Minimal form: `Immatriculation`, `Année fiscale`, CTA “Calculer”

  * Dashed border, rounded rectangle, soft shadow (near‑zero)

* B) Output Card (Right):

  * Label: “Sortie”

  * Neutral placeholder when empty; shows summary/estimation when available

* Payment Method Selector:

  * Horizontal pills: Mobile Money, Espèces (point de collecte)

  * Tiny color circle + name; high‑contrast active state

1. Right Utility Panel (Apple‑style Glass)

* Toggles (pill switches):

  * Recevoir reçu PDF

  * Activer rappels avant échéance

  * Mode calcul détaillé

* Sliders (micro‑thin):

  * Intensité des rappels

  * Contraste visuel

* Download Section:

  * Button: “Télécharger la quittance” (black bg, white text, rounded‑full, subtle hover lift/invert)

  * Small helper: “Enregistrez votre reçu officiel.”

## Design System

* Colors: `#000`, `#111`, `#222`, `#777`, `#EEE`, accent red `#FF2A2A` only for active states

* Typography: SF Pro / Inter / Helvetica Now (tight bold headlines; airy body; uppercase labels)

* Grid: strong Swiss alignment, abundant negative space, near‑zero shadows

* Dividers: 1px at 8–10% opacity, perfect alignment

* Iconography: minimal, line icons (using existing `icons.min.css`, `templates/cms/base_public.html:35-39`)

## Accessibility & i18n

* ARIA roles/labels; keyboard navigation; visible focus states

* Use `{% trans %}` for user‑facing strings (consistent with current templates)

* Maintain responsive mobile/desktop layouts with preserved rhythm

## Integration Notes

* Keep CMS context via `get_cms_context()` (`cms/views.py:102-146`)

* Keep header/footer includes (`templates/cms/base_public.html:63-66`, `85-87`)

* Optionally render CMS‑managed sections below the new layout (`templates/cms/public_home.html:240-247`)

* Load CSS/JS through `extra_css` and `extra_js` blocks

## Testing

* Update `cms/tests/test_public_home_view.py` to assert the new structure renders (sidebar, workspace, utility panel)

* Accessibility checks (landmarks, labels, tab order)

* Visual QA at mobile/desktop breakpoints

## Deliverables

* Refactored `public_home.html` with the premium 3‑panel layout

* New `public_premium.css` and `public_premium.js` assets

* No changes to routing or view logic

* Consistent, Dribbble‑worthy visual identity aligned to Tax Collector

