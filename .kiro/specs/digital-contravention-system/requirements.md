# Requirements Document - Système de Contravention Numérique

## Introduction

Ce document définit les exigences pour un système de gestion des contraventions et infractions routières à Madagascar, intégré à la plateforme existante de taxation des véhicules. Le système permettra aux agents de police et de gendarmerie d'enregistrer des infractions, d'émettre des contraventions numériques, et de gérer les paiements d'amendes via les méthodes de paiement existantes (MVola, espèces, cartes bancaires).

## Glossaire

- **Système**: Le système de contravention numérique intégré à la plateforme TaxCollector
- **Agent Contrôleur**: Policier ou gendarme autorisé à constater des infractions et émettre des contraventions
- **Contravention**: Procès-verbal d'infraction routière émis par un agent contrôleur
- **Infraction**: Violation du Code de la Route Malagasy (Loi n°2017-002 du 6 juillet 2017)
- **Conducteur**: Personne physique conduisant un véhicule au moment de l'infraction
- **Véhicule**: Véhicule terrestre enregistré dans le système (référence au modèle Vehicule existant)
- **Amende**: Montant financier à payer suite à une contravention
- **PV Électronique**: Procès-verbal numérique généré par le système
- **QR Code de Contravention**: Code QR unique permettant la vérification et le paiement d'une contravention
- **Fourrière**: Lieu de mise en dépôt des véhicules saisis
- **Récidive**: Nouvelle infraction commise par un conducteur ayant déjà été sanctionné dans les 12 derniers mois
- **Article de Loi**: Référence légale du Code de la Route (format: L7.X-Y)
- **Montant Variable**: Amende dont le montant est déterminé par l'autorité compétente selon les circonstances
- **Sanction Administrative**: Mesure complémentaire à l'amende (suspension permis, immobilisation, emprisonnement)
- **Aggravation**: Augmentation de l'amende ou de la sanction en cas d'accident ou de récidive
- **Délai de Paiement**: Période accordée pour régler l'amende avant application de pénalités

## Requirements

### Requirement 1

**User Story:** En tant qu'administrateur système, je veux configurer les types d'infractions et leurs sanctions conformément à la Loi n°2017-002, afin que les agents contrôleurs puissent émettre des contraventions légalement valides.

#### Acceptance Criteria

1. WHEN l'administrateur accède à l'interface de gestion des infractions, THE Système SHALL afficher la liste complète des types d'infractions organisés par catégorie (Délits graves, Infractions de circulation, Infractions documentaires, Infractions de sécurité)
2. WHEN l'administrateur crée un nouveau type d'infraction, THE Système SHALL enregistrer le nom de l'infraction, l'article du Code de la Route (format L7.X-Y), la loi applicable, le montant minimum d'amende, le montant maximum d'amende, l'indicateur de montant variable, les sanctions administratives possibles, et l'indicateur de fourrière obligatoire
3. WHEN l'administrateur configure une infraction avec montant variable, THE Système SHALL permettre de définir des montants par défaut pour chaque autorité compétente (Police nationale, Police communale, Gendarmerie)
4. WHEN l'administrateur configure les aggravations, THE Système SHALL permettre de définir les pénalités en cas d'accident et en cas de récidive pour chaque type d'infraction
5. WHEN l'administrateur modifie un type d'infraction existant, THE Système SHALL conserver l'historique des modifications avec la date, l'utilisateur, et les valeurs avant/après modification
6. WHEN l'administrateur désactive un type d'infraction, THE Système SHALL empêcher son utilisation pour de nouvelles contraventions tout en préservant les contraventions existantes
7. THE Système SHALL valider que le montant minimum d'amende est inférieur ou égal au montant maximum pour chaque type d'infraction
8. THE Système SHALL pré-charger les 24 types d'infractions définis dans la Loi n°2017-002 lors de l'initialisation du système

### Requirement 2

**User Story:** En tant qu'administrateur système, je veux créer et gérer des profils d'agents contrôleurs, afin que seuls les agents autorisés puissent émettre des contraventions.

#### Acceptance Criteria

1. WHEN l'administrateur crée un profil d'agent contrôleur, THE Système SHALL enregistrer le matricule unique, le nom complet, l'unité d'affectation, le grade, et les informations de contact de l'agent
2. WHEN l'administrateur associe un compte utilisateur à un profil d'agent contrôleur, THE Système SHALL créer automatiquement les permissions nécessaires pour accéder au module de contravention
3. WHEN un agent contrôleur se connecte au système, THE Système SHALL vérifier que son profil est actif et que ses permissions sont valides
4. WHEN l'administrateur désactive un profil d'agent contrôleur, THE Système SHALL bloquer l'accès au module de contravention pour cet agent tout en conservant l'historique de ses contraventions émises
5. THE Système SHALL permettre à l'administrateur de consulter les statistiques d'activité de chaque agent contrôleur incluant le nombre de contraventions émises et le montant total des amendes

### Requirement 3

**User Story:** En tant qu'agent contrôleur, je veux enregistrer une infraction constatée sur le terrain, afin de générer une contravention numérique conforme au Code de la Route avec calcul automatique de l'amende.

#### Acceptance Criteria

1. WHEN l'agent contrôleur accède au formulaire de création de contravention, THE Système SHALL afficher la liste des types d'infractions actives organisées par catégorie avec leurs articles de loi
2. WHEN l'agent contrôleur sélectionne un type d'infraction, THE Système SHALL afficher automatiquement l'article de loi, la fourchette d'amende, les sanctions administratives associées, et l'indicateur de fourrière obligatoire
3. WHEN l'infraction sélectionnée a un montant variable, THE Système SHALL afficher le montant par défaut selon l'autorité de l'agent contrôleur et permettre l'ajustement dans la fourchette légale
4. WHEN l'agent contrôleur saisit la plaque d'immatriculation du véhicule, THE Système SHALL rechercher le véhicule dans la base de données et pré-remplir les informations du véhicule et du propriétaire si trouvé
5. WHEN l'agent contrôleur enregistre les informations du conducteur, THE Système SHALL valider le format du numéro de CIN (12 chiffres) et du numéro de permis de conduire
6. WHEN l'agent contrôleur indique qu'un accident est associé à l'infraction, THE Système SHALL appliquer automatiquement la pénalité d'aggravation pour accident si définie pour ce type d'infraction
7. WHEN le système détecte une récidive pour le même conducteur dans les 12 derniers mois, THE Système SHALL appliquer automatiquement la pénalité de récidive et afficher un avertissement à l'agent
8. WHEN l'agent contrôleur enregistre la localisation de l'infraction, THE Système SHALL capturer les coordonnées GPS si disponibles et permettre la saisie manuelle de l'adresse avec indication de la route nationale ou communale
9. WHEN l'agent contrôleur valide la contravention, THE Système SHALL générer un numéro unique de PV (format: PV-YYYYMMDD-XXXXXX), créer un QR code de vérification, calculer le délai de paiement (15 jours par défaut), et enregistrer la date et l'heure exactes de l'infraction
10. WHEN la contravention est créée, THE Système SHALL envoyer une notification au propriétaire du véhicule si ses coordonnées sont disponibles dans le système avec lien vers les détails de la contravention

### Requirement 4

**User Story:** En tant qu'agent contrôleur, je veux consulter l'historique des infractions d'un conducteur ou d'un véhicule, afin d'identifier les récidives et appliquer les sanctions appropriées.

#### Acceptance Criteria

1. WHEN l'agent contrôleur recherche un conducteur par son numéro de CIN ou de permis, THE Système SHALL afficher la liste de toutes les contraventions associées à ce conducteur avec leur statut de paiement
2. WHEN l'agent contrôleur recherche un véhicule par sa plaque d'immatriculation, THE Système SHALL afficher la liste de toutes les contraventions associées à ce véhicule avec leur statut de paiement
3. WHEN le système détecte une récidive pour une même infraction dans les 12 derniers mois, THE Système SHALL afficher un avertissement à l'agent contrôleur et suggérer l'application de sanctions renforcées
4. THE Système SHALL calculer et afficher le nombre total d'infractions impayées pour un conducteur ou un véhicule
5. THE Système SHALL permettre à l'agent contrôleur de filtrer l'historique par type d'infraction, période, et statut de paiement

### Requirement 5

**User Story:** En tant que conducteur sanctionné, je veux consulter les détails de ma contravention via le QR code ou le numéro de PV, afin de comprendre l'infraction commise et le montant à payer.

#### Acceptance Criteria

1. WHEN le conducteur scanne le QR code de la contravention avec son smartphone, THE Système SHALL afficher une page web contenant tous les détails de la contravention sans nécessiter d'authentification
2. WHEN le conducteur saisit le numéro de PV dans le portail public, THE Système SHALL afficher les détails de la contravention après validation du numéro
3. THE Système SHALL afficher le type d'infraction, la date et l'heure, le lieu, le montant de l'amende, les sanctions complémentaires, et le délai de paiement
4. THE Système SHALL afficher le statut de paiement actuel de la contravention avec indication claire si elle est payée, impayée, ou en attente
5. WHEN la contravention est impayée, THE Système SHALL afficher les options de paiement disponibles avec des liens directs vers les interfaces de paiement

### Requirement 6

**User Story:** En tant que conducteur sanctionné, je veux payer mon amende en ligne via MVola, carte bancaire ou espèces auprès d'un agent partenaire, afin de régulariser ma situation rapidement.

#### Acceptance Criteria

1. WHEN le conducteur sélectionne le paiement par MVola, THE Système SHALL utiliser l'intégration MVola existante pour initier une transaction de paiement d'amende
2. WHEN le conducteur sélectionne le paiement par carte bancaire, THE Système SHALL utiliser l'intégration Stripe existante pour traiter le paiement de l'amende
3. WHEN le conducteur se présente chez un agent partenaire pour payer en espèces, THE Système SHALL permettre à l'agent partenaire de rechercher la contravention et d'enregistrer le paiement via le module de paiement en espèces existant
4. WHEN un paiement d'amende est confirmé, THE Système SHALL mettre à jour automatiquement le statut de la contravention à "Payée" et enregistrer la date et l'heure du paiement
5. WHEN un paiement d'amende est confirmé, THE Système SHALL générer un reçu de paiement avec QR code de vérification et l'envoyer au conducteur par email si disponible
6. THE Système SHALL appliquer les frais de plateforme appropriés selon la méthode de paiement choisie conformément aux configurations existantes

### Requirement 7

**User Story:** En tant qu'agent contrôleur, je veux enregistrer une mise en fourrière d'un véhicule, afin de documenter la saisie du véhicule et calculer les frais de fourrière applicables.

#### Acceptance Criteria

1. WHEN l'agent contrôleur enregistre une mise en fourrière lors de la création d'une contravention, THE Système SHALL créer automatiquement un dossier de fourrière lié à la contravention
2. WHEN le système crée un dossier de fourrière, THE Système SHALL enregistrer la date et l'heure de mise en fourrière, le lieu de la fourrière, et le motif de la saisie
3. WHEN le système calcule les frais de fourrière, THE Système SHALL appliquer les tarifs configurés pour le transport et le gardiennage selon le type de véhicule
4. THE Système SHALL calculer automatiquement les frais de gardiennage en fonction du nombre de jours écoulés depuis la mise en fourrière
5. WHEN le propriétaire souhaite récupérer son véhicule, THE Système SHALL afficher le montant total à payer incluant l'amende de la contravention et les frais de fourrière
6. WHEN tous les paiements sont effectués, THE Système SHALL générer un bon de sortie de fourrière avec QR code de vérification

### Requirement 8

**User Story:** En tant qu'administrateur de la police, je veux consulter des rapports statistiques sur les contraventions, afin d'analyser les tendances des infractions et l'efficacité des contrôles.

#### Acceptance Criteria

1. WHEN l'administrateur accède au tableau de bord des contraventions, THE Système SHALL afficher le nombre total de contraventions émises, le taux de paiement, et le montant total collecté pour la période sélectionnée
2. WHEN l'administrateur génère un rapport par type d'infraction, THE Système SHALL afficher le nombre de contraventions par type avec répartition géographique et temporelle
3. WHEN l'administrateur génère un rapport par agent contrôleur, THE Système SHALL afficher les statistiques d'activité de chaque agent incluant le nombre de contraventions émises et le taux de paiement
4. WHEN l'administrateur génère un rapport de recouvrement, THE Système SHALL afficher la liste des contraventions impayées avec ancienneté et montant total des créances
5. THE Système SHALL permettre l'exportation de tous les rapports au format PDF et Excel
6. THE Système SHALL permettre de filtrer les rapports par période, région, type d'infraction, et agent contrôleur

### Requirement 9

**User Story:** En tant qu'administrateur système, je veux configurer les tarifs de fourrière et les délais de paiement conformément aux réglementations, afin d'assurer la conformité légale du système.

#### Acceptance Criteria

1. WHEN l'administrateur configure les tarifs de fourrière, THE Système SHALL permettre de définir le tarif de transport (défaut: 20 000 Ariary) et le tarif de gardiennage journalier (défaut: 10 000 Ariary) selon le type de véhicule
2. WHEN l'administrateur configure les durées minimales de fourrière, THE Système SHALL permettre de définir une durée minimale pour véhicules non périssables (défaut: 10 jours) et pour produits périssables (défaut: 5 jours)
3. WHEN l'administrateur configure les délais de paiement, THE Système SHALL permettre de définir un délai standard (défaut: 15 jours), un délai immédiat pour infractions mineures, et un délai avant jugement pour délits graves
4. WHEN l'administrateur configure les pénalités de retard, THE Système SHALL permettre de définir un pourcentage de majoration applicable après le délai standard avec minimum et maximum
5. THE Système SHALL appliquer automatiquement les pénalités de retard aux contraventions impayées après expiration du délai standard
6. THE Système SHALL calculer automatiquement le montant total de fourrière en additionnant les frais de transport et les frais de gardiennage selon le nombre de jours écoulés
7. WHEN un véhicule est en fourrière depuis la durée minimale, THE Système SHALL permettre sa restitution uniquement après paiement complet de l'amende et des frais de fourrière

### Requirement 10

**User Story:** En tant que système, je veux enregistrer un journal d'audit complet de toutes les opérations de contravention, afin de garantir la traçabilité et la transparence des actions.

#### Acceptance Criteria

1. WHEN un agent contrôleur crée une contravention, THE Système SHALL enregistrer dans le journal d'audit l'identité de l'agent, la date et l'heure, l'adresse IP, et toutes les données de la contravention
2. WHEN une contravention est modifiée, THE Système SHALL enregistrer dans le journal d'audit les données avant et après modification avec l'identité de l'utilisateur ayant effectué la modification
3. WHEN un paiement d'amende est effectué, THE Système SHALL enregistrer dans le journal d'audit tous les détails de la transaction incluant la méthode de paiement et le montant
4. WHEN une contravention est annulée, THE Système SHALL enregistrer dans le journal d'audit le motif d'annulation et l'identité de l'utilisateur ayant effectué l'annulation
5. THE Système SHALL garantir l'immuabilité du journal d'audit en utilisant un mécanisme de chaînage cryptographique similaire au modèle CashAuditLog existant
6. THE Système SHALL permettre aux administrateurs autorisés de consulter le journal d'audit avec filtres par utilisateur, type d'action, et période

### Requirement 11

**User Story:** En tant qu'agent contrôleur, je veux contester ou annuler une contravention en cas d'erreur, afin de corriger les erreurs de saisie ou les contraventions émises par erreur.

#### Acceptance Criteria

1. WHEN l'agent contrôleur demande l'annulation d'une contravention dans les 24 heures suivant sa création, THE Système SHALL permettre l'annulation directe avec saisie obligatoire d'un motif
2. WHEN l'agent contrôleur demande l'annulation d'une contravention après 24 heures, THE Système SHALL soumettre la demande à validation par un superviseur
3. WHEN un superviseur valide une demande d'annulation, THE Système SHALL annuler la contravention, mettre à jour son statut, et enregistrer l'action dans le journal d'audit
4. WHEN une contravention est annulée après paiement, THE Système SHALL initier automatiquement un processus de remboursement et notifier le conducteur
5. THE Système SHALL empêcher l'annulation d'une contravention si le véhicule est en fourrière sans validation d'un administrateur de niveau supérieur

### Requirement 12

**User Story:** En tant que conducteur, je veux contester une contravention que je juge injustifiée, afin de faire valoir mes droits et obtenir une révision de la sanction.

#### Acceptance Criteria

1. WHEN le conducteur accède aux détails de sa contravention, THE Système SHALL afficher un bouton "Contester cette contravention" si le délai de contestation n'est pas expiré
2. WHEN le conducteur soumet une contestation, THE Système SHALL permettre la saisie d'un motif détaillé et le téléchargement de documents justificatifs
3. WHEN une contestation est soumise, THE Système SHALL suspendre automatiquement le délai de paiement et notifier l'agent contrôleur ayant émis la contravention
4. WHEN un superviseur examine une contestation, THE Système SHALL afficher tous les éléments de la contravention, les justificatifs du conducteur, et permettre une décision motivée
5. WHEN une contestation est acceptée, THE Système SHALL annuler la contravention et notifier le conducteur
6. WHEN une contestation est rejetée, THE Système SHALL réactiver le délai de paiement avec notification au conducteur et possibilité de recours administratif

### Requirement 13

**User Story:** En tant que système, je veux m'intégrer avec le système de véhicules existant, afin d'utiliser les données des véhicules et propriétaires déjà enregistrés.

#### Acceptance Criteria

1. WHEN l'agent contrôleur saisit une plaque d'immatriculation, THE Système SHALL interroger le modèle Vehicule existant pour récupérer les informations du véhicule
2. WHEN un véhicule est trouvé dans le système, THE Système SHALL pré-remplir automatiquement la marque, le modèle, la couleur, et les informations du propriétaire
3. WHEN le propriétaire du véhicule a un compte utilisateur dans le système, THE Système SHALL utiliser ses coordonnées pour l'envoi de notifications
4. THE Système SHALL permettre la création de contraventions pour des véhicules non enregistrés dans le système avec saisie manuelle des informations
5. THE Système SHALL créer un lien bidirectionnel entre les contraventions et les véhicules permettant de consulter les contraventions depuis la fiche véhicule

### Requirement 14

**User Story:** En tant que système, je veux m'intégrer avec le système de paiement existant, afin de réutiliser les méthodes de paiement et les configurations déjà en place.

#### Acceptance Criteria

1. WHEN un paiement d'amende est initié, THE Système SHALL créer un enregistrement PaiementTaxe avec un type spécifique "amende_contravention" pour différencier des paiements de taxe véhicule
2. WHEN un paiement MVola est effectué pour une amende, THE Système SHALL utiliser le modèle MvolaConfiguration actif et appliquer les frais de plateforme configurés
3. WHEN un paiement en espèces est effectué pour une amende, THE Système SHALL utiliser le système de CashSession et CashTransaction existant avec calcul de commission pour l'agent partenaire
4. WHEN un paiement par carte bancaire est effectué pour une amende, THE Système SHALL utiliser l'intégration Stripe existante avec la configuration active
5. THE Système SHALL générer un QRCode de vérification pour chaque contravention payée en utilisant le modèle QRCode existant
6. THE Système SHALL permettre la consultation de l'historique des paiements d'amendes via l'interface de gestion des paiements existante

### Requirement 15

**User Story:** En tant qu'agent contrôleur mobile, je veux utiliser l'application sur smartphone ou tablette via l'API REST, afin d'émettre des contraventions directement sur le terrain avec authentification JWT.

#### Acceptance Criteria

1. WHEN l'agent contrôleur se connecte à l'application mobile, THE Système SHALL authentifier l'agent via JWT (JSON Web Token) avec durée de validité de 60 minutes
2. WHEN l'agent contrôleur crée une contravention via l'API mobile, THE Système SHALL valider les données et générer automatiquement le numéro PV, le QR code et calculer le montant avec aggravations
3. WHEN l'agent contrôleur crée une contravention via l'API mobile, THE Système SHALL capturer automatiquement les coordonnées GPS et l'horodatage de l'appareil
4. THE Système SHALL permettre la capture de photos du véhicule et de l'infraction via l'API avec compression automatique des images côté serveur
5. THE Système SHALL permettre la signature électronique du conducteur transmise en base64 via l'API
6. WHEN l'agent contrôleur consulte ses contraventions via l'API, THE Système SHALL retourner la liste filtrée par agent avec pagination et recherche
7. THE Système SHALL fournir des endpoints API pour recherche de véhicules, conducteurs, et vérification de récidives en temps réel
8. WHEN l'agent contrôleur upload une photo via l'API, THE Système SHALL valider la taille maximale de 5 mégaoctets et le format (JPEG, PNG, WEBP) avant acceptation

### Requirement 16

**User Story:** En tant qu'administrateur système, je veux importer les 24 types d'infractions de la Loi n°2017-002 dans le système, afin de disposer d'une base de données conforme au Code de la Route Malagasy.

#### Acceptance Criteria

1. WHEN l'administrateur exécute la commande d'import des infractions, THE Système SHALL créer automatiquement les 24 types d'infractions définis dans la Loi n°2017-002 avec leurs articles, montants, et sanctions
2. THE Système SHALL organiser les infractions en 4 catégories principales: Délits routiers graves (7 types), Infractions de circulation (7 types), Infractions documentaires (6 types), et Infractions de sécurité (4 types)
3. THE Système SHALL enregistrer pour chaque infraction l'article du Code de la Route (format L7.X-Y), la référence à la Loi n°2017-002, le montant minimum et maximum d'amende en Ariary, et les sanctions administratives textuelles
4. WHEN une infraction a un montant variable selon l'autorité, THE Système SHALL marquer l'infraction avec un indicateur "montant_variable" et permettre la configuration ultérieure des montants par autorité
5. WHEN une infraction nécessite une mise en fourrière obligatoire, THE Système SHALL marquer l'infraction avec un indicateur "fourriere_obligatoire"
6. THE Système SHALL permettre l'export de la liste des infractions au format CSV et PDF pour consultation et audit
7. WHEN l'administrateur met à jour une infraction importée, THE Système SHALL conserver la référence légale originale et marquer l'infraction comme "modifiée" avec traçabilité

### Requirement 17

**User Story:** En tant qu'agent contrôleur, je veux capturer des photos et preuves de l'infraction, afin de documenter visuellement la contravention et faciliter la contestation éventuelle.

#### Acceptance Criteria

1. WHEN l'agent contrôleur crée une contravention, THE Système SHALL permettre la capture de jusqu'à 5 photos via l'appareil photo du smartphone ou le téléchargement de fichiers
2. WHEN une photo est capturée ou téléchargée, THE Système SHALL compresser automatiquement l'image en utilisant le module ImageOptimizer existant avec qualité optimale pour documents officiels
3. WHEN une photo est enregistrée, THE Système SHALL extraire et enregistrer les métadonnées EXIF incluant la date, l'heure, et les coordonnées GPS si disponibles
4. THE Système SHALL permettre l'annotation des photos avec des marqueurs et du texte pour identifier les éléments clés de l'infraction
5. THE Système SHALL stocker les photos dans un emplacement sécurisé avec lien vers la contravention et garantir leur intégrité via un hash cryptographique
6. WHEN le conducteur ou un superviseur consulte la contravention, THE Système SHALL afficher les photos associées avec leurs métadonnées et annotations
7. THE Système SHALL permettre le téléchargement des photos originales uniquement aux utilisateurs autorisés (agent émetteur, superviseurs, administrateurs)
