# Plan d'Organisation: Types d'Utilisateurs et Catégories d'Exonération

**Version:** 1.0  
**Date:** Décembre 2024  
**Projet:** Plateforme de Collecte de Taxe sur les Véhicules - Madagascar

---

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Types d'Utilisateurs Réorganisés](#types-dutilisateurs-réorganisés)
3. [Catégories d'Exonération selon la Loi](#catégories-dexonération-selon-la-loi)
4. [Plan de Refactorisation](#plan-de-refactorisation)
5. [Corrections Nécessaires](#corrections-nécessaires)
6. [Migration des Données](#migration-des-données)
7. [Tests et Validation](#tests-et-validation)

---

## Vue d'ensemble

Ce document organise:
1. **Les types d'utilisateurs** selon les besoins réels (Individual, Company, Public Administration, International Organization)
2. **Les catégories d'exonération** selon la loi malgache (PLF 2026)
3. **La refactorisation du code** pour aligner l'implémentation avec les exigences légales

---

## Types d'Utilisateurs Réorganisés

### Structure Cible

#### 1. **Individual** (`individual`)
- **Nom d'affichage:** "Particulier (Citoyen)"
- **Description:** Citoyens individuels enregistrant des véhicules personnels
- **Catégories de véhicules autorisées:** Personnel uniquement
- **Types de véhicules:** Moto, Scooter, Voiture

#### 2. **Company** (`company`)
- **Nom d'affichage:** "Entreprise/Société"
- **Description:** Entreprises privées gérant des flottes de véhicules
- **Catégories de véhicules autorisées:** Commercial, Transport
- **Types de véhicules:** Tous types terrestres (moto, scooter, voiture, camion, bus, camionnette, remorque)

#### 3. **Public Administration and Institution** (`public_institution`)
- **Nom d'affichage:** "Administration Publique et Institution"
- **Description:** Toutes les institutions publiques et administrations malgaches
- **Inclusions:**
  - Ministères
  - Primature (Bureau du Premier Ministre)
  - Assemblée Nationale
  - Communes (Municipalités)
  - Services d'urgence (Ambulance, Sapeurs-pompiers)
  - Forces de l'ordre (Police, Gendarmerie)
  - Autres institutions publiques malgaches
- **Catégories de véhicules autorisées:** 
  - Administratif
  - Ambulance
  - Sapeurs-pompiers
  - Police
  - Gendarmerie
  - Personnel (pour les fonctionnaires)
- **Types de véhicules:** Tous types selon le besoin

#### 4. **International Organization** (`international_organization`)
- **Nom d'affichage:** "Organisation Internationale"
- **Description:** Organisations internationales et missions diplomatiques
- **Inclusions:**
  - Ambassades et consulats
  - Organisations internationales (ONU, Banque Mondiale, FMI, etc.)
  - Missions diplomatiques
  - Organisations non-gouvernementales internationales
  - Autres entités sous conventions internationales
- **Catégories de véhicules autorisées:**
  - Convention_internationale (exonéré)
- **Types de véhicules:** Tous types selon le besoin
- **Note:** Les véhicules de ces organisations sont automatiquement exonérés de taxe selon les conventions internationales

#### 5. **Agent Partenaire** (séparé, créé par admin)
- **Model:** `AgentPartenaireProfile`
- **Description:** Agents autorisés à collecter les paiements en espèces
- **Pas de changement nécessaire**

#### 6. **Agent Gouvernement** (séparé, créé par admin)
- **Model:** `AgentVerification`
- **Description:** Agents gouvernementaux pour la vérification des QR codes
- **Pas de changement nécessaire**

---

## Catégories d'Exonération selon la Loi

### Article 02.09.03 - PLF 2026

Selon le **Projet de Loi de Finances 2026 de Madagascar**, les catégories de véhicules exonérées sont:

#### 1. **Convention Internationale** (`Convention_internationale`)
- **Description:** Véhicules non soumis à taxation en vertu des conventions internationales
- **Exemples:** Véhicules diplomatiques, véhicules d'organisations internationales

#### 2. **Ambulance** (`Ambulance`)
- **Description:** Véhicules de catégorie ambulance
- **Usage:** Services médicaux d'urgence

#### 3. **Sapeurs-pompiers** (`Sapeurs-pompiers`)
- **Description:** Véhicules de catégorie sapeurs-pompiers
- **Usage:** Services de lutte contre l'incendie et de secours

#### 4. **Administratif** (`Administratif`) ⚠️ **MANQUANT ACTUELLEMENT**
- **Description:** Véhicules administratifs
- **Usage:** Véhicules utilisés par les administrations publiques
- **Note:** Cette catégorie est **manquante** dans le code actuel et doit être ajoutée

### Catégories d'Exonération - Résumé

```python
EXEMPT_CATEGORIES = [
    'Convention_internationale',  # ✅ Déjà implémenté
    'Ambulance',                  # ✅ Déjà implémenté
    'Sapeurs-pompiers',           # ✅ Déjà implémenté
    'Administratif',              # ❌ MANQUANT - À AJOUTER
]
```

---

## Plan de Refactorisation

### Phase 1: Correction des Catégories d'Exonération

#### Étape 1.1: Mettre à jour `est_exonere()` dans `vehicles/models.py`

**Fichier:** `vehicles/models.py`

**Code actuel (ligne 239-241):**
```python
def est_exonere(self):
    """Check if vehicle is exempt from tax"""
    return self.categorie_vehicule in ['Ambulance', 'Sapeurs-pompiers', 'Convention_internationale']
```

**Code corrigé:**
```python
def est_exonere(self):
    """
    Vérifie si le véhicule est exonéré de taxe selon l'Article 02.09.03 du PLF 2026.
    
    Catégories exonérées:
    1. Les véhicules non soumis à taxation en vertu des conventions internationales
    2. Les véhicules de catégorie "ambulance" et "sapeurs-pompiers"
    3. Les véhicules administratifs
    """
    EXEMPT_CATEGORIES = [
        'Convention_internationale',
        'Ambulance',
        'Sapeurs-pompiers',
        'Administratif',  # ✅ AJOUTÉ
    ]
    return self.categorie_vehicule in EXEMPT_CATEGORIES
```

#### Étape 1.2: Mettre à jour les vérifications dans `vehicles/views.py`

**Fichier:** `vehicles/views.py` (ligne 616)

**Code actuel:**
```python
if vehicule.categorie_vehicule in ['Ambulance', 'Sapeurs-pompiers', 'Convention_internationale']:
    return 0
```

**Code corrigé:**
```python
if vehicule.est_exonere():  # Utiliser la méthode du modèle
    return 0
```

#### Étape 1.3: Mettre à jour `vehicles/services.py`

**Fichier:** `vehicles/services.py`

Vérifier et mettre à jour toutes les vérifications d'exonération pour utiliser `vehicule.est_exonere()` au lieu de vérifications hardcodées.

#### Étape 1.4: Ajouter constante pour les catégories exonérées

**Fichier:** `vehicles/models.py`

```python
# Constantes pour les catégories exonérées (selon PLF 2026, Article 02.09.03)
EXEMPT_VEHICLE_CATEGORIES = [
    'Convention_internationale',
    'Ambulance',
    'Sapeurs-pompiers',
    'Administratif',
]
```

### Phase 2: Refactorisation des Types d'Utilisateurs

#### Étape 2.1: Mettre à jour `USER_TYPE_CHOICES` dans `core/models.py`

**Fichier:** `core/models.py`

**Code actuel:**
```python
USER_TYPE_CHOICES = [
    ('individual', 'Individual Citizen'),
    ('company', 'Company/Business'),
    ('emergency', 'Emergency Service Provider'),
    ('government', 'Government Administrator'),
    ('law_enforcement', 'Law Enforcement Officer'),
]
```

**Code refactorisé:**
```python
USER_TYPE_CHOICES = [
    ('individual', 'Particulier (Citoyen)'),
    ('company', 'Entreprise/Société'),
    ('public_institution', 'Administration Publique et Institution'),
    ('international_organization', 'Organisation Internationale'),
]
```

**Note:** 
- Les types `emergency`, `government`, et `law_enforcement` sont consolidés en `public_institution`.
- Le type `international_organization` est ajouté pour les organisations internationales et missions diplomatiques.

#### Étape 2.2: Mettre à jour `CustomUserCreationForm` dans `core/forms.py`

**Fichier:** `core/forms.py`

**Code actuel:**
```python
USER_TYPE_CHOICES = [
    ('individual', 'Particulier (Citoyen)'),
    ('company', 'Entreprise/Société'),
    ('emergency', 'Service d\'urgence'),
    ('government', 'Administration publique'),
    ('law_enforcement', 'Forces de l\'ordre'),
]
```

**Code refactorisé:**
```python
USER_TYPE_CHOICES = [
    ('individual', 'Particulier (Citoyen)'),
    ('company', 'Entreprise/Société'),
    ('public_institution', 'Administration Publique et Institution'),
    ('international_organization', 'Organisation Internationale'),
]
```

#### Étape 2.3: Mettre à jour `get_allowed_vehicle_categories()` dans `core/models.py`

**Fichier:** `core/models.py`

**Code actuel:**
```python
def get_allowed_vehicle_categories(self):
    if self.user_type == 'individual':
        return ['Personnel']
    elif self.user_type == 'company':
        return ['Commercial', 'Transport']
    elif self.user_type == 'emergency':
        return ['Ambulance', 'Sapeurs-pompiers', 'Secours']
    elif self.user_type == 'government':
        return ['Administratif', 'Personnel', 'Commercial', 'Transport', 'Ambulance', 'Sapeurs-pompiers']
    elif self.user_type == 'law_enforcement':
        return ['Police', 'Gendarmerie', 'Personnel']
    return []
```

**Code refactorisé:**
```python
def get_allowed_vehicle_categories(self):
    """Retourne les catégories de véhicules autorisées pour ce type d'utilisateur"""
    if self.user_type == 'individual':
        return ['Personnel']
    elif self.user_type == 'company':
        return ['Commercial', 'Transport']
    elif self.user_type == 'public_institution':
        # Administration publique peut enregistrer tous types de véhicules administratifs
        return [
            'Administratif',
            'Ambulance',
            'Sapeurs-pompiers',
            'Police',
            'Gendarmerie',
            'Personnel',  # Pour les fonctionnaires
        ]
    elif self.user_type == 'international_organization':
        # Organisations internationales peuvent enregistrer des véhicules sous convention internationale
        return [
            'Convention_internationale',
        ]
    return []
```

#### Étape 2.4: Mettre à jour `get_allowed_terrestrial_subtypes()` dans `core/models.py`

**Fichier:** `core/models.py`

**Code actuel:**
```python
def get_allowed_terrestrial_subtypes(self):
    if self.user_type == 'individual':
        return ['moto', 'scooter', 'voiture']
    elif self.user_type == 'company':
        return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']
    elif self.user_type == 'emergency':
        return ['voiture', 'camion', 'bus', 'camionnette']
    elif self.user_type == 'government':
        return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']
    elif self.user_type == 'law_enforcement':
        return ['moto', 'scooter', 'voiture', 'camion']
    return []
```

**Code refactorisé:**
```python
def get_allowed_terrestrial_subtypes(self):
    """Retourne les sous-types de véhicules terrestres autorisés pour ce type d'utilisateur"""
    if self.user_type == 'individual':
        return ['moto', 'scooter', 'voiture']
    elif self.user_type == 'company':
        return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']
    elif self.user_type == 'public_institution':
        # Administration publique peut enregistrer tous types de véhicules
        return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']
    elif self.user_type == 'international_organization':
        # Organisations internationales peuvent enregistrer tous types de véhicules
        return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']
    return []
```

#### Étape 2.5: Créer un nouveau modèle de profil pour Public Institution

**Fichier:** `core/models.py`

```python
class PublicInstitutionProfile(models.Model):
    """Profil pour les administrations publiques et institutions"""
    
    INSTITUTION_TYPE_CHOICES = [
        ('ministere', 'Ministère'),
        ('primature', 'Primature'),
        ('assemblee_nationale', 'Assemblée Nationale'),
        ('commune', 'Commune'),
        ('service_urgence', 'Service d\'urgence'),
        ('forces_ordre', 'Forces de l\'ordre'),
        ('autre', 'Autre institution publique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='public_institution_profile'
    )
    institution_name = models.CharField(
        max_length=200, 
        verbose_name="Nom de l'institution"
    )
    institution_type = models.CharField(
        max_length=50, 
        choices=INSTITUTION_TYPE_CHOICES,
        verbose_name="Type d'institution"
    )
    department = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Département/Service"
    )
    official_registration_number = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name="Numéro d'enregistrement officiel"
    )
    address = models.TextField(blank=True, verbose_name="Adresse")
    contact_person = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Personne de contact"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil Administration Publique"
        verbose_name_plural = "Profils Administrations Publiques"
        indexes = [
            models.Index(fields=['institution_type']),
            models.Index(fields=['institution_name']),
        ]
    
    def __str__(self):
        return f"{self.institution_name} ({self.get_institution_type_display()})"
```

#### Étape 2.6: Créer un nouveau modèle de profil pour International Organization

**Fichier:** `core/models.py`

```python
class InternationalOrganizationProfile(models.Model):
    """Profil pour les organisations internationales et missions diplomatiques"""
    
    ORGANIZATION_TYPE_CHOICES = [
        ('ambassade', 'Ambassade'),
        ('consulat', 'Consulat'),
        ('mission_diplomatique', 'Mission diplomatique'),
        ('organisation_internationale', 'Organisation internationale (ONU, etc.)'),
        ('ong_internationale', 'ONG internationale'),
        ('autre', 'Autre organisation sous convention internationale'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='international_organization_profile'
    )
    organization_name = models.CharField(
        max_length=200, 
        verbose_name="Nom de l'organisation"
    )
    organization_type = models.CharField(
        max_length=50, 
        choices=ORGANIZATION_TYPE_CHOICES,
        verbose_name="Type d'organisation"
    )
    country_of_origin = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Pays d'origine"
    )
    convention_number = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Numéro de convention"
    )
    diplomatic_immunity = models.BooleanField(
        default=False,
        verbose_name="Immunité diplomatique"
    )
    address = models.TextField(blank=True, verbose_name="Adresse")
    contact_person = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Personne de contact"
    )
    official_document_url = models.URLField(
        max_length=500, 
        blank=True,
        verbose_name="Document officiel (convention, accord)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil Organisation Internationale"
        verbose_name_plural = "Profils Organisations Internationales"
        indexes = [
            models.Index(fields=['organization_type']),
            models.Index(fields=['organization_name']),
            models.Index(fields=['country_of_origin']),
        ]
    
    def __str__(self):
        return f"{self.organization_name} ({self.get_organization_type_display()})"
```

### Phase 3: Migration des Données Existantes

#### Étape 3.1: Créer une migration pour mettre à jour les user types

**Fichier:** `core/migrations/XXXX_refactor_user_types.py`

```python
from django.db import migrations

def migrate_user_types(apps, schema_editor):
    """Migre les anciens types d'utilisateurs vers les nouveaux"""
    UserProfile = apps.get_model('core', 'UserProfile')
    
    # Migrer emergency -> public_institution
    UserProfile.objects.filter(user_type='emergency').update(user_type='public_institution')
    
    # Migrer government -> public_institution
    UserProfile.objects.filter(user_type='government').update(user_type='public_institution')
    
    # Migrer law_enforcement -> public_institution
    UserProfile.objects.filter(user_type='law_enforcement').update(user_type='public_institution')

def reverse_migration(apps, schema_editor):
    """Migration inverse (si nécessaire)"""
    UserProfile = apps.get_model('core', 'UserProfile')
    
    # Note: On ne peut pas distinguer les sous-types après migration
    # Cette fonction est à utiliser avec précaution
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', 'XXXX_previous_migration'),
    ]

    operations = [
        migrations.RunPython(migrate_user_types, reverse_migration),
    ]
```

#### Étape 3.2: Vérifier les véhicules avec catégorie 'Administratif'

Vérifier que tous les véhicules avec `categorie_vehicule='Administratif'` sont correctement identifiés comme exonérés après la correction.

### Phase 4: Mise à jour des Templates et Formulaires

#### Étape 4.1: Mettre à jour les templates de registration

**Fichier:** `templates/registration/register.html`

Mettre à jour les options du formulaire pour refléter les nouveaux types d'utilisateurs.

#### Étape 4.2: Mettre à jour les formulaires de véhicule

S'assurer que les catégories de véhicules incluent 'Administratif' et que les utilisateurs de type `public_institution` peuvent la sélectionner.

---

## Corrections Nécessaires

### 1. Correction de la Méthode `est_exonere()`

**Fichier:** `vehicles/models.py`
- ✅ Ajouter 'Administratif' à la liste des catégories exonérées
- ✅ Ajouter documentation selon la loi

### 2. Correction des Vérifications Hardcodées

**Fichiers à vérifier:**
- `vehicles/views.py` (ligne 616)
- `vehicles/services.py`
- `payments/views.py`
- `api/v1/views.py`
- Tous les autres endroits où l'exonération est vérifiée

**Action:** Remplacer toutes les vérifications hardcodées par l'utilisation de `vehicule.est_exonere()`.

### 3. Mise à jour des Constantes

**Fichier:** `vehicles/models.py`

Ajouter une constante `EXEMPT_VEHICLE_CATEGORIES` pour centraliser la liste des catégories exonérées.

### 4. Documentation

Mettre à jour la documentation pour refléter:
- Les types d'utilisateurs refactorisés
- Les catégories d'exonération selon la loi
- Les changements apportés au code

---

## Migration des Données

### Données Existantes à Migrer

1. **UserProfile avec user_type:**
   - `emergency` → `public_institution`
   - `government` → `public_institution`
   - `law_enforcement` → `public_institution`

2. **Profils étendus:**
   - `EmergencyServiceProfile` → `PublicInstitutionProfile` (avec `institution_type='service_urgence'`)
   - `GovernmentAdminProfile` → `PublicInstitutionProfile` (avec `institution_type` approprié)
   - `LawEnforcementProfile` → `PublicInstitutionProfile` (avec `institution_type='forces_ordre'`)

### Script de Migration

```python
# core/management/commands/migrate_user_types.py
from django.core.management.base import BaseCommand
from core.models import UserProfile, EmergencyServiceProfile, GovernmentAdminProfile, LawEnforcementProfile
from core.models import PublicInstitutionProfile

class Command(BaseCommand):
    help = 'Migre les anciens types d\'utilisateurs vers public_institution'

    def handle(self, *args, **options):
        # Migrer les user types
        UserProfile.objects.filter(user_type='emergency').update(user_type='public_institution')
        UserProfile.objects.filter(user_type='government').update(user_type='public_institution')
        UserProfile.objects.filter(user_type='law_enforcement').update(user_type='public_institution')
        
        # Migrer les profils étendus
        # EmergencyServiceProfile -> PublicInstitutionProfile
        for profile in EmergencyServiceProfile.objects.all():
            PublicInstitutionProfile.objects.create(
                user_profile=profile.user_profile,
                institution_name=profile.organization_name,
                institution_type='service_urgence',
                department=profile.department_contact,
                official_registration_number=profile.official_license,
            )
        
        # GovernmentAdminProfile -> PublicInstitutionProfile
        for profile in GovernmentAdminProfile.objects.all():
            PublicInstitutionProfile.objects.create(
                user_profile=profile.user_profile,
                institution_name=profile.department,
                institution_type='ministere',  # ou autre selon le cas
                department=profile.department,
                official_registration_number=profile.employee_id,
            )
        
        # LawEnforcementProfile -> PublicInstitutionProfile
        for profile in LawEnforcementProfile.objects.all():
            PublicInstitutionProfile.objects.create(
                user_profile=profile.user_profile,
                institution_name=profile.department,
                institution_type='forces_ordre',
                department=profile.department,
                official_registration_number=profile.badge_number,
            )
        
        self.stdout.write(self.style.SUCCESS('Migration terminée avec succès'))
```

---

## Tests et Validation

### Tests Unitaires à Créer

1. **Test de la méthode `est_exonere()`:**
   ```python
   def test_est_exonere_includes_administratif(self):
       vehicule = Vehicule.objects.create(
           categorie_vehicule='Administratif',
           # ... autres champs
       )
       self.assertTrue(vehicule.est_exonere())
   ```

2. **Test des catégories exonérées:**
   ```python
   def test_all_exempt_categories(self):
       exempt_categories = ['Convention_internationale', 'Ambulance', 'Sapeurs-pompiers', 'Administratif']
       for category in exempt_categories:
           vehicule = Vehicule.objects.create(categorie_vehicule=category, ...)
           self.assertTrue(vehicule.est_exonere(), f"{category} should be exempt")
   ```

3. **Test des types d'utilisateurs:**
   ```python
   def test_public_institution_categories(self):
       profile = UserProfile.objects.create(user_type='public_institution', ...)
       categories = profile.get_allowed_vehicle_categories()
       self.assertIn('Administratif', categories)
       self.assertIn('Ambulance', categories)
       self.assertIn('Sapeurs-pompiers', categories)
   ```

### Tests d'Intégration

1. **Test du calcul de taxe pour véhicules exonérés:**
   - Vérifier que les véhicules administratifs retournent un montant de 0
   - Vérifier que les autres catégories exonérées fonctionnent correctement

2. **Test de l'enregistrement de véhicules:**
   - Vérifier que les utilisateurs `public_institution` peuvent enregistrer des véhicules administratifs
   - Vérifier que les véhicules administratifs sont automatiquement marqués comme exonérés

---

## Checklist d'Implémentation

### Phase 1: Corrections d'Exonération
- [ ] Mettre à jour `est_exonere()` dans `vehicles/models.py`
- [ ] Ajouter constante `EXEMPT_VEHICLE_CATEGORIES`
- [ ] Mettre à jour toutes les vérifications hardcodées dans `vehicles/views.py`
- [ ] Mettre à jour `vehicles/services.py`
- [ ] Mettre à jour `payments/views.py`
- [ ] Mettre à jour `api/v1/views.py`
- [ ] Vérifier tous les autres fichiers

### Phase 2: Refactorisation des Types d'Utilisateurs
- [ ] Mettre à jour `USER_TYPE_CHOICES` dans `core/models.py`
- [ ] Mettre à jour `CustomUserCreationForm` dans `core/forms.py`
- [ ] Mettre à jour `get_allowed_vehicle_categories()` dans `core/models.py`
- [ ] Mettre à jour `get_allowed_terrestrial_subtypes()` dans `core/models.py`
- [ ] Créer `PublicInstitutionProfile` model
- [ ] Créer migration pour le nouveau modèle

### Phase 3: Migration des Données
- [ ] Créer migration pour mettre à jour les user types
- [ ] Créer script de migration pour les profils étendus
- [ ] Tester la migration sur un environnement de développement
- [ ] Exécuter la migration en production

### Phase 4: Templates et Formulaires
- [ ] Mettre à jour `templates/registration/register.html`
- [ ] Mettre à jour les formulaires de véhicule
- [ ] Mettre à jour les templates d'administration

### Phase 5: Tests
- [ ] Créer tests unitaires pour `est_exonere()`
- [ ] Créer tests pour les nouveaux types d'utilisateurs
- [ ] Créer tests d'intégration
- [ ] Exécuter tous les tests

### Phase 6: Documentation
- [ ] Mettre à jour la documentation technique
- [ ] Mettre à jour la documentation utilisateur
- [ ] Créer guide de migration

---

## Notes Importantes

1. **Rétrocompatibilité:** Les anciens profils (`EmergencyServiceProfile`, `GovernmentAdminProfile`, `LawEnforcementProfile`) peuvent être conservés temporairement pour la migration, puis supprimés après migration complète.

2. **Agents:** Les agents (Agent Partenaire et Agent Gouvernement) restent séparés et ne sont pas affectés par cette refactorisation.

3. **Validation:** Tous les changements doivent être testés avant déploiement en production.

4. **Loi:** Les catégories d'exonération doivent strictement respecter l'Article 02.09.03 du PLF 2026.

---

## Conclusion

Ce plan organise:
- ✅ Les types d'utilisateurs en 3 catégories principales (Individual, Company, Public Institution)
- ✅ Les catégories d'exonération selon la loi malgache (incluant 'Administratif' manquant)
- ✅ La refactorisation du code pour aligner avec les exigences
- ✅ La migration des données existantes
- ✅ Les tests et la validation

**Prochaine étape:** Commencer par la Phase 1 (Corrections d'Exonération) car c'est la plus critique et la plus simple à implémenter.

