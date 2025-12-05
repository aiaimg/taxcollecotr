# Vehicle Form JavaScript Documentation

## Overview

The vehicle form functionality has been refactored into two separate JavaScript files for better maintainability:

1. **carte-grise-ocr.js** - Handles OCR (Optical Character Recognition) for carte grise biométrique
2. **vehicle-form.js** - Handles all other vehicle form functionality

## Files

### 1. carte-grise-ocr.js

**Purpose**: Automatic form filling from carte grise biométrique images (recto + verso)

**Features**:
- Drag and drop file upload for recto and verso
- Click to upload functionality
- File validation (type and size)
- Image preview
- OCR processing via AJAX
- Automatic form field population
- Visual feedback (success/error messages)

**Supported File Types**: JPG, JPEG, PNG, WEBP (max 10MB)

**Usage**:
```html
<script src="{% static 'js/carte-grise-ocr.js' %}"></script>
```

The script automatically initializes when the DOM is ready and looks for these elements:
- `#carte-grise-recto` - File input for recto
- `#carte-grise-verso` - File input for verso
- `#ocr-drop-zone-recto` - Drop zone for recto
- `#ocr-drop-zone-verso` - Drop zone for verso
- `#process-ocr-btn` - Button to trigger OCR processing
- `#ocr-progress` - Progress indicator
- `#ocr-result` - Result display area

### 2. vehicle-form.js

**Purpose**: Handles tax calculation, cylindree conversion, and document management

**Features**:

#### Tax Calculation
- Real-time tax calculation based on vehicle data
- Debounced AJAX requests (500ms delay)
- Visual loading states
- Exemption handling
- Error handling

#### License Plate Formatting
- Auto-formatting (e.g., "1234AB" → "1234 AB")
- Uppercase conversion
- Character validation

#### Cylindree Conversion
- Automatic conversion from cm³ to CV (fiscal horsepower)
- Debounced conversion (800ms delay)
- CV suggestions
- Example vehicles display
- Manual conversion button

#### Energy Source Handling
- Hides cylindree field for electric vehicles
- Clears cylindree value when electric is selected

#### Document Management (Edit Mode Only)
- Document upload with validation
- Document listing
- Document editing
- Document deletion
- File type and size validation
- Real-time updates via AJAX

**Supported Document Types**: PDF, JPG, JPEG, PNG, WEBP (max 10MB)

**Usage**:
```html
<script src="{% static 'js/vehicle-form.js' %}"></script>
```

The script automatically initializes when the DOM is ready. For edit mode, ensure the form has a `data-vehicle-id` attribute:
```html
<form id="vehicule-form" data-vehicle-id="{{ object.pk }}">
```

## API Endpoints

### Tax Calculation
- **URL**: `/vehicles/ajax/calculate-tax/`
- **Method**: POST
- **Parameters**: 
  - `puissance_fiscale_cv`
  - `source_energie`
  - `date_premiere_circulation`
  - `categorie_vehicule`

### Cylindree Conversion
- **URL**: `/vehicles/api/convert-cylindree/`
- **Method**: GET
- **Parameters**: `cylindree` (query parameter)

### OCR Processing
- **URL**: `/vehicles/ajax/ocr/carte-grise/`
- **Method**: POST
- **Parameters**: 
  - `carte_grise_recto` (file)
  - `carte_grise_verso` (file, optional)

### Document Management
- **List**: `/vehicles/{vehicle_id}/documents/` (GET)
- **Upload**: `/vehicles/{vehicle_id}/documents/upload-ajax/` (POST)
- **Edit**: `/vehicles/{vehicle_id}/documents/{document_id}/` (POST)
- **Delete**: `/vehicles/{vehicle_id}/documents/{document_id}/delete/` (POST)

## Dependencies

- **Bootstrap 5**: For modals, tooltips, and alerts
- **Notifications.js**: For user notifications (optional, falls back to alert())

## Browser Compatibility

- Modern browsers with ES6 support
- FileReader API support
- Fetch API support
- FormData API support

## Debugging

Both scripts include console logging for debugging:
- File validation errors
- AJAX request errors
- OCR processing status
- Document management operations

Enable browser console to see debug messages.

## Maintenance Notes

### Adding New Form Fields

To add a new field that triggers tax calculation:
1. Add the field ID to the `taxFields` array in `vehicle-form.js`
2. The field will automatically trigger debounced tax calculation

### Modifying File Validation

File validation rules are defined in both scripts:
- **carte-grise-ocr.js**: `validTypes` array in `handleDroppedFile()`
- **vehicle-form.js**: `ALLOWED_EXTS` and `ALLOWED_MIMES` sets in `initDocumentManagement()`

### Customizing Debounce Delays

Debounce delays can be adjusted:
- Tax calculation: 500ms (line with `debounce(calculateTax, 500)`)
- Cylindree conversion: 800ms (line with `debounce(convertCylindree, 800)`)

## Testing

### Manual Testing Checklist

#### OCR Functionality
- [ ] Drag and drop recto image
- [ ] Drag and drop verso image
- [ ] Click to upload recto
- [ ] Click to upload verso
- [ ] Clear recto image
- [ ] Clear verso image
- [ ] Process OCR with both images
- [ ] Process OCR with recto only
- [ ] Verify form fields are populated
- [ ] Test with invalid file types
- [ ] Test with oversized files

#### Tax Calculation
- [ ] Enter puissance fiscale
- [ ] Select source energie
- [ ] Enter date premiere circulation
- [ ] Verify tax calculation updates
- [ ] Test with exempt vehicle type
- [ ] Test with missing required fields

#### Cylindree Conversion
- [ ] Enter cylindree value
- [ ] Verify automatic conversion
- [ ] Click manual conversion button
- [ ] Apply CV suggestion
- [ ] Test with electric vehicle (should hide cylindree)

#### Document Management
- [ ] Upload new document
- [ ] View document list
- [ ] Edit document
- [ ] Delete document
- [ ] Test file validation
- [ ] Test with invalid file types

## Troubleshooting

### OCR Not Working
1. Check browser console for errors
2. Verify OCR endpoint is accessible
3. Check file upload limits in Django settings
4. Verify CSRF token is present

### Tax Calculation Not Updating
1. Check if all required fields are filled
2. Verify tax calculation endpoint is accessible
3. Check browser console for AJAX errors
4. Verify CSRF token is present

### Drag and Drop Not Working
1. Check if drop zones have correct IDs
2. Verify file inputs have correct IDs
3. Check browser console for JavaScript errors
4. Test with different file types

### Document Upload Failing
1. Check file size (max 10MB)
2. Verify file type is supported
3. Check Django file upload settings
4. Verify CSRF token is present
5. Check server logs for errors
