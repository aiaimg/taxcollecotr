## Overview

Implement distinct sidebar sections for Maritime and Aerial vehicles under the company fleet navigation, preserving existing Terrestrial functionality. Add proper routes/filters, consistent styling with visual differentiation, accessibility, and tests.

## Files To Update

* `templates/velzon/partials/sidebar_company.html` (add two new collapsible sections)

* `core/views.py` (support category filtering in `FleetVehicleListView`)

* `css/branding.css` (light visual accents for section differentiation)

## Sidebar Design

* Insert two new collapsible sections beneath Fleet Management:

  * Maritime Vehicles

    * Sub-items:

      * `All Maritime Vehicles` → `core:fleet_vehicles?category=MARITIME`

      * `Add Maritime Vehicle` → `vehicles:vehicle_create_maritime`

  * Aerial Vehicles

    * Sub-items:

      * `All Aerial Vehicles` → `core:fleet_vehicles?category=AERIEN`

      * `Add Aerial Vehicle` → `vehicles:vehicle_create_aerial`

* Use existing patterns: `menu-title`, `nav-item`, `nav-link menu-link`, `collapse menu-dropdown`, with Bootstrap collapse and ARIA attributes.

* Keep existing items like `Tous les Véhicules` and `Ajouter un Véhicule` unchanged.

* Code references for current structure: `templates/velzon/partials/sidebar_company.html:37-71`.

## Routing And Views

* Reuse `core:fleet_vehicles` and extend its view to support category filtering.

* Update `FleetVehicleListView.get_queryset` to honor a new GET parameter `category` with values `TERRESTRE | AERIEN | MARITIME` and filter on `Vehicule.vehicle_category`.

  * Current view location: `core/views.py:804-858`

  * Add after type filter: check `self.request.GET.get("category")` and apply `queryset.filter(vehicle_category=category)` if present.

* Vehicle creation routes already exist:

  * `vehicles:vehicle_create_terrestrial`/`_aerial`/`_maritime` in `vehicles/urls.py:15-17`

## Styling And Icons

* Keep base styling consistent with Velzon.

* Add subtle visual accents so sections are distinguishable:

  * Maritime: `ri-ship-line` icon with accent class (e.g., `text-info`), left border accent via `.sidebar-section-maritime { border-left: 3px solid #0dcaf0; }`

  * Aerial: `ri-plane-line` icon with accent class (e.g., `text-primary`), left border accent via `.sidebar-section-aerial { border-left: 3px solid #6f42c1; }`

* Place small CSS in `css/branding.css` so it loads after theme styles.

## Accessibility And Responsiveness

* Ensure all collapsible toggles have `role="button"`, `aria-controls`, and toggle `aria-expanded` via existing JS in sidebar (`templates/velzon/partials/sidebar_company.html:175-215`).

* Provide descriptive text labels and `aria-hidden="true"` on decorative icons.

* Keep keyboard navigation and large tap targets consistent with existing menu.

* Verify contrast and focus outline remain visible with the added accents.

## Icons And Visual Indicators

* Maritime: `ri-ship-line`

* Aerial: `ri-plane-line`

* Use existing icon set loaded in `base_velzon.html:23` (`icons.min.css`).

## Maintain Existing Functionality

* Do not change role routing in `base_velzon.html:42-67`.

* Preserve current Fleet, Payment, Export, Notifications, and Account items.

## Tests

* Unit tests for view filtering:

  * Add tests to ensure `core:fleet_vehicles?category=AERIEN` returns only aerial vehicles and similarly for maritime and terrestrial.

* Navigation tests:

  * Verify sidebar renders new sections for company users and links resolve (status 200) with authorized user.

* Manual QA matrix:

  * Desktop and mobile breakpoints

  * Keyboard-only navigation through collapsed menus

  * Screen reader labels announced for new menu items

  * All links route correctly and list contents are filtered

## Risks And Rollback

* Low risk: Changes are additive and isolated.

* Rollback: Revert template changes and remove category filter handling in the view.

## Deliverables

* Updated sidebar with distinct Maritime and Aerial sections and working links

* Category filter support in fleet listing

* CSS accents for visual differentiation

* Tests covering routing and filtering

