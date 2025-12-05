# OCR Testing Guide - Carte Grise Biométrique

## Quick Test Steps

### 1. Access the Form
Navigate to: **http://127.0.0.1:8000/vehicles/add/**

### 2. Test Drag and Drop

**Method 1: Drag and Drop**
1. Open your file explorer
2. Find a carte grise biométrique image (JPG/PNG)
3. Drag the image file
4. Drop it onto the blue dashed box
5. Watch the box highlight when you hover over it
6. See the file info appear with preview
7. Click "Extraire" button

**Method 2: Click to Browse**
1. Click anywhere on the blue dashed box
2. OR click the "Parcourir les fichiers" button
3. Select your carte grise image
4. See the file info appear with preview
5. Click "Extraire" button

**Method 3: Traditional Upload**
1. Click "Parcourir les fichiers" button
2. Select file from dialog
3. Click "Extraire"

### 3. Watch the Magic

**During Processing:**
- Progress spinner appears
- "Extraction des informations en cours..." message shows

**After Success:**
- Success message with confidence score
- Form fields auto-fill with green highlight
- Fields extracted are listed
- Preview image shows

**If Error:**
- Error message in red
- Helpful tips displayed

### 4. Review and Submit

1. Check all filled fields
2. Correct any errors
3. Fill missing fields manually
4. Submit the form

## Visual Features to Test

### ✅ Drag