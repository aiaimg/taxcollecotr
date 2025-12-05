# OCR Recto/Verso Update - Carte Grise Biométrique

## Changements Effectués

### 1. Interface Utilisateur Améliorée

**Emplacement:** Déplacé dans la colonne de droite, au-dessus de l'aperçu de la taxe

**Nouvelles Fonctionnalités:**
- ✅ Upload séparé pour **recto** et **verso**
- ✅ Drag & drop pour chaque face
- ✅ Prévisualisation des images uploadées
- ✅ Tooltip informatif au survol (hover)
- ✅ Design compact et élégant
- ✅ Boutons de suppression individuels

### 2. Structure de l'Interface

```
┌─────────────────────────────────────┐
│  Remplissage automatique       ℹ️   │  ← Tooltip au survol
├─────────────────────────────────────┤
│  Recto (Face avant)                 │
│  ┌───────────────────────────────┐  │
│  │  📤 Glissez ou cliquez        │  │  ← Zone drag & drop
│  └───────────────────────────────┘  │
│                                     │
│  Verso (Face arrière)               │
│  ┌───────────────────────────────┐  │
│  │  📤 Glissez ou cliquez        │  │  ← Zone drag & drop
│  └───────────────────────────────┘  │
│                                     │
│  [Extraire les informations]        │  ← Bouton (visible si recto uploadé)
└─────────────────────────────────────┘
```

### 3. Tooltip Informatif

Au survol de l'icône ℹ️, affiche:
```
Carte grise biométrique uniquement
❌ Carte rose (temporaire)
❌ Facture de moto
❌ Autres documents
```

### 4. Backend Mis à Jour

**Endpoint:** `POST /vehicles/ajax/ocr/carte-grise/`

**Paramètres:**
- `carte_grise_recto` (requis) - Image du recto
- `carte_grise_verso` (optionnel) - Image du verso
- `csrfmiddlewaretoken` - Token CSRF

**Logique:**
1. Traite le recto en premier
2. Si verso fourni, le traite également
3. Fusionne les résultats (verso complète les données manquantes du recto)
4. Calcule la confiance moyenne

### 5. Fichiers Modifiés

#### Frontend
- `templates/vehicles/vehicule_form.html`
  - Section OCR déplacée dans la colonne de droite
  - Deux zones de drop séparées (recto/verso)
  - Tooltip Bootstrap ajouté
  - CSS amélioré

- `static/js/carte-grise-ocr.js`
  - Gestion de deux fichiers séparés
  - Prévisualisation pour chaque face
  - Validation indépendante
  - Boutons de suppression individuels

#### Backend
- `vehicles/views.py`
  - `process_carte_grise_ocr()` mis à jour
  - Accepte recto + verso
  - Fusion intelligente des résultats
  - Gestion des fichiers temporaires améliorée

## Utilisation

### Pour l'Utilisateur

1. **Aller sur la page d'ajout de véhicule**
   - `/vehicles/add/`

2. **Voir la section OCR à droite**
   - Au-dessus de "Aperçu de la taxe"
   - Icône ℹ️ pour plus d'infos (hover)

3. **Uploader le recto (obligatoire)**
   - Glisser-déposer l'image
   - OU cliquer pour parcourir
   - Prévisualisation s'affiche

4. **Uploader le verso (optionnel)**
   - Même processus que le recto
   - Améliore la précision

5. **Cliquer sur "Extraire les informations"**
   - Bouton apparaît quand recto est uploadé
   - Traitement 2-5 secondes
   - Formulaire se remplit automatiquement

6. **Vérifier et corriger**
   - Champs extraits sont mis en évidence
   - Message de succès avec nombre de champs
   - Corriger si nécessaire

7. **Soumettre le formulaire**

### Avantages du Recto/Verso

**Recto contient généralement:**
- Plaque d'immatriculation
- Nom du propriétaire
- Marque et modèle
- Date de première circulation

**Verso contient généralement:**
- VIN/Numéro de châssis
- Puissance fiscale (CV)
- Cylindrée
- Source d'énergie
- Couleur

**En combinant les deux:**
- ✅ Meilleure précision globale
- ✅ Plus de champs extraits
- ✅ Données redondantes pour validation
- ✅ Confiance accrue

## Styles CSS

### Classes Principales

```css
.ocr-drop-zone {
    /* Zone de drop normale */
    background-color: #f8f9fa;
    border: 2px dashed #dee2e6;
}

.ocr-drop-zone:hover {
    /* Au survol */
    background-color: #e9ecef;
    border-color: #0d6efd;
}

.ocr-drop-zone.drag-over {
    /* Pendant le drag */
    background-color: #cfe2ff;
    border-color: #0d6efd;
    transform: scale(1.02);
}

.ocr-drop-zone.has-file {
    /* Fichier uploadé */
    background-color: #d1e7dd;
    border-color: #198754;
}
```

## Tests

### Scénarios à Tester

1. **Upload recto seul**
   - ✅ Bouton "Extraire" apparaît
   - ✅ Traitement réussi
   - ✅ Données extraites

2. **Upload recto + verso**
   - ✅ Les deux prévisualisations s'affichent
   - ✅ Traitement des deux images
   - ✅ Fusion des résultats
   - ✅ Meilleure précision

3. **Suppression individuelle**
   - ✅ Bouton X sur chaque prévisualisation
   - ✅ Supprime uniquement l'image concernée
   - ✅ Peut re-uploader

4. **Drag & drop**
   - ✅ Glisser image sur zone recto
   - ✅ Glisser image sur zone verso
   - ✅ Animation de survol
   - ✅ Prévisualisation immédiate

5. **Tooltip**
   - ✅ Survol de l'icône ℹ️
   - ✅ Affiche les informations
   - ✅ Disparaît au départ

6. **Validation**
   - ✅ Format incorrect rejeté
   - ✅ Fichier trop gros rejeté
   - ✅ Messages d'erreur clairs

## Améliorations Futures

1. **Détection automatique recto/verso**
   - Analyser l'image pour déterminer la face
   - Placer automatiquement dans la bonne zone

2. **Rotation automatique**
   - Détecter l'orientation
   - Corriger automatiquement

3. **Qualité d'image**
   - Vérifier la netteté
   - Avertir si image floue

4. **Comparaison recto/verso**
   - Valider la cohérence des données
   - Alerter si incohérences

5. **Historique OCR**
   - Sauvegarder les extractions
   - Apprendre des corrections utilisateur

## Dépannage

### Le bouton "Extraire" n'apparaît pas
- Vérifier que le recto est uploadé
- Vérifier la console JavaScript

### Erreur "Format non supporté"
- Utiliser JPG ou PNG uniquement
- Pas de PDF, GIF, etc.

### Erreur "Fichier trop volumineux"
- Réduire la taille de l'image
- Maximum 10MB par fichier

### Tooltip ne s'affiche pas
- Vérifier que Bootstrap est chargé
- Vérifier la console pour erreurs JS

### Prévisualisation ne s'affiche pas
- Vérifier le format de l'image
- Vérifier les permissions de fichier

---

**Date:** 7 novembre 2025  
**Version:** 2.0.0  
**Status:** ✅ Implémenté et testé
