# Requirements Document - Tax Collector Citizen Mobile App

## Introduction

Ce document définit les exigences pour l'application mobile Tax Collector destinée aux citoyens et entreprises de Madagascar. L'application permettra aux utilisateurs d'enregistrer leurs véhicules, de calculer et payer leurs taxes annuelles, et de consulter leur historique de paiements via une interface mobile native développée en React Native.

## Glossaire

- **Système**: L'application mobile Tax Collector Citizen App (iOS et Android)
- **Utilisateur**: Citoyen ou entreprise propriétaire de véhicules
- **Backend**: L'API REST Django existante de la plateforme Tax Collector
- **Véhicule**: Véhicule terrestre enregistré dans le système
- **Taxe Annuelle**: Taxe obligatoire selon PLF 2026
- **QR Code**: Code de vérification généré après paiement
- **JWT**: JSON Web Token pour authentification
- **Offline Mode**: Mode hors ligne avec synchronisation différée
- **Push Notification**: Notification push native (iOS/Android)
- **Biométrie**: Touch ID (iOS) ou Fingerprint/Face Unlock (Android)

## Requirements

### Requirement 1

**User Story:** En tant qu'utilisateur, je veux créer un compte sur l'application mobile, afin d'accéder aux fonctionnalités de gestion de véhicules et de paiement de taxes.

#### Acceptance Criteria

1. WHEN l'utilisateur ouvre l'application pour la première fois, THE Système SHALL afficher un écran d'accueil avec les options "S'inscrire" et "Se connecter"
2. WHEN l'utilisateur sélectionne "S'inscrire", THE Système SHALL afficher un formulaire d'inscription avec les champs: type de compte (Particulier/Entreprise), prénom, nom, email, téléphone, mot de passe, confirmation mot de passe, et langue préférée (Français/Malagasy)
3. WHEN l'utilisateur soumet le formulaire d'inscription, THE Système SHALL valider que l'email est au format valide, que le téléphone est au format +261XXXXXXXXX, que le mot de passe contient au moins 8 caractères avec majuscules, minuscules et chiffres, et que les deux mots de passe correspondent
4. WHEN l'inscription est validée, THE Système SHALL envoyer une requête POST à l'API `/api/v1/auth/register/` et stocker le JWT token reçu de manière sécurisée dans le Keychain (iOS) ou Keystore (Android)
5. WHEN l'inscription réussit, THE Système SHALL envoyer un email de vérification à l'adresse fournie et afficher un message demandant à l'utilisateur de vérifier son email
6. WHEN l'utilisateur vérifie son email via le lien reçu, THE Système SHALL activer le compte et permettre l'accès complet à l'application
7. THE Système SHALL afficher des messages d'erreur clairs en cas d'échec (email déjà utilisé, téléphone invalide, mot de passe faible)

### Requirement 2

**User Story:** En tant qu'utilisateur, je veux me connecter à l'application avec mon email et mot de passe, afin d'accéder à mon compte et mes véhicules.

#### Acceptance Criteria

1. WHEN l'utilisateur sélectionne "Se connecter", THE Système SHALL afficher un formulaire avec les champs email et mot de passe
2. WHEN l'utilisateur soumet ses identifiants, THE Système SHALL envoyer une requête POST à `/api/token/` avec les credentials
3. WHEN l'authentification réussit, THE Système SHALL stocker le JWT access token (durée: 60 min) et refresh token (durée: 7 jours) de manière sécurisée
4. WHEN l'utilisateur a activé la biométrie, THE Système SHALL proposer l'authentification par Touch ID (iOS) ou Fingerprint/Face Unlock (Android) pour les connexions suivantes
5. WHEN le token expire, THE Système SHALL automatiquement utiliser le refresh token pour obtenir un nouveau access token via `/api/token/refresh/`
6. WHEN le refresh token expire, THE Système SHALL déconnecter l'utilisateur et afficher l'écran de connexion
7. THE Système SHALL afficher un message d'erreur clair en cas d'identifiants incorrects

### Requirement 3

**User Story:** En tant qu'utilisateur, je veux voir la liste de mes véhicules enregistrés, afin de consulter leur statut de paiement et gérer mes taxes.

#### Acceptance Criteria

1. WHEN l'utilisateur accède au dashboard après connexion, THE Système SHALL afficher la liste de ses véhicules via GET `/api/v1/vehicles/`
2. WHEN la liste est chargée, THE Système SHALL afficher pour chaque véhicule: la plaque d'immatriculation, la marque et modèle, une photo miniature si disponible, et le statut de paiement (Payé/Impayé/Expiré/Exonéré)
3. WHEN un véhicule a une taxe payée, THE Système SHALL afficher un badge vert "✓ Payé" avec la date d'expiration
4. WHEN un véhicule a une taxe impayée, THE Système SHALL afficher un badge orange "! À payer" avec le montant dû
5. WHEN un véhicule a une taxe expirée, THE Système SHALL afficher un badge rouge "✗ Expiré" avec le nombre de jours de retard
6. WHEN un véhicule est exonéré, THE Système SHALL afficher un badge bleu "ⓘ Exonéré"
7. THE Système SHALL permettre de tirer pour rafraîchir (pull-to-refresh) la liste des véhicules
8. THE Système SHALL afficher un message "Aucun véhicule enregistré" avec un bouton "Ajouter un véhicule" si la liste est vide

### Requirement 4

**User Story:** En tant qu'utilisateur, je veux ajouter un nouveau véhicule, afin de pouvoir payer sa taxe annuelle.

#### Acceptance Criteria

1. WHEN l'utilisateur clique sur "Ajouter un véhicule", THE Système SHALL afficher un formulaire multi-étapes avec navigation par onglets
2. WHEN l'utilisateur est à l'étape 1 "Informations de base", THE Système SHALL afficher les champs: plaque d'immatriculation, marque, modèle, couleur, VIN (optionnel), et une case à cocher "Véhicule sans plaque"
3. WHEN l'utilisateur coche "Véhicule sans plaque", THE Système SHALL désactiver le champ plaque et générer automatiquement un identifiant temporaire
4. WHEN l'utilisateur est à l'étape 2 "Spécifications techniques", THE Système SHALL afficher: type de véhicule (liste déroulante), puissance fiscale (CV), cylindrée (cm³), source d'énergie (Essence/Diesel/Électrique/Hybride), et date de première circulation
5. WHEN l'utilisateur saisit la cylindrée, THE Système SHALL suggérer automatiquement la puissance fiscale correspondante et afficher un message d'avertissement si la cohérence cylindrée/CV est douteuse
6. WHEN l'utilisateur est à l'étape 3 "Catégorie", THE Système SHALL afficher les catégories disponibles selon le type de compte (Personnel pour particuliers, Commercial pour entreprises)
7. WHEN l'utilisateur est à l'étape 4 "Documents" (optionnel), THE Système SHALL permettre de prendre des photos ou sélectionner des images de la carte grise (recto/verso), assurance, et contrôle technique
8. WHEN l'utilisateur soumet le formulaire, THE Système SHALL envoyer une requête POST à `/api/v1/vehicles/` avec toutes les données et les images compressées
9. WHEN l'ajout réussit, THE Système SHALL afficher un message de succès, calculer automatiquement le montant de la taxe, et proposer de payer immédiatement
10. THE Système SHALL valider que tous les champs obligatoires sont remplis avant de permettre la soumission

### Requirement 5

**User Story:** En tant qu'utilisateur, je veux consulter le montant de taxe à payer pour un véhicule, afin de connaître le coût avant de procéder au paiement.

#### Acceptance Criteria

1. WHEN l'utilisateur sélectionne un véhicule dans la liste, THE Système SHALL afficher l'écran de détails du véhicule
2. WHEN l'écran de détails se charge, THE Système SHALL appeler GET `/api/v1/tax-calculations/calculate/` avec les paramètres du véhicule
3. WHEN le calcul est reçu, THE Système SHALL afficher le montant de la taxe en gros caractères avec la devise (Ariary)
4. WHEN le véhicule est exonéré, THE Système SHALL afficher "EXONÉRÉ" avec l'explication de la catégorie d'exonération
5. THE Système SHALL afficher les détails du calcul: puissance fiscale (X CV), source d'énergie, âge du véhicule (Y ans), et grille tarifaire applicable
6. THE Système SHALL afficher la date limite de paiement (31 décembre de l'année en cours)
7. THE Système SHALL afficher un bouton "Payer maintenant" si le véhicule a une taxe à payer
8. THE Système SHALL afficher le QR code et le reçu si la taxe est déjà payée

### Requirement 6

**User Story:** En tant qu'utilisateur, je veux payer la taxe de mon véhicule via MVola, afin de régulariser ma situation fiscale rapidement.

#### Acceptance Criteria

1. WHEN l'utilisateur clique sur "Payer maintenant", THE Système SHALL afficher un écran de sélection de méthode de paiement avec les options: MVola, Carte bancaire (Stripe), et Espèces (Agent partenaire)
2. WHEN l'utilisateur sélectionne MVola, THE Système SHALL afficher un formulaire demandant le numéro de téléphone MVola (format +261XXXXXXXXX)
3. WHEN l'utilisateur soumet le numéro MVola, THE Système SHALL calculer et afficher le montant total incluant les frais de plateforme (3%) avec détail: Taxe + Frais = Total
4. WHEN l'utilisateur confirme, THE Système SHALL envoyer une requête POST à `/api/v1/payments/initiate/` avec method="mvola" et customer_msisdn
5. WHEN la requête est initiée, THE Système SHALL afficher un écran d'attente avec le message "Vérifiez votre téléphone MVola pour confirmer le paiement"
6. WHEN l'utilisateur confirme sur son téléphone MVola, THE Système SHALL recevoir la confirmation via polling de GET `/api/v1/payments/{id}/` toutes les 3 secondes
7. WHEN le paiement est confirmé, THE Système SHALL afficher un écran de succès avec le reçu, le QR code, et un bouton "Télécharger le reçu PDF"
8. WHEN le paiement échoue, THE Système SHALL afficher un message d'erreur clair avec la raison (solde insuffisant, timeout, annulation) et proposer de réessayer

### Requirement 7

**User Story:** En tant qu'utilisateur, je veux payer la taxe de mon véhicule par carte bancaire via Stripe, afin d'utiliser ma carte internationale.

#### Acceptance Criteria

1. WHEN l'utilisateur sélectionne "Carte bancaire", THE Système SHALL afficher un formulaire Stripe intégré pour saisir les informations de carte
2. WHEN l'utilisateur saisit les informations de carte, THE Système SHALL valider le format en temps réel (numéro de carte, date d'expiration, CVV)
3. WHEN l'utilisateur soumet le paiement, THE Système SHALL envoyer une requête POST à `/api/v1/payments/initiate/` avec method="stripe" et payment_method_id
4. WHEN le paiement nécessite 3D Secure, THE Système SHALL afficher la page de vérification 3D Secure dans une WebView
5. WHEN le paiement est confirmé, THE Système SHALL afficher l'écran de succès avec reçu et QR code
6. WHEN le paiement échoue, THE Système SHALL afficher un message d'erreur avec la raison (carte refusée, fonds insuffisants, erreur 3D Secure)

### Requirement 8

**User Story:** En tant qu'utilisateur, je veux voir le QR code de mon véhicule après paiement, afin de prouver que ma taxe est payée.

#### Acceptance Criteria

1. WHEN l'utilisateur consulte les détails d'un véhicule avec taxe payée, THE Système SHALL afficher le QR code de vérification
2. WHEN le QR code est affiché, THE Système SHALL montrer la date de génération et la date d'expiration
3. WHEN l'utilisateur tape sur le QR code, THE Système SHALL l'agrandir en plein écran pour faciliter la présentation aux agents
4. WHEN l'utilisateur consulte l'historique des paiements, THE Système SHALL afficher le QR code pour chaque paiement complété
5. WHEN l'utilisateur sélectionne un paiement dans l'historique, THE Système SHALL afficher le QR code avec les détails du paiement
6. THE Système SHALL permettre de partager le QR code via les applications de partage du système
7. THE Système SHALL permettre de sauvegarder le QR code dans la galerie de photos
8. WHEN le véhicule n'a pas de taxe payée, THE Système SHALL afficher un message "Aucun QR code disponible - Payez votre taxe pour obtenir un QR code"

### Requirement 9

**User Story:** En tant qu'utilisateur, je veux consulter l'historique de mes paiements, afin de suivre mes transactions et télécharger mes reçus.

#### Acceptance Criteria

1. WHEN l'utilisateur accède à "Historique", THE Système SHALL afficher la liste de tous les paiements via GET `/api/v1/payments/`
2. WHEN la liste est chargée, THE Système SHALL afficher pour chaque paiement: le véhicule concerné (plaque), le montant payé, la date de paiement, la méthode de paiement (icône MVola/Stripe/Cash), et le statut
3. WHEN l'utilisateur sélectionne un paiement, THE Système SHALL afficher les détails complets: numéro de transaction, date et heure exactes, montant détaillé (taxe + frais), méthode de paiement, et le QR code
4. WHEN l'utilisateur clique sur "Télécharger le reçu", THE Système SHALL télécharger le PDF via GET `/api/v1/payments/{id}/receipt/` et l'enregistrer dans la galerie ou le partager
5. THE Système SHALL permettre de filtrer l'historique par année fiscale et par véhicule
6. THE Système SHALL afficher un message "Aucun paiement effectué" si l'historique est vide

### Requirement 10

**User Story:** En tant qu'utilisateur, je veux recevoir des notifications push pour les rappels de paiement, afin de ne pas oublier de payer ma taxe avant l'échéance.

#### Acceptance Criteria

1. WHEN l'utilisateur installe l'application, THE Système SHALL demander la permission d'envoyer des notifications push
2. WHEN la permission est accordée, THE Système SHALL enregistrer le device token auprès du backend via POST `/api/v1/notifications/register-device/`
3. WHEN une notification push est reçue, THE Système SHALL l'afficher avec le titre, le message, et une icône appropriée
4. WHEN l'utilisateur tape sur une notification, THE Système SHALL ouvrir l'application et naviguer vers l'écran approprié (détails du véhicule, paiement, etc.)
5. THE Système SHALL recevoir des notifications pour: rappels de paiement (30j, 15j, 7j avant échéance), confirmation de paiement, expiration de taxe, et alertes importantes
6. THE Système SHALL permettre à l'utilisateur de gérer ses préférences de notifications dans les paramètres de l'application

### Requirement 11

**User Story:** En tant qu'utilisateur, je veux utiliser l'application en mode hors ligne, afin de consulter mes véhicules et préparer des paiements même sans connexion internet.

#### Acceptance Criteria

1. WHEN l'application détecte une perte de connexion, THE Système SHALL afficher un indicateur "Mode hors ligne" dans la barre de statut
2. WHEN l'utilisateur est hors ligne, THE Système SHALL permettre de consulter la liste des véhicules et l'historique des paiements depuis le cache local (AsyncStorage)
3. WHEN l'utilisateur est hors ligne, THE Système SHALL permettre de consulter les détails des véhicules et les reçus téléchargés précédemment
4. WHEN l'utilisateur tente d'effectuer une action nécessitant une connexion (paiement, ajout de véhicule), THE Système SHALL afficher un message "Cette action nécessite une connexion internet"
5. WHEN la connexion est rétablie, THE Système SHALL synchroniser automatiquement les données en arrière-plan et mettre à jour l'interface
6. THE Système SHALL afficher un indicateur de synchronisation pendant la mise à jour des données

### Requirement 12

**User Story:** En tant qu'utilisateur, je veux changer la langue de l'application entre Français et Malagasy, afin d'utiliser l'application dans ma langue préférée.

#### Acceptance Criteria

1. WHEN l'utilisateur accède aux paramètres, THE Système SHALL afficher une option "Langue / Fiteny" avec les choix Français et Malagasy
2. WHEN l'utilisateur change de langue, THE Système SHALL mettre à jour immédiatement tous les textes de l'interface dans la langue sélectionnée
3. WHEN l'utilisateur change de langue, THE Système SHALL enregistrer la préférence localement et l'envoyer au backend via PUT `/api/v1/users/me/`
4. WHEN l'application démarre, THE Système SHALL charger la langue préférée de l'utilisateur depuis le stockage local
5. THE Système SHALL afficher tous les textes, messages d'erreur, et notifications dans la langue sélectionnée

### Requirement 13

**User Story:** En tant qu'utilisateur, je veux voir mon profil et modifier mes informations personnelles, afin de maintenir mes données à jour.

#### Acceptance Criteria

1. WHEN l'utilisateur accède à "Profil", THE Système SHALL afficher ses informations: photo de profil, nom complet, email, téléphone, type de compte, et langue préférée
2. WHEN l'utilisateur clique sur "Modifier", THE Système SHALL afficher un formulaire pré-rempli avec ses informations actuelles
3. WHEN l'utilisateur modifie ses informations, THE Système SHALL valider les champs (email valide, téléphone valide) avant de permettre la sauvegarde
4. WHEN l'utilisateur sauvegarde, THE Système SHALL envoyer une requête PUT à `/api/v1/users/me/` avec les nouvelles données
5. WHEN la mise à jour réussit, THE Système SHALL afficher un message de confirmation et mettre à jour l'interface
6. THE Système SHALL permettre de changer la photo de profil en prenant une photo ou en sélectionnant depuis la galerie

### Requirement 14

**User Story:** En tant qu'utilisateur, je veux me déconnecter de l'application, afin de sécuriser mon compte sur un appareil partagé.

#### Acceptance Criteria

1. WHEN l'utilisateur sélectionne "Se déconnecter" dans les paramètres, THE Système SHALL afficher une confirmation "Êtes-vous sûr de vouloir vous déconnecter ?"
2. WHEN l'utilisateur confirme, THE Système SHALL envoyer une requête POST à `/api/v1/auth/logout/` pour invalider le token
3. WHEN la déconnexion est confirmée, THE Système SHALL supprimer tous les tokens JWT du stockage sécurisé
4. WHEN la déconnexion est confirmée, THE Système SHALL effacer toutes les données en cache (véhicules, paiements, profil)
5. WHEN la déconnexion est complète, THE Système SHALL rediriger l'utilisateur vers l'écran de connexion
6. THE Système SHALL désactiver la biométrie pour les connexions futures jusqu'à ce que l'utilisateur se reconnecte et la réactive

### Requirement 15

**User Story:** En tant qu'utilisateur, je veux que l'application soit performante et réactive, afin d'avoir une expérience utilisateur fluide.

#### Acceptance Criteria

1. WHEN l'application démarre, THE Système SHALL afficher l'écran d'accueil en moins de 2 secondes
2. WHEN l'utilisateur navigue entre les écrans, THE Système SHALL afficher le nouvel écran en moins de 300 millisecondes
3. WHEN l'utilisateur charge la liste des véhicules, THE Système SHALL afficher les données en moins de 3 secondes
4. WHEN l'utilisateur effectue une recherche ou un filtrage, THE Système SHALL afficher les résultats en moins de 500 millisecondes
5. THE Système SHALL compresser les images avant upload pour réduire la consommation de données mobiles
6. THE Système SHALL utiliser le cache local pour afficher immédiatement les données précédemment chargées pendant le chargement des nouvelles données
7. THE Système SHALL afficher des indicateurs de chargement (spinners, skeletons) pendant les opérations longues
8. THE Système SHALL optimiser la consommation de batterie en limitant les requêtes en arrière-plan

