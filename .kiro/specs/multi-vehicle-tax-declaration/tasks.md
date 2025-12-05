# Implementation Plan - Module de Déclaration Fiscale Multi-Véhicules

## Overview

Ce plan d'implémentation détaille les tâches nécessaires pour étendre le système Tax Collector existant afin de supporter les véhicules aériens et maritimes. L'approche est incrémentale, en commençant par les modèles de données, puis les services, les formulaires, et enfin l'interface utilisateur.

## Tasks

- [x] 1. Préparer la base de données et les modèles
  - Créer les migrations pour étendre le modèle `Vehicule`
  - Ajouter les champs spécifiques aériens et maritimes
  - Créer les index pour optimiser les requêtes
  - _Requirements: 3.1, 4.1_

- [x] 1.1 Créer la migration pour les champs véhicules multi-catégories
  - Ajouter `vehicle_category` (TERRESTRE/AERIEN/MARITIME)
  - Ajouter champs aériens: `immatriculation_aerienne`, `masse_maximale_decollage_kg`, `numero_serie_aeronef`
  - Ajouter champs maritimes: `numero_francisation`, `nom_navire`, `longueur_metres`, `tonnage_tonneaux`, `puissance_moteur_kw`
  - Créer index sur `vehicle_category`, `immatriculation_aerienne`, `numero_francisation`
  - _Requirements: 3.1, 4.1_

- [x] 1.2 Étendre le modèle `GrilleTarifaire` pour tarifs forfaitaires
  - Ajouter `grid_type` (PROGRESSIVE/FLAT_AERIAL/FLAT_MARITIME)
  - Ajouter `maritime_category` (NAVIRE_PLAISANCE/JETSKI/AUTRES_ENGINS)
  - Ajouter `aerial_type` (ALL/AVION/HELICOPTERE/etc.)
  - Ajouter seuils maritimes: `longueur_min_metres`, `puissance_min_cv_maritime`, `puissance_min_kw_maritime`
  - _Requirements: 9.2, 9.3, 9.4_

- [x] 1.3 Créer les types de véhicules aériens et maritimes
  - Créer migration de données pour ajouter types aériens (Avion, Hélicoptère, Drone, ULM, Planeur, Ballon)
  - Créer migration de données pour ajouter types maritimes (Bateau de plaisance, Yacht, Jet-ski, Voilier, etc.)
  - Définir l'ordre d'affichage approprié
  - _Requirements: 3.2, 4.2_

- [x] 1.4 Étendre les types de documents véhicules
  - Ajouter types de documents aériens: `certificat_navigabilite`, `certificat_immatriculation_aerienne`, `assurance_aerienne`, `carnet_vol`
  - Ajouter types de documents maritimes: `certificat_francisation`, `permis_navigation`, `assurance_maritime`, `certificat_jaugeage`
  - Mettre à jour les choix dans `DocumentVehicule.DOCUMENT_TYPE_CHOICES`
  - _Requirements: 6.2, 6.3_

- [ ] 2. Créer les grilles tarifaires forfaitaires
  - Créer la grille forfaitaire pour véhicules aériens (2,000,000 Ar)
  - Créer les grilles forfaitaires pour véhicules maritimes (200,000 Ar et 1,000,000 Ar)
  - Configurer les seuils de classification maritime
  - _Requirements: 5.3, 5.4, 9.3, 9.4_

- [x] 2.1 Créer la grille tarifaire aérienne
  - Créer `GrilleTarifaire` avec `grid_type='FLAT_AERIAL'`
  - Définir `aerial_type='ALL'` (tous types d'aéronefs)
  - Définir `montant_ariary=2000000`
  - Définir `annee_fiscale=2026` et `est_active=True`
  - _Requirements: 5.3, 9.3_

- [x] 2.2 Créer les grilles tarifaires maritimes
  - Créer grille pour `NAVIRE_PLAISANCE` (200,000 Ar) avec seuils longueur ≥7m ou puissance ≥22CV/90kW
  - Créer grille pour `JETSKI` (200,000 Ar) avec seuil puissance ≥90kW
  - Créer grille pour `AUTRES_ENGINS` (1,000,000 Ar) sans seuils
  - _Requirements: 5.4, 9.4, 10.1, 10.2, 10.3_


- [ ] 3. Implémenter les services de calcul de taxe
  - Étendre `TaxCalculationService` avec méthodes pour aérien et maritime
  - Implémenter la logique de classification maritime
  - Implémenter les conversions de puissance CV ↔ kW
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 10.4, 10.5_

- [x] 3.1 Étendre `TaxCalculationService.calculate_tax()` pour router par catégorie
  - Modifier la méthode principale pour détecter `vehicle_category`
  - Router vers `calculate_terrestrial_tax()` pour TERRESTRE (existant)
  - Router vers `calculate_aerial_tax()` pour AERIEN (nouveau)
  - Router vers `calculate_maritime_tax()` pour MARITIME (nouveau)
  - _Requirements: 5.1_

- [x] 3.2 Implémenter `calculate_aerial_tax()` pour tarif forfaitaire
  - Vérifier si véhicule est exonéré
  - Récupérer la grille `FLAT_AERIAL` active pour l'année fiscale
  - Retourner montant forfaitaire de 2,000,000 Ar
  - Gérer les erreurs si grille non configurée
  - _Requirements: 5.3_

- [x] 3.3 Implémenter `calculate_maritime_tax()` avec classification
  - Vérifier si véhicule est exonéré
  - Appeler `_classify_maritime_vehicle()` pour déterminer la catégorie
  - Récupérer la grille `FLAT_MARITIME` correspondante
  - Retourner montant selon catégorie (200K ou 1M Ar)
  - _Requirements: 5.4, 10.1, 10.2, 10.3_

- [x] 3.4 Implémenter `_classify_maritime_vehicle()` pour classification automatique
  - Extraire longueur, puissance CV et puissance kW du véhicule
  - Convertir kW en CV si nécessaire (kW × 1.36)
  - Détecter jet-ski/moto nautique par nom de type + puissance ≥90kW → JETSKI
  - Détecter navire de plaisance si longueur ≥7m OU puissance ≥22CV OU puissance ≥90kW → NAVIRE_PLAISANCE
  - Sinon → AUTRES_ENGINS
  - _Requirements: 10.1, 10.2, 10.3, 10.6_

- [x] 3.5 Implémenter les fonctions de conversion de puissance
  - Créer `convert_cv_to_kw(cv)` avec formule: kW = CV × 0.735
  - Créer `convert_kw_to_cv(kw)` avec formule: CV = kW × 1.36
  - Créer `validate_power_conversion(cv, kw)` pour vérifier cohérence (tolérance 1%)
  - Gérer les arrondis à 2 décimales
  - _Requirements: 10.4, 10.5_

- [x] 3.6 Écrire les tests unitaires pour les services de calcul
  - Tester `calculate_aerial_tax()` retourne toujours 2M Ar
  - Tester `calculate_maritime_tax()` retourne 200K pour NAVIRE_PLAISANCE et JETSKI
  - Tester `calculate_maritime_tax()` retourne 1M pour AUTRES_ENGINS
  - Tester `_classify_maritime_vehicle()` pour tous les cas limites
  - Tester conversions CV ↔ kW avec round-trip
  - _Requirements: 5.3, 5.4, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 4. Créer les formulaires de déclaration
  - Créer `VehiculeAerienForm` pour véhicules aériens
  - Créer `VehiculeMaritimeForm` pour véhicules maritimes
  - Implémenter les validations spécifiques par catégorie
  - _Requirements: 3.1-3.7, 4.1-4.7_

- [x] 4.1 Créer `VehiculeAerienForm` avec champs aériens
  - Définir les champs: `immatriculation_aerienne`, `type_vehicule`, `marque`, `modele`, `numero_serie_aeronef`, `masse_maximale_decollage_kg`, `puissance_moteur_kw`, `date_premiere_circulation`, `categorie_vehicule`
  - Configurer les widgets avec classes CSS et placeholders
  - Définir les labels et help_text en français
  - _Requirements: 3.1_

- [x] 4.2 Implémenter les validations pour `VehiculeAerienForm`
  - Valider format `immatriculation_aerienne` (ex: 5R-XXX pour Madagascar)
  - Valider `masse_maximale_decollage_kg` entre 10 kg et 500,000 kg
  - Auto-définir `vehicle_category = 'AERIEN'` dans `clean()`
  - Valider que `type_vehicule` est un type aérien
  - _Requirements: 3.3, 3.4_

- [x] 4.3 Créer `VehiculeMaritimeForm` avec champs maritimes
  - Définir les champs: `numero_francisation`, `nom_navire`, `type_vehicule`, `marque`, `modele`, `longueur_metres`, `tonnage_tonneaux`, `puissance_fiscale_cv`, `puissance_moteur_kw`, `date_premiere_circulation`, `categorie_vehicule`
  - Ajouter champ `puissance_moteur_unit` (CV/kW) pour sélection d'unité
  - Configurer les widgets avec classes CSS et placeholders
  - _Requirements: 4.1_

- [x] 4.4 Implémenter les validations pour `VehiculeMaritimeForm`
  - Valider format `numero_francisation`
  - Valider `longueur_metres` entre 1m et 400m
  - Valider `tonnage_tonneaux` positif
  - Convertir automatiquement CV ↔ kW selon `puissance_moteur_unit`
  - Valider cohérence de la conversion avec `validate_power_conversion()`
  - Auto-définir `vehicle_category = 'MARITIME'` dans `clean()`
  - _Requirements: 4.3, 4.4, 4.5, 10.4, 10.5_

- [x] 4.5 Implémenter `get_maritime_classification()` dans le formulaire
  - Extraire longueur, puissance CV, puissance kW, type véhicule
  - Appeler la logique de classification (réutiliser `_classify_maritime_vehicle()`)
  - Retourner la catégorie maritime déterminée
  - Stocker dans `specifications_techniques['maritime_classification']`
  - _Requirements: 4.7, 10.6_

- [x] 4.6 Écrire les tests unitaires pour les formulaires
  - Tester validation format immatriculation aérienne
  - Tester validation limites masse maximale
  - Tester validation format francisation
  - Tester validation limites longueur
  - Tester conversion automatique CV ↔ kW
  - Tester détection incohérence conversion
  - Tester classification maritime automatique
  - _Requirements: 3.3, 3.4, 4.3, 4.4, 4.5, 10.4, 10.5, 10.6_

- [x] 5. Créer les vues et templates
  - Créer vue de sélection de catégorie
  - Créer vues de création pour aérien et maritime
  - Créer les templates correspondants
  - _Requirements: 1.1, 1.2, 3.1-3.7, 4.1-4.7_

- [x] 5.1 Créer `VehicleCategorySelectionView` pour sélection de catégorie
  - Créer vue basée sur `TemplateView`
  - Afficher 3 cartes: Terrestre, Aérien, Maritime
  - Chaque carte avec icône, nom, description, et lien vers formulaire
  - Afficher compteur de véhicules par catégorie
  - _Requirements: 1.1, 1.4_

- [x] 5.2 Créer template `category_selection.html`
  - Design avec 3 cartes Bootstrap/Tailwind
  - Icônes: `ri-car-line` (terrestre), `ri-plane-line` (aérien), `ri-ship-line` (maritime)
  - Boutons "Déclarer" vers formulaires respectifs
  - Afficher compteurs de véhicules déclarés
  - _Requirements: 1.1, 1.4_

- [x] 5.3 Créer `VehiculeAerienCreateView` pour création aérien
  - Hériter de `CreateView` avec `LoginRequiredMixin`
  - Utiliser `VehiculeAerienForm`
  - Auto-définir `vehicle_category = 'AERIEN'`
  - Auto-définir `proprietaire = request.user`
  - Créer notification après création
  - Rediriger vers détail du véhicule
  - _Requirements: 3.1-3.7_

- [x] 5.4 Créer template `vehicule_aerien_form.html`
  - Formulaire avec tous les champs aériens
  - Tooltips d'aide pour chaque champ
  - Validation côté client (HTML5)
  - Affichage du calcul de taxe en temps réel (AJAX)
  - Section upload de documents (certificat navigabilité, etc.)
  - _Requirements: 3.1-3.7, 6.2, 7.1, 7.2_

- [x] 5.5 Créer `VehiculeMaritimeCreateView` pour création maritime
  - Hériter de `CreateView` avec `LoginRequiredMixin`
  - Utiliser `VehiculeMaritimeForm`
  - Auto-définir `vehicle_category = 'MARITIME'`
  - Appeler `get_maritime_classification()` et stocker résultat
  - Créer notification avec classification
  - Rediriger vers détail du véhicule
  - _Requirements: 4.1-4.7_

- [x] 5.6 Créer template `vehicule_maritime_form.html`
  - Formulaire avec tous les champs maritimes
  - Sélecteur d'unité de puissance (CV/kW) avec conversion automatique
  - Affichage de la classification automatique en temps réel
  - Tooltips d'aide pour chaque champ
  - Affichage du calcul de taxe en temps réel (AJAX)
  - Section upload de documents (certificat francisation, etc.)
  - _Requirements: 4.1-4.7, 6.3, 7.1, 7.2, 10.6_

- [x] 5.7 Étendre `VehiculeListView` pour filtrer par catégorie
  - Ajouter filtre par `vehicle_category` dans le formulaire de recherche
  - Afficher icône appropriée selon catégorie
  - Afficher champs spécifiques selon catégorie (immat aérienne, francisation, etc.)
  - Grouper par catégorie dans l'affichage
  - _Requirements: 1.3, 17.3_

- [x] 5.8 Étendre `VehiculeDetailView` pour afficher selon catégorie
  - Détecter `vehicle_category` du véhicule
  - Afficher champs spécifiques aériens si AERIEN
  - Afficher champs spécifiques maritimes si MARITIME (avec classification)
  - Afficher documents appropriés selon catégorie
  - Afficher calcul de taxe avec méthode appropriée
  - _Requirements: 17.2_

- [x] 6. Implémenter les endpoints AJAX
  - Créer endpoint pour calcul de taxe en temps réel
  - Créer endpoint pour classification maritime en temps réel
  - Créer endpoint pour conversion CV ↔ kW
  - _Requirements: 5.7, 7.3, 10.6_

- [x] 6.1 Créer endpoint AJAX `calculate_tax_ajax`
  - Accepter POST avec données véhicule (catégorie, caractéristiques)
  - Créer instance temporaire de `Vehicule` (non sauvegardée)
  - Appeler `TaxCalculationService.calculate_tax()`
  - Retourner JSON avec montant, grille applicable, méthode de calcul
  - _Requirements: 5.7, 7.3_

- [x] 6.2 Créer endpoint AJAX `classify_maritime_ajax`
  - Accepter POST avec longueur, puissance CV, puissance kW, type véhicule
  - Appeler `_classify_maritime_vehicle()`
  - Retourner JSON avec catégorie, montant taxe, niveau de confiance
  - Permettre override manuel si confiance moyenne
  - _Requirements: 10.6, 10.7_

- [x] 6.3 Créer endpoint AJAX `convert_power_ajax`
  - Accepter POST avec valeur et unité source (CV ou kW)
  - Appeler `convert_cv_to_kw()` ou `convert_kw_to_cv()`
  - Retourner JSON avec valeur convertie
  - _Requirements: 10.4, 10.5_

- [x] 6.4 Créer JavaScript pour calcul temps réel dans formulaires
  - Écouter changements sur champs de puissance, âge, source énergie (terrestre)
  - Écouter changements sur champs aériens (masse, puissance)
  - Écouter changements sur champs maritimes (longueur, puissance)
  - Appeler endpoints AJAX appropriés
  - Afficher résultat dans section dédiée du formulaire
  - _Requirements: 5.7, 7.3_


- [x] 7. Étendre l'API REST
  - Étendre `VehicleViewSet` pour supporter toutes catégories
  - Créer serializers pour aérien et maritime
  - Ajouter endpoints de filtrage par catégorie
  - _Requirements: 5.1-5.7_

- [x] 7.1 Créer `VehiculeAerienSerializer`
  - Définir tous les champs aériens
  - Ajouter champ calculé `tax_amount` via `SerializerMethodField`
  - Implémenter `get_tax_amount()` appelant `calculate_aerial_tax()`
  - _Requirements: 5.3_

- [x] 7.2 Créer `VehiculeMaritimeSerializer`
  - Définir tous les champs maritimes
  - Ajouter champs calculés `tax_amount` et `maritime_classification`
  - Implémenter `get_tax_amount()` appelant `calculate_maritime_tax()`
  - Implémenter `get_maritime_classification()` appelant `_classify_maritime_vehicle()`
  - _Requirements: 5.4, 10.6_

- [x] 7.3 Étendre `VehicleViewSet.get_serializer_class()`
  - Détecter `vehicle_category` dans `request.data`
  - Retourner `VehiculeAerienSerializer` si AERIEN
  - Retourner `VehiculeMaritimeSerializer` si MARITIME
  - Retourner `VehiculeSerializer` (terrestre) par défaut
  - _Requirements: 5.1_

- [x] 7.4 Ajouter action `@action calculate_tax` dans `VehicleViewSet`
  - Accepter paramètre `year` (optionnel, défaut année courante)
  - Récupérer véhicule par `pk`
  - Appeler `TaxCalculationService.calculate_tax()`
  - Retourner JSON avec détails du calcul
  - _Requirements: 5.1, 5.7_

- [x] 7.5 Ajouter action `@action by_category` dans `VehicleViewSet`
  - Accepter paramètre `category` (TERRESTRE/AERIEN/MARITIME)
  - Filtrer queryset par `vehicle_category`
  - Retourner liste sérialisée
  - _Requirements: 17.3_

- [x] 7.6 Écrire les tests API pour véhicules multi-catégories
  - Tester création véhicule aérien via API
  - Tester création véhicule maritime via API
  - Tester endpoint `calculate_tax` pour chaque catégorie
  - Tester endpoint `by_category` avec filtres
  - Tester sérialisation correcte des champs spécifiques
  - _Requirements: 5.1-5.7_

- [x] 8. Implémenter la gestion des documents
  - Étendre le système de documents pour nouveaux types
  - Adapter les validations selon catégorie véhicule
  - Mettre à jour les templates d'upload
  - _Requirements: 6.1-6.7_

- [x] 8.1 Mettre à jour `DocumentVehicule.DOCUMENT_TYPE_CHOICES`
  - Ajouter types aériens: `certificat_navigabilite`, `certificat_immatriculation_aerienne`, `assurance_aerienne`, `carnet_vol`
  - Ajouter types maritimes: `certificat_francisation`, `permis_navigation`, `assurance_maritime`, `certificat_jaugeage`
  - _Requirements: 6.2, 6.3_

- [x] 8.2 Créer méthode `get_required_documents_by_category()` dans `Vehicule`
  - Retourner liste de types de documents requis selon `vehicle_category`
  - TERRESTRE: carte_grise, assurance, controle_technique
  - AERIEN: certificat_navigabilite, certificat_immatriculation_aerienne, assurance_aerienne
  - MARITIME: certificat_francisation, permis_navigation, assurance_maritime
  - _Requirements: 6.1, 6.2, 6.3, 13.4_

- [x] 8.3 Créer méthode `validate_required_documents()` dans `Vehicule`
  - Récupérer documents requis via `get_required_documents_by_category()`
  - Vérifier que chaque type requis a au moins un document uploadé
  - Retourner liste des documents manquants
  - Bloquer soumission si documents manquants
  - _Requirements: 6.7, 13.4_

- [x] 8.4 Étendre template `vehicule_detail.html` pour documents par catégorie
  - Afficher checklist de documents requis selon catégorie
  - Indiquer visuellement documents uploadés vs manquants
  - Permettre upload de documents spécifiques à la catégorie
  - Afficher avertissement si certificat expiré (navigabilité, francisation)
  - _Requirements: 6.2, 6.3, 6.5, 6.6, 7.5_

- [x] 9. Implémenter les notifications
  - Étendre les notifications pour inclure catégorie véhicule
  - Créer notifications spécifiques pour aérien/maritime
  - Adapter les templates de notification
  - _Requirements: 16.1-16.7_

- [x] 9.1 Étendre `NotificationService.create_vehicle_added_notification()`
  - Détecter `vehicle_category` du véhicule
  - Adapter le message selon catégorie (aéronef ajouté, navire ajouté, etc.)
  - Inclure classification maritime dans le message si MARITIME
  - Inclure montant de taxe calculé
  - _Requirements: 16.2_

- [x] 9.2 Créer notification pour classification maritime
  - Créer `create_maritime_classification_notification()`
  - Envoyer après création véhicule maritime
  - Inclure catégorie déterminée (NAVIRE_PLAISANCE, JETSKI, AUTRES_ENGINS)
  - Inclure montant de taxe applicable
  - Permettre contestation si classification semble incorrecte
  - _Requirements: 10.6, 10.7, 16.2_

- [x] 9.3 Adapter les templates de notification email/SMS
  - Créer template spécifique pour véhicule aérien
  - Créer template spécifique pour véhicule maritime
  - Inclure informations spécifiques (immat aérienne, francisation, classification)
  - _Requirements: 16.2, 16.7_

- [x] 10. Créer l'interface d'administration
  - Étendre les vues admin pour gérer multi-catégories
  - Créer interface de gestion des grilles tarifaires forfaitaires
  - Ajouter statistiques par catégorie
  - _Requirements: 9.1-9.9, 12.1-12.7, 15.1-15.7_

- [x] 10.1 Étendre `admin_vehicle_list` pour filtrer par catégorie
  - Ajouter filtre dropdown pour `vehicle_category`
  - Afficher colonnes spécifiques selon catégorie
  - Afficher icône de catégorie dans la liste
  - Grouper statistiques par catégorie
  - _Requirements: 12.2, 15.1_

- [x] 10.2 Créer vue `admin_tariff_grid_management`
  - Afficher 3 sections: Progressive (Terrestre), Forfaitaire Aérien, Forfaitaire Maritime
  - Section terrestre: tableau existant des 80 tarifs
  - Section aérien: formulaire simple (montant forfaitaire, année fiscale)
  - Section maritime: 3 formulaires (NAVIRE_PLAISANCE, JETSKI, AUTRES_ENGINS) avec seuils
  - Permettre activation/désactivation par année fiscale
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 10.3 Créer formulaire `AerialTariffForm`
  - Champs: `aerial_type` (défaut ALL), `montant_ariary`, `annee_fiscale`, `est_active`
  - Validation: montant positif, année fiscale courante ou future
  - Auto-définir `grid_type = 'FLAT_AERIAL'`
  - _Requirements: 9.3_

- [x] 10.4 Créer formulaire `MaritimeTariffForm`
  - Champs: `maritime_category`, `longueur_min_metres`, `puissance_min_cv_maritime`, `puissance_min_kw_maritime`, `montant_ariary`, `annee_fiscale`, `est_active`
  - Validation selon catégorie (seuils requis pour NAVIRE_PLAISANCE et JETSKI)
  - Auto-définir `grid_type = 'FLAT_MARITIME'`
  - _Requirements: 9.4_

- [x] 10.5 Créer vue `admin_declaration_validation_queue`
  - Lister toutes déclarations avec statut "Soumise"
  - Filtrer par catégorie véhicule
  - Afficher informations spécifiques selon catégorie
  - Permettre validation ou rejet avec raison
  - _Requirements: 12.1, 12.2, 12.4, 12.5_

- [x] 10.6 Créer dashboard statistiques multi-catégories
  - Graphique: Répartition véhicules par catégorie (camembert)
  - Graphique: Revenus par catégorie (barres)
  - Graphique: Évolution déclarations par catégorie (ligne)
  - Tableau: Top 10 types de véhicules déclarés
  - Métriques: Taux de paiement par catégorie
  - _Requirements: 15.1, 15.2, 15.7_

- [ ] 11. Implémenter les aides contextuelles
  - Créer tooltips pour tous les champs
  - Créer panneaux d'aide détaillés
  - Implémenter indicateur de progression
  - _Requirements: 7.1-7.7_

- [x] 11.1 Créer fichier `help_texts.py` avec textes d'aide
  - Définir dictionnaire de textes d'aide par champ
  - Inclure exemples concrets
  - Inclure références légales (PLFI)
  - Supporter multilingue (FR/MG)
  - _Requirements: 7.1, 7.2_

- [x] 11.2 Implémenter tooltips Bootstrap dans templates
  - Ajouter attribut `data-bs-toggle="tooltip"` sur labels
  - Ajouter attribut `title` avec texte d'aide court
  - Initialiser tooltips en JavaScript
  - _Requirements: 7.1_

- [x] 11.3 Créer composant modal d'aide détaillée
  - Créer modal Bootstrap réutilisable
  - Afficher aide détaillée avec exemples et références légales
  - Déclencher par clic sur icône `ri-question-line` à côté des champs
  - _Requirements: 7.2_

- [x] 11.4 Implémenter indicateur de progression
  - Créer composant progress bar Bootstrap
  - Calculer pourcentage de complétion (champs remplis / total)
  - Afficher étapes: Informations de base → Caractéristiques → Documents → Révision
  - Mettre à jour en temps réel lors de la saisie
  - _Requirements: 7.4_

- [x] 11.5 Créer checklist de documents requis
  - Afficher liste de documents requis selon catégorie
  - Indiquer visuellement uploadés (✓ vert) vs manquants (✗ rouge)
  - Permettre clic pour upload direct
  - _Requirements: 7.5_

- [x] 12. Implémenter le système de brouillons
  - Permettre sauvegarde en brouillon
  - Lister et gérer les brouillons
  - Reprendre un brouillon
  - _Requirements: 8.1-8.6_

- [x] 12.1 Ajouter champ `statut_declaration` dans `Vehicule`
  - Valeurs: BROUILLON, SOUMISE, VALIDEE, REJETEE
  - Défaut: BROUILLON
  - Index sur ce champ
  - _Requirements: 8.1, 8.6_

- [x] 12.2 Créer bouton "Sauvegarder en brouillon" dans formulaires
  - Ajouter bouton secondaire à côté de "Soumettre"
  - Sauvegarder sans validation de complétude
  - Définir `statut_declaration = 'BROUILLON'`
  - Afficher message de confirmation
  - _Requirements: 8.1_

- [x] 12.3 Créer vue `draft_vehicle_list`
  - Lister tous véhicules avec `statut_declaration = 'BROUILLON'`
  - Afficher badge "Brouillon" et date dernière modification
  - Permettre reprise, suppression
  - Afficher avertissement si brouillon > 30 jours
  - _Requirements: 8.2, 8.4, 8.5_

- [x] 12.4 Adapter vues de création pour reprendre brouillon
  - Détecter paramètre `draft_id` dans URL
  - Pré-remplir formulaire avec données du brouillon
  - Restaurer documents uploadés
  - _Requirements: 8.3_

- [x] 12.5 Implémenter validation complète lors de soumission
  - Valider tous champs requis
  - Valider documents requis uploadés
  - Changer `statut_declaration` de BROUILLON à SOUMISE
  - Créer notification de soumission
  - _Requirements: 8.6, 16.2_

- [-] 13. Implémenter l'historique et recherche
  - Créer vue d'historique des déclarations
  - Implémenter filtres avancés
  - Permettre export des données
  - _Requirements: 17.1-17.7_

- [x] 13.1 Créer vue `declaration_history`
  - Lister tous véhicules de l'utilisateur
  - Grouper par année fiscale et catégorie
  - Afficher détails: date soumission, date validation, statut paiement, montant taxe
  - _Requirements: 17.1, 17.2_

- [x] 13.2 Implémenter filtres dans historique
  - Filtre par catégorie (TERRESTRE/AERIEN/MARITIME)
  - Filtre par statut (BROUILLON/SOUMISE/VALIDEE/REJETEE)
  - Filtre par année fiscale
  - Recherche par identifiant (plaque, immat aérienne, francisation)
  - _Requirements: 17.3, 17.4, 17.5_

- [x] 13.3 Implémenter export de l'historique
  - Bouton "Exporter" avec choix format (CSV/PDF)
  - CSV: toutes colonnes, une ligne par véhicule
  - PDF: rapport formaté avec logo et en-tête
  - Inclure tous véhicules filtrés
  - _Requirements: 17.6_

- [x] 13.4 Ajouter boutons d'action dans historique
  - Bouton "Télécharger reçu" si paiement effectué
  - Bouton "Télécharger QR code" si paiement effectué
  - Bouton "Payer" si impayé
  - Bouton "Voir détails" pour tous
  - _Requirements: 17.7_

- [x] 14. Checkpoint - Tests d'intégration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14.1 Écrire tests d'intégration pour flux complet aérien
  - Test: Créer véhicule aérien → Calculer taxe → Créer paiement → Générer QR
  - Vérifier montant taxe = 2,000,000 Ar
  - Vérifier QR code généré et valide
  - Vérifier notifications envoyées
  - _Requirements: 3.1-3.7, 5.3_

- [x] 14.2 Écrire tests d'intégration pour flux complet maritime
  - Test: Créer véhicule maritime → Classification auto → Calculer taxe → Créer paiement → Générer QR
  - Tester les 3 catégories (NAVIRE_PLAISANCE, JETSKI, AUTRES_ENGINS)
  - Vérifier montants corrects (200K ou 1M Ar)
  - Vérifier classification stockée
  - _Requirements: 4.1-4.7, 5.4, 10.1-10.7_

- [x] 14.3 Écrire tests de régression pour véhicules terrestres
  - Vérifier que fonctionnalités existantes fonctionnent toujours
  - Tester calcul taxe progressive
  - Tester paiements existants non affectés
  - Tester QR codes existants toujours valides
  - _Requirements: 2.1-2.7, 5.2_

- [x] 14.4 Écrire tests de performance
  - Tester classification de 1000 véhicules maritimes < 1s
  - Tester calcul de 300 taxes (mixte) < 2s
  - Tester chargement liste 1000 véhicules < 3s
  - _Requirements: Performance_

- [ ] 15. Documentation et formation
  - Créer documentation utilisateur
  - Créer documentation administrateur
  - Préparer matériel de formation
  - _Requirements: All_

- [ ] 15.1 Créer guide utilisateur pour déclaration aérienne
  - Étapes détaillées avec captures d'écran
  - Explication des champs requis
  - Liste des documents nécessaires
  - FAQ spécifique aérien
  - _Requirements: 3.1-3.7, 6.2_

- [ ] 15.2 Créer guide utilisateur pour déclaration maritime
  - Étapes détaillées avec captures d'écran
  - Explication de la classification automatique
  - Guide de conversion CV ↔ kW
  - Liste des documents nécessaires
  - FAQ spécifique maritime
  - _Requirements: 4.1-4.7, 6.3, 10.1-10.7_

- [ ] 15.3 Créer guide administrateur pour gestion grilles tarifaires
  - Comment créer/modifier grilles forfaitaires
  - Comment activer/désactiver par année fiscale
  - Comment configurer seuils maritimes
  - Procédure de validation des déclarations
  - _Requirements: 9.1-9.9, 12.1-12.7_

- [ ] 15.4 Créer vidéos de démonstration
  - Vidéo: Déclarer un aéronef (5 min)
  - Vidéo: Déclarer un navire (5 min)
  - Vidéo: Gérer les grilles tarifaires (admin, 10 min)
  - _Requirements: All_

- [ ] 16. Déploiement final
  - Préparer le déploiement en production
  - Effectuer la migration
  - Vérifier le système
  - _Requirements: All_

- [ ] 16.1 Préparer script de déploiement
  - Créer script de backup base de données
  - Créer script d'application des migrations
  - Créer script de création des grilles tarifaires
  - Créer script de création des types de véhicules
  - Créer script de vérification post-déploiement
  - _Requirements: All_

- [ ] 16.2 Effectuer déploiement en staging
  - Backup base staging
  - Appliquer migrations
  - Créer grilles tarifaires
  - Créer types de véhicules
  - Tests de fumée complets
  - _Requirements: All_

- [ ] 16.3 Effectuer tests d'acceptation utilisateur (UAT)
  - Inviter utilisateurs pilotes
  - Tester déclaration aérienne end-to-end
  - Tester déclaration maritime end-to-end
  - Collecter feedback
  - Corriger bugs critiques
  - _Requirements: All_

- [ ] 16.4 Planifier maintenance production
  - Annoncer maintenance (email, SMS, in-app)
  - Planifier fenêtre de 2h hors heures de pointe
  - Préparer équipe de support
  - _Requirements: All_

- [ ] 16.5 Effectuer déploiement en production
  - Activer mode maintenance
  - Backup complet base production
  - Appliquer migrations
  - Créer grilles tarifaires
  - Créer types de véhicules
  - Vérification post-déploiement
  - Désactiver mode maintenance
  - _Requirements: All_

- [ ] 16.6 Monitoring post-déploiement (48h)
  - Surveiller logs d'erreurs
  - Surveiller performance (temps de réponse)
  - Surveiller utilisation (nouvelles déclarations)
  - Support réactif pour utilisateurs
  - _Requirements: All_

- [ ] 17. Final Checkpoint - Vérification complète
  - Ensure all tests pass, ask the user if questions arise.
