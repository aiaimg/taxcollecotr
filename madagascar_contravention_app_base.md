# Document de base – Application de contravention numérique pour la Police à Madagascar

---

## 1. Introduction
Ce document sert de base pour le développement d’une application de gestion des contraventions et infractions routières à Madagascar. Il s’articule autour du Code de la Route Malagasy et intègre les catégories d’infractions, les montants d’amendes, le mécanisme d’enregistrement et le paiement numérique.

---
## 2. Schéma des principales entités métiers

### 2.1. Tableau des infractions et sanctions
| Type d'infraction                                                    | Montant amende (Ariary)        | Sanctions/Mesures complémentaires                      |
|---------------------------------------------------------------------|--------------------------------|--------------------------------------------------------|
| Conduite en état d’ivresse ou stupéfiants                           | 100 000 - 400 000              | Suspension/retrait permis, immobilisation, emprisonnement|
| Refus de vérification (alcoolémie, stupéfiants)                     | 200 000 - 800 000              | Suspension/retrait permis, immobilisation              |
| Conduite sans permis en état d’ivresse                              | 200 000 - 800 000              | Emprisonnement (1-12 mois)                             |
| Délit de fuite                                                      | 500 000 - 2 000 000            | Emprisonnement (2-12 mois)                             |
| Excès de vitesse                                                    | 200 000 - 800 000              | Suspension/retrait permis                              |
| Non port du casque (moto)                                           | Jusqu’à 6 000                  | Avertissement/immobilisation                           |
| Défaut de carte grise/permis/assurance/visite technique             | Variable selon autorité         | Mise en fourrière + poursuites pénales                 |
| Infraction de stationnement interdit                                | 12 000 - 600 000               | Immobilisation par taquets d’arrêt                     |
| Violation de signalisation/feux rouges                             | Variable (souvent > 30 000)    | Mise en fourrière possible                             |
| Usage du téléphone au volant                                        | Variable selon autorité         | Avertissement/amende                                   |
| Modifications illégales du véhicule                                 | Jusqu’à 100 000                | Immobilisation du véhicule                             |
| Chargement mal arrimé/débordant                                    | Variable selon autorité         | Avertissement/immobilisation                           |

---
## 3. Procédure numérique de contravention

### 3.1. Enregistrement d’une infraction
- Identification automatique du policier via compte/biométrie
- Choix de l’infraction dans la liste normalisée
- Remplissage du PV électronique (lieu, heure, véhicule, conducteur)
- Attribution du montant et calcul des frais annexes (fourrière, gardiennage)
- Génération automatique d’un code QR/ID unique pour la contravention

### 3.2. Paiement immédiat
- Affichage d’un portail de paiement (mobile money, carte bancaire, espèces)
- Transmission sécurisée au service de finances de la police
- Validation du paiement et génération d’un reçu numérique
- Mise à jour automatique de la base de données des infractions

---
## 4. Structure de la base de données (suggestion)

### 4.1. Tables principales
- **Infractions** (`id_infraction`, `type`, `montant_min`, `montant_max`, `sanction`)
- **Contravention** (`id`, `date_heure`, `lieu`, `policier_id`, `conducteur_id`, `vehicule_id`, `id_infraction`, `montant_applique`, `status_paiement`, `mode_paiement`, `code_qr`)
- **Policiers** (`id`, `nom`, `matricule`, `unité_affectation`, `login`)
- **Conducteurs** (`id`, `nom`, `cin`, `permis`, `adresse`, `telephone`)
- **Véhicules** (`id`, `immatriculation`, `type`, `propriétaire_id`)
- **Paiements** (`id`, `contravention_id`, `date_paiement`, `mode`, `montant`) 

### 4.2. Sécurité et traçabilité
- Authentification forte pour les agents
- Historisation de toutes les actions et paiements
- Chaque amende/contravention liée à un identifiant et QR code unique
- Sauvegarde centralisée et synchronisation en temps réel

---
## 5. Frais associés (modèle fourrière)
| Type de frais                                 | Montant/Durée                |
|-----------------------------------------------|------------------------------|
| Transport vers fourrière (véhicule léger)      | 20 000 Ariary                |
| Gardiennage (voiture par jour)                | 10 000 Ariary/jour           |
| Durée minimale de fourrière                   | 10 jours (non périssable)    |
| Durée minimale pour produits périssables      | 5 jours                      |
| Total estimé pour 10 jours (voiture)          | Environ 120 000 Ariary       |
| Transport animaux sans papiers                | 15 000 - 100 000 Ariary      |

---
## 6. Points techniques pour le développement
- Synchronisation mobile/web possible (API RESTful recommandée)
- Architecture sécurisée, gestion des accès par rôles
- Intégration mobile money, paiement par QR code
- Table de correspondance pour gestion des tarifs variables
- Exportation des données au format CSV, PDF et reporting

---
## 7. Annexes
- Modèle pour interface utilisateur (tableau de saisie, liste déroulante d’infractions)
- Définition des statuts de contravention (`en_attente`, `payée`, `contestée`, `recouvrement`)
- Logique d’escalade en cas de non-paiement (blocage permis, saisie véhicule)

---

Ce document est adapté pour une application métier destinée à la police routière à Madagascar (contravention numérique, enregistrement, paiement, reporting). Il pourra être enrichi lors de spécifications techniques complètes ou modélisation détaillée.