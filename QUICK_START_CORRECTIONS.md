# Corrections Rapides - Catégories d'Exonération

## Problème Identifié

La catégorie **'Administratif'** est **manquante** dans la liste des catégories exonérées, alors qu'elle est requise par la loi malgache (PLF 2026, Article 02.09.03).

## Corrections Immédiates Nécessaires

### 1. Correction de `vehicles/models.py` (LIGNE 239-241)

**AVANT:**
```python
def est_exonere(self):
    """Check if vehicle is exempt from tax"""
    return self.categorie_vehicule in ['Ambulance', 'Sapeurs-pompiers', 'Convention_internationale']
```

**APRÈS:**
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

### 2. Correction de `vehicles/views.py` (LIGNE 616)

**AVANT:**
```python
if vehicule.categorie_vehicule in ['Ambulance', 'Sapeurs-pompiers', 'Convention_internationale']:
    return 0
```

**APRÈS:**
```python
if vehicule.est_exonere():  # Utiliser la méthode du modèle
    return 0
```

## Catégories d'Exonération selon la Loi

Selon l'**Article 02.09.03 du PLF 2026**, les catégories exonérées sont:

1. ✅ **Convention_internationale** - Déjà implémenté
2. ✅ **Ambulance** - Déjà implémenté
3. ✅ **Sapeurs-pompiers** - Déjà implémenté
4. ❌ **Administratif** - **MANQUANT - À AJOUTER**

## Fichiers à Vérifier

- [x] `vehicles/models.py` - Méthode `est_exonere()`
- [ ] `vehicles/views.py` - Vérification hardcodée (ligne 616)
- [ ] `vehicles/services.py` - Vérifications d'exonération
- [ ] `payments/views.py` - Vérifications d'exonération
- [ ] `api/v1/views.py` - Vérifications d'exonération
- [ ] Autres fichiers avec vérifications hardcodées

## Action Immédiate

**Corriger immédiatement** la méthode `est_exonere()` pour inclure 'Administratif', car actuellement les véhicules administratifs ne sont **pas reconnus comme exonérés**.

