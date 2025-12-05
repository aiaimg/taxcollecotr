# Requirements Document

## Introduction

Le système Tax Collector doit être étendu pour supporter la déclaration fiscale complète de tous les types de véhicules conformément au Projet de Loi de Finances Initiales (PLFI). Actuellement, le système gère principalement les véhicules terrestres. Cette extension permettra la gestion des véhicules aériens et maritimes avec des formulaires de déclaration adaptés, des validations spécifiques, et un calcul automatique des taxes selon les barèmes en vigueur pour chaque catégorie.

## Glossary

- **System**: La plateforme Tax Collector pour la collecte de taxes sur les véhicules
- **Vehicule Terrestre**: Véhicule circulant sur route (voiture, camion, moto, bus, etc.)
- **Vehicule Aerien**: Aéronef (avion, hélicoptère, drone, ULM, etc.)
- **Vehicule Maritime**: Embarcation (bateau, navire, yacht, jet-ski, etc.)
- **Declarant**: Utilisateur (particulier, entreprise, organisation) qui effectue une déclaration fiscale
- **Grille Tarifaire**: Barème officiel des taxes. Pour véhicules terrestres: basé sur puissance (CV), source d'énergie et âge. Pour véhicules maritimes et aériens: tarifs forfaitaires par catégorie
- **Document Justificatif**: Document officiel requis pour la déclaration (carte grise, certificat de navigabilité, certificat de francisation, etc.)
- **Puissance Fiscale**: Mesure de la puissance d'un véhicule utilisée pour le calcul de la taxe (CV pour terrestre, kW pour aérien, tonnage pour maritime)
- **Annee Fiscale**: Année pour laquelle la taxe est due
- **Statut de Declaration**: État d'avancement d'une déclaration (Brouillon, Soumise, Validée, Rejetée)
- **OCR**: Optical Character Recognition - technologie d'extraction automatique de données depuis des documents scannés
- **Immatriculation**: Numéro d'identification unique d'un véhicule (plaque pour terrestre, numéro de queue pour aérien, numéro de francisation pour maritime)

## Requirements

### Requirement 1

**User Story:** En tant que déclarant, je veux accéder à un module de déclaration fiscale organisé par catégorie de véhicule, afin de pouvoir déclarer facilement mes véhicules terrestres, aériens ou maritimes.

#### Acceptance Criteria

1. WHEN the declarant accesses the tax declaration module THEN the System SHALL display three distinct sections for terrestrial vehicles, aerial vehicles, and maritime vehicles
2. WHEN the declarant selects a vehicle category THEN the System SHALL display the appropriate declaration form with category-specific fields
3. WHEN the declarant navigates between categories THEN the System SHALL preserve unsaved data in the current category with a warning message
4. WHEN the declarant views the declaration module THEN the System SHALL display a summary count of declared vehicles per category
5. WHEN the declarant has no vehicles in a category THEN the System SHALL display a call-to-action button to add the first vehicle of that type

### Requirement 2

**User Story:** En tant que déclarant de véhicule terrestre, je veux remplir un formulaire de déclaration adapté aux véhicules terrestres, afin de fournir toutes les informations nécessaires conformes à la réglementation.

#### Acceptance Criteria

1. WHEN the declarant creates a terrestrial vehicle declaration THEN the System SHALL require plaque d'immatriculation, marque, modèle, puissance fiscale (CV), cylindrée (cm3), source d'énergie, and date de première circulation
2. WHEN the declarant enters a plaque d'immatriculation THEN the System SHALL normalize the format by removing spaces and converting to uppercase
3. WHEN the declarant enters cylindrée and puissance fiscale THEN the System SHALL validate coherence between these values and display a warning if inconsistent
4. WHEN the declarant selects a source d'énergie THEN the System SHALL display only valid options (Essence, Diesel, Électrique, Hybride)
5. WHEN the declarant submits the terrestrial vehicle form THEN the System SHALL validate all required fields are completed before allowing submission
6. WHEN the declarant uploads a carte grise document THEN the System SHALL extract data using OCR and pre-fill form fields with extracted information
7. WHEN OCR extraction completes THEN the System SHALL allow the declarant to review and correct extracted data before final submission

### Requirement 3

**User Story:** En tant que déclarant de véhicule aérien, je veux remplir un formulaire de déclaration adapté aux véhicules aériens, afin de fournir toutes les informations spécifiques aux aéronefs.

#### Acceptance Criteria

1. WHEN the declarant creates an aerial vehicle declaration THEN the System SHALL require numéro d'immatriculation aérienne, type d'aéronef, constructeur, modèle, numéro de série, masse maximale au décollage (kg), puissance moteur (kW), and date de première mise en service
2. WHEN the declarant selects type d'aéronef THEN the System SHALL display options including Avion, Hélicoptère, Drone, ULM, Planeur, and Ballon (all taxed at 2,000,000 Ar/year)
3. WHEN the declarant enters numéro d'immatriculation aérienne THEN the System SHALL validate the format matches international standards (ex: 5R-XXX for Madagascar)
4. WHEN the declarant enters masse maximale au décollage THEN the System SHALL validate the value is positive and within realistic bounds (10 kg to 500,000 kg)
5. WHEN the declarant uploads a certificat de navigabilité THEN the System SHALL extract relevant data and verify the document validity period
6. WHEN the certificat de navigabilité is expired THEN the System SHALL display a warning and require the declarant to upload a valid certificate
7. WHEN the declarant submits the aerial vehicle form THEN the System SHALL apply the fixed annual tax rate of 2,000,000 Ariary for all types of aircraft

### Requirement 4

**User Story:** En tant que déclarant de véhicule maritime, je veux remplir un formulaire de déclaration adapté aux véhicules maritimes, afin de fournir toutes les informations spécifiques aux embarcations.

#### Acceptance Criteria

1. WHEN the declarant creates a maritime vehicle declaration THEN the System SHALL require numéro de francisation, nom du navire, type d'embarcation, constructeur, longueur (m), tonnage (tonneaux), puissance moteur (CV ou kW), and date de première mise à l'eau
2. WHEN the declarant selects type d'embarcation THEN the System SHALL display options including Navire de plaisance (≥7m ou moteur ≥22 CV/90 kW), Jet-ski/moto nautique/scooter des mers (≥90 kW), and Autres engins maritimes motorisés
3. WHEN the declarant enters numéro de francisation THEN the System SHALL validate the format and verify uniqueness in the system
4. WHEN the declarant enters longueur THEN the System SHALL validate the value is positive and within realistic bounds (1 m to 400 m)
5. WHEN the declarant enters puissance moteur for a maritime vehicle THEN the System SHALL validate the value is positive and determine if the vehicle meets the threshold criteria (≥22 CV or ≥90 kW depending on category)
6. WHEN the declarant uploads a certificat de francisation THEN the System SHALL extract relevant data and verify the document authenticity
7. WHEN the declarant submits the maritime vehicle form THEN the System SHALL apply the appropriate fixed annual tax rate: 200,000 Ar for navire de plaisance (≥7m ou moteur ≥22 CV/90 kW), 200,000 Ar for jet-ski/moto nautique/scooter des mers (≥90 kW), or 1,000,000 Ar for autres engins maritimes motorisés

### Requirement 5

**User Story:** En tant que déclarant, je veux que le système calcule automatiquement le montant de la taxe pour chaque véhicule déclaré, afin de connaître immédiatement le montant à payer.

#### Acceptance Criteria

1. WHEN the declarant completes all required fields for a vehicle THEN the System SHALL calculate the tax amount automatically using the appropriate tariff grid
2. WHEN the System calculates tax for a terrestrial vehicle THEN the System SHALL use puissance fiscale (CV), source d'énergie, and vehicle age to determine the applicable rate from the PLF 2026 grid
3. WHEN the System calculates tax for an aerial vehicle THEN the System SHALL apply the fixed rate of 2,000,000 Ariary per year for all aircraft types
4. WHEN the System calculates tax for a maritime vehicle THEN the System SHALL apply the fixed rate based on category: 200,000 Ar for navire de plaisance (≥7m ou moteur ≥22 CV/90 kW), 200,000 Ar for jet-ski (≥90 kW), or 1,000,000 Ar for autres engins maritimes motorisés
5. WHEN no tariff grid entry matches the vehicle characteristics THEN the System SHALL display an error message requesting the declarant to contact support
6. WHEN the vehicle qualifies for an exemption (ambulance, sapeurs-pompiers, administratif, convention internationale) THEN the System SHALL display the tax amount as zero with an exemption badge
7. WHEN the tax calculation completes THEN the System SHALL display a detailed breakdown showing the applicable tariff, vehicle characteristics used, and final amount

### Requirement 6

**User Story:** En tant que déclarant, je veux pouvoir joindre les documents justificatifs nécessaires pour chaque type de véhicule, afin de compléter ma déclaration conformément aux exigences légales.

#### Acceptance Criteria

1. WHEN the declarant uploads a document for a terrestrial vehicle THEN the System SHALL accept carte grise (recto/verso), assurance, contrôle technique, and photo de la plaque
2. WHEN the declarant uploads a document for an aerial vehicle THEN the System SHALL accept certificat de navigabilité, certificat d'immatriculation, assurance aérienne, and carnet de vol
3. WHEN the declarant uploads a document for a maritime vehicle THEN the System SHALL accept certificat de francisation, permis de navigation, assurance maritime, and certificat de jaugeage
4. WHEN the declarant uploads a document THEN the System SHALL validate the file format is PDF, JPEG, PNG, or WebP with maximum size of 10 MB
5. WHEN the declarant uploads an image document THEN the System SHALL optimize the image automatically by converting to WebP format and compressing to reduce storage
6. WHEN the declarant uploads a document THEN the System SHALL display a preview thumbnail and allow the declarant to replace or delete the document
7. WHEN the declarant submits a declaration without required documents THEN the System SHALL prevent submission and display a list of missing documents

### Requirement 7

**User Story:** En tant que déclarant, je veux recevoir des aides contextuelles et des explications pendant le processus de déclaration, afin de comprendre mes obligations fiscales et de remplir correctement le formulaire.

#### Acceptance Criteria

1. WHEN the declarant hovers over a form field label THEN the System SHALL display a tooltip with a clear explanation of the required information
2. WHEN the declarant clicks on a help icon next to a field THEN the System SHALL display a detailed explanation panel with examples and legal references
3. WHEN the declarant enters invalid data in a field THEN the System SHALL display an inline error message explaining the validation rule and providing an example of valid input
4. WHEN the declarant accesses the declaration module THEN the System SHALL display a progress indicator showing completed steps and remaining steps
5. WHEN the declarant is on the document upload step THEN the System SHALL display a checklist of required documents with visual indicators for uploaded and missing documents
6. WHEN the declarant completes a declaration section THEN the System SHALL display a success message confirming the section is complete
7. WHEN the declarant navigates away from an incomplete form THEN the System SHALL display a confirmation dialog warning about unsaved changes

### Requirement 8

**User Story:** En tant que déclarant, je veux pouvoir sauvegarder ma déclaration en brouillon et y revenir plus tard, afin de compléter ma déclaration en plusieurs sessions.

#### Acceptance Criteria

1. WHEN the declarant clicks the save draft button THEN the System SHALL save all entered data with status "Brouillon" without validating completeness
2. WHEN the declarant returns to the declaration module THEN the System SHALL display all draft declarations with a "Brouillon" badge and last modification date
3. WHEN the declarant opens a draft declaration THEN the System SHALL restore all previously entered data including uploaded documents
4. WHEN the declarant has multiple draft declarations THEN the System SHALL allow the declarant to delete unwanted drafts
5. WHEN a draft declaration is older than 30 days THEN the System SHALL display a warning suggesting the declarant to complete or delete it
6. WHEN the declarant submits a draft declaration THEN the System SHALL validate all required fields and change status to "Soumise"

### Requirement 9

**User Story:** En tant qu'administrateur, je veux pouvoir configurer et gérer les grilles tarifaires pour chaque catégorie de véhicule, afin d'appliquer les barèmes officiels conformes au PLFI (grille progressive pour terrestres, tarifs forfaitaires pour aériens et maritimes).

#### Acceptance Criteria

1. WHEN the administrator accesses the tariff grid management THEN the System SHALL display separate sections for terrestrial vehicles (progressive grid), aerial vehicles (fixed rates), and maritime vehicles (fixed rates by category)
2. WHEN the administrator creates a new terrestrial vehicle tariff entry THEN the System SHALL require power range (CV), age range, energy source, fiscal year, and tax amount
3. WHEN the administrator creates a new aerial vehicle tariff entry THEN the System SHALL require aircraft type, fiscal year, and fixed tax amount (default: 2,000,000 Ar)
4. WHEN the administrator creates a new maritime vehicle tariff entry THEN the System SHALL require maritime category (navire de plaisance, jet-ski, autres engins), length threshold, power threshold, fiscal year, and fixed tax amount
5. WHEN the administrator creates a terrestrial tariff entry with overlapping ranges THEN the System SHALL prevent creation and display an error message indicating the conflict
6. WHEN the administrator activates a new tariff grid for a fiscal year THEN the System SHALL deactivate previous grids for the same year and category
7. WHEN the administrator modifies a tariff entry THEN the System SHALL create an audit log entry recording the change, user, and timestamp
8. WHEN the administrator imports a tariff grid from CSV THEN the System SHALL validate all entries and display a summary of successful imports and errors
9. WHEN the System calculates tax using a tariff grid THEN the System SHALL use only active entries for the current fiscal year

### Requirement 10

**User Story:** En tant que système, je veux appliquer automatiquement les critères de seuil pour les véhicules maritimes, afin de déterminer la catégorie tarifaire applicable selon les caractéristiques du véhicule.

#### Acceptance Criteria

1. WHEN the declarant enters a maritime vehicle with longueur ≥ 7 meters OR puissance moteur ≥ 22 CV (or ≥ 90 kW) THEN the System SHALL classify it as "Navire de plaisance" with tax rate of 200,000 Ar
2. WHEN the declarant enters a jet-ski, moto nautique, or scooter des mers with puissance moteur ≥ 90 kW THEN the System SHALL classify it as "Jet-ski/moto nautique" with tax rate of 200,000 Ar
3. WHEN the declarant enters a maritime vehicle that does not meet the above thresholds THEN the System SHALL classify it as "Autres engins maritimes motorisés" with tax rate of 1,000,000 Ar
4. WHEN the declarant enters puissance moteur in CV THEN the System SHALL convert to kW using the formula: kW = CV × 0.735
5. WHEN the declarant enters puissance moteur in kW THEN the System SHALL convert to CV using the formula: CV = kW × 1.36
6. WHEN the System classifies a maritime vehicle THEN the System SHALL display the classification result and applicable tax rate before submission
7. WHEN the declarant disagrees with the automatic classification THEN the System SHALL allow manual override with administrator approval required

### Requirement 12

**User Story:** En tant qu'administrateur, je veux pouvoir valider ou rejeter les déclarations soumises, afin de vérifier la conformité des informations et des documents avant l'émission du paiement.

#### Acceptance Criteria

1. WHEN the administrator accesses the declaration validation queue THEN the System SHALL display all declarations with status "Soumise" ordered by submission date
2. WHEN the administrator opens a declaration for review THEN the System SHALL display all vehicle information, uploaded documents, and calculated tax amount
3. WHEN the administrator validates a declaration THEN the System SHALL change status to "Validée" and send a notification to the declarant with payment instructions
4. WHEN the administrator rejects a declaration THEN the System SHALL require a rejection reason and change status to "Rejetée"
5. WHEN a declaration is rejected THEN the System SHALL send a notification to the declarant with the rejection reason and allow resubmission
6. WHEN the administrator validates a declaration THEN the System SHALL generate a QR code for verification and associate it with the vehicle
7. WHEN the administrator views declaration statistics THEN the System SHALL display counts of declarations by status and category with trend graphs

### Requirement 16

**User Story:** En tant que déclarant, je veux recevoir des notifications à chaque étape du processus de déclaration, afin d'être informé de l'avancement et des actions requises.

#### Acceptance Criteria

1. WHEN the declarant saves a draft declaration THEN the System SHALL send an in-app notification confirming the save
2. WHEN the declarant submits a declaration THEN the System SHALL send an email and SMS notification confirming submission with a reference number
3. WHEN an administrator validates a declaration THEN the System SHALL send an email and in-app notification to the declarant with payment instructions
4. WHEN an administrator rejects a declaration THEN the System SHALL send an email and in-app notification to the declarant with the rejection reason
5. WHEN a declaration payment is completed THEN the System SHALL send an email and SMS notification with the receipt and QR code
6. WHEN a declaration is 15 days from expiration THEN the System SHALL send a reminder notification to the declarant
7. WHEN the System sends a notification THEN the System SHALL respect the declarant's notification preferences (email, SMS, push, in-app)

### Requirement 17

**User Story:** En tant que déclarant, je veux pouvoir consulter l'historique de toutes mes déclarations, afin de suivre mes véhicules déclarés et les paiements effectués.

#### Acceptance Criteria

1. WHEN the declarant accesses the declaration history THEN the System SHALL display all declarations grouped by fiscal year and vehicle category
2. WHEN the declarant views a declaration in history THEN the System SHALL display vehicle details, submission date, validation date, payment status, and tax amount
3. WHEN the declarant filters the history by category THEN the System SHALL display only declarations for the selected category (terrestrial, aerial, maritime)
4. WHEN the declarant filters the history by status THEN the System SHALL display only declarations matching the selected status
5. WHEN the declarant searches the history by vehicle identifier THEN the System SHALL display matching declarations across all years
6. WHEN the declarant exports the history THEN the System SHALL generate a CSV or PDF file containing all declaration records
7. WHEN the declarant views a paid declaration THEN the System SHALL display a download button for the receipt and QR code

### Requirement 13

**User Story:** En tant que système, je veux valider la cohérence et l'exhaustivité des données déclarées, afin de garantir la conformité aux exigences légales et la qualité des données.

#### Acceptance Criteria

1. WHEN the declarant enters vehicle identification number THEN the System SHALL validate uniqueness across all vehicles in the database
2. WHEN the declarant enters vehicle characteristics THEN the System SHALL validate values are within realistic bounds for the vehicle category
3. WHEN the declarant uploads a document THEN the System SHALL validate the file is not corrupted and is readable
4. WHEN the declarant submits a declaration THEN the System SHALL verify all required documents for the vehicle category are uploaded
5. WHEN the System detects duplicate vehicle identification THEN the System SHALL prevent submission and display an error message with the existing vehicle details
6. WHEN the declarant enters a date field THEN the System SHALL validate the date is in the past for historical dates and in the future for expiration dates
7. WHEN the System validates a declaration THEN the System SHALL create a validation report listing all checks performed and their results

### Requirement 14

**User Story:** En tant que déclarant, je veux pouvoir modifier une déclaration rejetée et la resoumettre, afin de corriger les erreurs identifiées par l'administrateur.

#### Acceptance Criteria

1. WHEN the declarant opens a rejected declaration THEN the System SHALL display the rejection reason prominently at the top of the form
2. WHEN the declarant modifies a rejected declaration THEN the System SHALL allow editing of all fields and document uploads
3. WHEN the declarant resubmits a corrected declaration THEN the System SHALL change status from "Rejetée" to "Soumise" and add to the validation queue
4. WHEN the declarant resubmits a declaration THEN the System SHALL create an audit log entry recording the resubmission
5. WHEN the declarant views a rejected declaration THEN the System SHALL highlight the fields mentioned in the rejection reason
6. WHEN the declarant resubmits a declaration multiple times THEN the System SHALL display the submission history with dates and rejection reasons

### Requirement 15

**User Story:** En tant que système, je veux générer des rapports statistiques sur les déclarations par catégorie de véhicule, afin de fournir des données pour l'analyse et la prise de décision.

#### Acceptance Criteria

1. WHEN the administrator requests a statistical report THEN the System SHALL generate counts of declarations by vehicle category and fiscal year
2. WHEN the administrator views declaration statistics THEN the System SHALL display total tax revenue by vehicle category with comparison to previous years
3. WHEN the administrator filters statistics by date range THEN the System SHALL recalculate all metrics for the selected period
4. WHEN the administrator exports statistics THEN the System SHALL generate a CSV or Excel file with detailed breakdown by category and status
5. WHEN the System generates statistics THEN the System SHALL include average processing time from submission to validation
6. WHEN the System generates statistics THEN the System SHALL include rejection rate by vehicle category with common rejection reasons
7. WHEN the administrator views statistics THEN the System SHALL display trend graphs showing declaration volume over time by category
