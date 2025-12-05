# Tableau des infractions routières, amendes et références légales - Madagascar

## Document de base pour l'application de contravention numérique

---

## 1. Tableau complet avec références légales

| Type d'infraction | Article(s) | Loi applicable | Montant de l'amende (Ariary) | Sanctions administratives |
|---|---|---|---|---|
| **DÉLITS ROUTIERS GRAVES** | | | | |
| Conduite en état d'ivresse ou stupéfiants | L7.1-1 | Loi n°2017-002 | 100 000 - 400 000 | Suspension/retrait permis, immobilisation véhicule |
| Refus de vérification (alcoolémie) | L7.1-2 | Loi n°2017-002 | 200 000 - 800 000 | Retrait/suspension permis, immobilisation |
| Conduite sans permis en état d'ivresse | L7.1-3 | Loi n°2017-002 | 200 000 - 800 000 | Emprisonnement 1-12 mois, interdiction permis |
| Délit de fuite (accident) | L7.1-5 | Loi n°2017-002 | 500 000 - 2 000 000 | Emprisonnement 2-12 mois, retrait permis |
| Refus d'obtempérer aux ordres | L7.1-7 | Loi n°2017-002 | 200 000 - 800 000 | Retrait/suspension permis, immobilisation |
| **INFRACTIONS DE CIRCULATION** | | | | |
| Non-respect distance de sécurité | L7.2-4 | Loi n°2017-002 | 200 000 - 800 000 | Suspension permis si accident corporel |
| Excès de vitesse | L7.2-5 | Loi n°2017-002 | 200 000 - 800 000 | Retrait/suspension permis |
| Course/compétition non autorisée | L7.2-6 | Loi n°2017-002 | 400 000 - 800 000 | Emprisonnement 1-6 mois possible |
| Mise en danger d'autrui | L7.2-3 | Loi n°2017-002 | 200 000 - 1 500 000 | Emprisonnement 1-6 mois possible |
| Obstacle sur voie publique | L7.2-3 | Loi n°2017-002 | 200 000 - 1 500 000 | Emprisonnement 3-24 mois possible |
| Violation feux rouges/signalisation | L7.1-1, L7.2-1 | Loi n°2017-002 | Variable selon autorité | Mise en fourrière possible |
| Destruction patrimoine routier | L7.2-3 | Loi n°2017-002 | 200 000 - 800 000 | Application Code pénal art. 473-474 |
| Chargement mal arrimé/débordant | L7.2-8 | Loi n°2017-002 | Variable selon autorité | Avertissement/immobilisation |
| **INFRACTIONS DOCUMENTAIRES** | | | | |
| Défaut de carte grise | L7.4-1 | Loi n°2017-002 | Variable selon autorité | Mise en fourrière 10 jours minimum |
| Défaut de permis de conduire | L7.5-1 | Loi n°2017-002 | Variable selon autorité | Mise en fourrière + poursuites pénales |
| Défaut d'assurance | L7.4-5 | Loi n°2017-002 | 100 000 - 500 000 (1 M si accident) | Mise en fourrière, retrait permis si accident |
| Défaut de visite technique | L7.4-1 | Loi n°2017-002 | Variable selon autorité | Mise en fourrière |
| Conduite sans permis valable | L7.5-1 | Loi n°2017-002 | 500 000 - 1 500 000 | Emprisonnement 1-6 mois si récidive |
| Utilisation de faux papiers | L7.4-2 | Loi n°2017-002 | Variable selon autorité | Emprisonnement 6 mois - 2 ans possible |
| **INFRACTIONS DE SÉCURITÉ** | | | | |
| Non-port du casque (moto) | L7.6-1 | Loi n°2017-002 | Jusqu'à 6 000 | Avertissement/immobilisation |
| Non-port ceinture de sécurité | L7.6-2 | Loi n°2017-002 | Variable selon autorité | Avertissement |
| Modifications illégales du véhicule | L7.4-2 | Loi n°2017-002 | Jusqu'à 100 000 | Immobilisation du véhicule |
| Stationnement interdit | L7.2-7 (communes) | Loi n°2017-002 | 12 000 - 600 000 | Immobilisation par taquets d'arrêt |

---

## 2. Référence légale complète

**Loi n° 2017-002 du 6 juillet 2017 portant Code de la Route à Madagascar**

Cette loi abroge et remplace la Loi n° 2004-031 du 25 juillet 2004. Elle s'articule autour de plusieurs chapitres de répression (Chapitre 7 divisé en 7.1 à 7.6) selon le type d'infraction :

- **Chapitre 7.1** : Répression des infractions relatives à la conduite sous influence ou refus de vérification
- **Chapitre 7.2** : Répression des infractions relatives aux règles de l'usage des voies publiques
- **Chapitre 7.3** : Infractions techniquement interdites (plaques frauduleuses, etc.)
- **Chapitre 7.4** : Infractions documentaires et conditions administratives
- **Chapitre 7.5** : Infractions liées au permis de conduire
- **Chapitre 7.6** : Infractions de sécurité (casque, ceinture, extincteur, etc.)

---

## 3. Principes d'application des amendes

### 3.1 Montants variables selon autorité
Certaines infractions sont soumises à un montant **variable selon l'autorité compétente**. Pour standardiser, il est recommandé :
- Établir un tableau de tarification par autorité (Police commune, Police de circulation, autorités communales)
- Utiliser les montants minimums définies dans le code pour les infractions sans montant précis

### 3.2 Aggravations
- **En cas d'accident** : Les montants peuvent être augmentés (exemple : défaut d'assurance passe de 100 000-500 000 Ar à 1 000 000 Ar)
- **En cas de récidive** : Ajout possible d'emprisonnement (1 à 6 mois) ou doublement de l'amende

### 3.3 Frais supplémentaires
- **Mise en fourrière** : 20 000 Ar (transport) + 10 000 Ar/jour de gardiennage (durée minimale 10 jours)
- **Total estimé** : Environ 120 000 Ar pour 10 jours de fourrière

---

## 4. Structure pour intégration dans l'application numérique

### Base de données recommandée :

```
TABLE infractions_types (
  id INT PRIMARY KEY,
  type_infraction VARCHAR(255),
  article_code VARCHAR(50),
  loi_numero VARCHAR(50),
  montant_min INT,
  montant_max INT,
  montant_variable BOOLEAN,
  emprisonnement_possible VARCHAR(100),
  sanction_administrative VARCHAR(255),
  fourriere_obligatoire BOOLEAN,
  penalite_accident INT,
  penalite_recidive INT
)

TABLE contraventions (
  id INT PRIMARY KEY,
  date_heure TIMESTAMP,
  lieu VARCHAR(255),
  policier_id INT,
  conducteur_id INT,
  vehicule_id INT,
  infraction_type_id INT,
  montant_applique INT,
  status_paiement ENUM('impayée', 'payée', 'contestée'),
  mode_paiement VARCHAR(50),
  code_qr VARCHAR(255),
  FOREIGN KEY (infraction_type_id) REFERENCES infractions_types(id)
)
```

---

## 5. Modalités de paiement

### 5.1 Modes acceptés
- Mobile money (Airtel Money, Orange Money, Vonage)
- Carte bancaire (via passerelle de paiement sécurisée)
- Espèces (avec émission d'un reçu QR code)

### 5.2 Délai de paiement
- **Immédiat** : idéal pour les infractions mineures (stationnement, ceinture)
- **Sous 15 jours** : infractions graves documentées
- **Avant jugement** : délits (ivresse, fuite)

---

## 6. Notes importantes pour développeurs

1. **Sécurité** : Chiffrement des données sensibles, authentification forte pour policiers
2. **Traçabilité** : Chaque amende doit être liée à un agent, avec horodatage
3. **Synchronisation** : Compatible avec les bases de données de l'État (CNI, permis, immatriculation)
4. **Reporting** : Dashboards statistiques par zone, par type d'infraction, par mois
5. **Conformité légale** : Respect de la signature électronique et des procédures administratives

---

## 7. Exemple d'enregistrement d'infraction

**Police : Agent ABC (ID: 001)**
- Infraction : Excès de vitesse
- Article : L7.2-5
- Loi : n°2017-002
- Montant appliqué : 400 000 Ar (fourchette 200k-800k)
- Lieu : Route nationale n°1, km 25
- Heure : 14h30
- Conducteur : Ramanantenaina Jean
- Véhicule : Taxi brousse ABC-123
- Mode de paiement proposé : Mobile money
- Code QR généré : [QR_20251112_00001]

---

Ce document constitue la **base documentaire légale et fonctionnelle** pour développer l'application de contravention numérique à Madagascar, conforme à la Loi n°2017-002 Code de la Route.