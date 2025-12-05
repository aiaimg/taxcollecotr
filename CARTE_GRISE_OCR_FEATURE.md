# Carte Grise Biométrique OCR Feature

## Overview

This feature allows users to automatically fill vehicle registration forms by uploading a photo of their **carte grise biométrique** (biometric vehicle registration card). The system uses OCR (Optical Character Recognition) to extract information from the document.

## Important Limitations

⚠️ **This feature ONLY works with:**
- **Carte grise biométrique** (modern biometric registration cards from Madagascar)

❌ **Does NOT work with:**
- **Carte rose** (temporary registration - pink card)
- **Facture de moto** (motorcycle invoices)
- Other vehicle documents

## How It Works

### User Flow

1. User navigates to "Add Vehicle" form
2. User sees OCR upload section at the top with clear instructions
3. User clicks "Télécharger carte grise biométrique" button
4. User selects a photo of their carte grise biométrique (JPG/PNG, max 10MB)
5. User clicks "Extraire les informations" button
6. System processes the image and extracts:
   - Plate number (Plaque d'immatriculation)
   - VIN/Chassis number
   - Owner name (Nom du propriétaire)
   - Vehicle brand (Marque)
   - Vehicle model (Modèle)
   - Color (Couleur)
   - First registration date (Date de première circulation)
   - Power in CV (Puissance fiscale)
   - Engine displacement (Cylindrée)
   - Energy source (Source d'énergie)
7. Form fields are automatically filled with extracted data
8. User reviews and corrects any errors
9. User submits the form

### Technical Implementation

#### Backend (Python/Django)

**OCR Processing:**
- `vehicles/ocr_utils.py` - Core OCR logic using tesserocr
- `vehicles/views.py` - `process_carte_grise_ocr()` endpoint

**Key Features:**
- Image preprocessing (grayscale, contrast enhancement, resizing)
- Pattern matching for specific fields (regex)
- French language OCR support
- Confidence scoring
- Error handling

#### Frontend (JavaScript)

**OCR Handler:**
- `static/js/carte-grise-ocr.js` - Handles upload, processing, and form filling
- Clean separation of concerns
- Progress indicators
- Success/error feedback
- Automatic form field population

#### Template

**Form Integration:**
- `templates/vehicles/vehicule_form.html` - Upload UI with clear warnings
- Bootstrap 5 styling
- Responsive design
- Clear visual feedback

## Installation

### Requirements

```bash
# Already added to requirements.txt
tesserocr==2.7.1
```

### System Dependencies

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # For French language support
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-fra
```

### Install Python Package

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## API Endpoint

### POST `/vehicles/ajax/ocr/carte-grise/`

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: 
  - `carte_grise_image`: Image file (JPG/PNG)
  - `csrfmiddlewaretoken`: CSRF token

**Response (Success):**
```json
{
  "success": true,
  "confidence": 85.5,
  "data": {
    "plaque_immatriculation": "6046015",
    "vin": "CT010014065",
    "nom_proprietaire": "RAZAFIARISON",
    "marque": "TOYOTA",
    "modele": "COROLLA",
    "couleur": "BLANC",
    "date_premiere_circulation": "2006-01-30",
    "puissance_fiscale_cv": 8,
    "cylindree_cm3": 1600,
    "source_energie": "Essence"
  },
  "message": "Informations extraites avec succès..."
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Accuracy Expectations

Based on carte grise biométrique documents:

| Field | Expected Accuracy |
|-------|------------------|
| Plate Number | 85-90% |
| VIN/Chassis | 75-85% |
| Owner Name | 70-80% |
| Brand | 75-85% |
| Model | 70-80% |
| Date | 80-90% |
| Power (CV) | 75-85% |
| Cylindrée | 75-85% |
| Energy Source | 70-80% |

**Overall:** 70-85% of fields extracted correctly

## User Experience

### Success Message
```
✓ 8/10 champs extraits (82% de confiance)
Champs extraits: Plaque, Propriétaire, Marque, Modèle, Date, Puissance (CV), Cylindrée, Énergie
ℹ️ Veuillez vérifier et corriger les informations si nécessaire.
```

### Visual Feedback
- Extracted fields are highlighted in green for 2 seconds
- Form automatically scrolls to show filled fields
- Clear error messages if OCR fails
- Progress indicator during processing

## Testing

### Manual Testing

1. Navigate to `/vehicles/add/`
2. Upload a carte grise biométrique image
3. Click "Extraire les informations"
4. Verify extracted data
5. Correct any errors
6. Submit form

### Test Images

Use the example carte grise images provided by the user for testing.

## Future Improvements

1. **Cloud OCR Fallback**: Use Google Cloud Vision API for low-confidence results
2. **Document Type Detection**: Automatically detect if uploaded document is carte grise biométrique
3. **Multi-page Support**: Handle PDF documents with multiple pages
4. **Learning System**: Improve accuracy based on user corrections
5. **Batch Processing**: Allow multiple vehicle registrations at once

## Security Considerations

- File size limit: 10MB
- Allowed formats: JPG, PNG only
- Temporary files are deleted after processing
- User authentication required
- CSRF protection enabled

## Troubleshooting

### OCR Returns Empty Results

**Possible causes:**
- Poor image quality
- Wrong document type (not carte grise biométrique)
- Tesseract not installed
- French language pack not installed

**Solutions:**
- Ask user to take a clearer photo
- Verify document type
- Install system dependencies
- Check tesseract installation: `tesseract --version`

### Low Accuracy

**Possible causes:**
- Glare or shadows on document
- Watermarks interfering with text
- Small font size
- Handwritten sections

**Solutions:**
- Improve image preprocessing
- Adjust OCR parameters
- Consider cloud OCR for difficult cases

## Support

For issues or questions, contact the development team.

---

**Created:** 2025-11-07  
**Last Updated:** 2025-11-07  
**Version:** 1.0.0
