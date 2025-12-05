/**
 * Vehicle Form Handler
 * Handles tax calculation, cylindree conversion, and document management
 */

(function() {
    'use strict';

    // Vehicle Form Class
    class VehicleForm {
        constructor() {
            this.form = document.getElementById('vehicule-form');
            this.taxPreview = document.getElementById('tax-preview');
            this.taxResult = document.getElementById('tax-result');
            
            // Tax calculation fields
            this.taxFields = [
                'id_puissance_fiscale_cv',
                'id_source_energie',
                'id_date_premiere_circulation',
                'id_categorie_vehicule'
            ];
            
            // Conversion data
            this.conversionData = null;

            // Define debounced functions (avoid class fields for compatibility)
            this.debouncedCalculateTax = this.debounce(() => this.calculateTax(), 500);
            this.debouncedConvertCylindree = this.debounce(() => this.convertCylindree(), 800);
            
            this.init();
        }

        init() {
            if (!this.form) {
                console.warn('Vehicle form not found on page');
                return;
            }

            // Initialize tax calculation
            this.initTaxCalculation();
            
            // Initialize license plate formatting
            this.initLicensePlateFormatting();
            
            // Initialize cylindree conversion
            this.initCylindreeConversion();
            
            // Initialize energy source handling
            this.initEnergySourceHandling();
            
            // Initialize document management (if editing)
            this.initDocumentManagement();
        }

        // ===== TAX CALCULATION =====
        
        initTaxCalculation() {
            // Bind events to tax calculation fields
            this.taxFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.addEventListener('input', () => this.debouncedCalculateTax());
                    field.addEventListener('change', () => this.debouncedCalculateTax());
                }
            });
            
            // Initial calculation if editing existing vehicle
            const isEditing = this.form.dataset.vehicleId;
            if (isEditing) {
                this.calculateTax();
            }
        }

        // (moved to constructor for compatibility)

        async calculateTax() {
            const formData = {
                puissance_fiscale_cv: document.getElementById('id_puissance_fiscale_cv').value,
                source_energie: document.getElementById('id_source_energie').value,
                date_premiere_circulation: document.getElementById('id_date_premiere_circulation').value,
                categorie_vehicule: document.getElementById('id_categorie_vehicule').value,
                csrfmiddlewaretoken: this.getCSRFToken()
            };
            
            // Check if required fields are filled
            if (!formData.puissance_fiscale_cv || !formData.source_energie || !formData.date_premiere_circulation) {
                this.showTaxPlaceholder();
                return;
            }
            
            // Show loading
            this.taxPreview.classList.add('loading');
            
            try {
                const response = await fetch('/vehicles/ajax/calculate-tax/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': formData.csrfmiddlewaretoken
                    },
                    body: new URLSearchParams(formData)
                });

                const result = await response.json();
                this.taxPreview.classList.remove('loading');
                
                if (result.success) {
                    this.displayTaxResult(result);
                } else {
                    this.showTaxError(result.message);
                }
            } catch (error) {
                console.error('Tax calculation error:', error);
                this.taxPreview.classList.remove('loading');
                this.showTaxError('Erreur lors du calcul de la taxe');
            }
        }

        displayTaxResult(result) {
            if (result.is_exempt) {
                this.taxResult.innerHTML = `
                    <div class="text-center">
                        <i class="ri-shield-line ri-3x mb-3"></i>
                        <h4 class="mb-2">Exonéré</h4>
                        <p class="mb-0 opacity-75">${result.message}</p>
                    </div>
                `;
            } else {
                const amount = parseFloat(result.tax_amount).toLocaleString('fr-FR');
                const currentYear = new Date().getFullYear();
                this.taxResult.innerHTML = `
                    <div class="text-center">
                        <div class="tax-amount mb-2">${amount} Ar</div>
                        <p class="mb-0 opacity-75">Taxe annuelle ${currentYear}</p>
                    </div>
                `;
            }
        }

        showTaxPlaceholder() {
            this.taxResult.innerHTML = `
                <div class="text-center py-4">
                    <i class="ri-information-line ri-2x mb-3 opacity-50"></i>
                    <p class="mb-0 opacity-75">
                        Remplissez les informations du véhicule pour voir le calcul de la taxe
                    </p>
                </div>
            `;
        }

        showTaxError(message) {
            this.taxResult.innerHTML = `
                <div class="text-center py-4">
                    <i class="ri-alert-line ri-2x mb-3 text-warning"></i>
                    <p class="mb-0">${message}</p>
                </div>
            `;
        }

        // ===== LICENSE PLATE FORMATTING =====
        
        initLicensePlateFormatting() {
            const plateField = document.getElementById('id_plaque_immatriculation');
            if (plateField) {
                plateField.addEventListener('input', function() {
                    let value = this.value.toUpperCase().replace(/[^0-9A-Z\s]/g, '');
                    
                    // Auto-format: add space after numbers
                    if (value.match(/^[0-9]{1,4}[A-Z]/)) {
                        value = value.replace(/^([0-9]{1,4})([A-Z])/, '$1 $2');
                    }
                    
                    this.value = value;
                });
            }
        }

        // ===== CYLINDREE CONVERSION =====
        
        initCylindreeConversion() {
            const cylindreeField = document.getElementById('id_cylindree_cm3');
            const convertBtn = document.getElementById('convert-cylindree-btn');
            const applySuggestionBtn = document.getElementById('apply-cv-suggestion');
            const cvField = document.getElementById('id_puissance_fiscale_cv');
            
            if (!cylindreeField) return;
            
            // Auto-conversion with debounce
            cylindreeField.addEventListener('input', () => {
                const cylindree = cylindreeField.value;
                if (cylindree && cylindree > 0) {
                    this.debouncedConvertCylindree();
                } else {
                    this.hideConversionInfo();
                }
            });
            
            // Manual conversion button
            if (convertBtn) {
                convertBtn.addEventListener('click', () => {
                    const cylindree = cylindreeField.value;
                    if (!cylindree || cylindree <= 0) {
                        this.showNotification('warning', 'Veuillez saisir une cylindrée valide');
                        return;
                    }
                    this.convertCylindree();
                });
            }
            
            // Apply CV suggestion
            if (applySuggestionBtn) {
                applySuggestionBtn.addEventListener('click', () => {
                    if (this.conversionData && this.conversionData.cv_suggere) {
                        cvField.value = this.conversionData.cv_suggere;
                        document.getElementById('cv-suggestion').style.display = 'none';
                        this.debouncedCalculateTax();
                    }
                });
            }
            
            // Hide suggestion when user manually enters CV
            if (cvField) {
                cvField.addEventListener('input', function() {
                    if (this.value) {
                        document.getElementById('cv-suggestion').style.display = 'none';
                    }
                });
            }
            
            // Initial conversion if editing
            const isEditing = this.form.dataset.vehicleId;
            if (isEditing && cylindreeField.value) {
                this.convertCylindree();
            }
        }

        // (moved to constructor for compatibility)

        async convertCylindree() {
            const cylindree = document.getElementById('id_cylindree_cm3').value;
            
            if (!cylindree || cylindree <= 0) {
                this.hideConversionInfo();
                return;
            }
            
            try {
                const response = await fetch(`/vehicles/api/convert-cylindree/?cylindree=${cylindree}`);
                const result = await response.json();
                
                if (result.success) {
                    this.showConversionInfo(result.data);
                } else {
                    this.hideConversionInfo();
                    console.error('Conversion error:', result.error);
                }
            } catch (error) {
                this.hideConversionInfo();
                console.error('AJAX error:', error);
            }
        }

        showConversionInfo(data) {
            this.conversionData = data;
            
            // Show conversion info
            document.getElementById('conversion-message').textContent = data.message;
            document.getElementById('conversion-examples').innerHTML =
                `<strong>Exemples:</strong> ${data.exemples_vehicules.join(', ')}`;
            document.getElementById('conversion-info').style.display = 'block';
            
            // Show suggestion if CV field is empty
            const cvField = document.getElementById('id_puissance_fiscale_cv');
            if (!cvField.value) {
                document.getElementById('cv-suggestion-text').textContent = data.conseil;
                document.getElementById('cv-suggestion').style.display = 'block';
            }
        }

        hideConversionInfo() {
            document.getElementById('conversion-info').style.display = 'none';
            document.getElementById('cv-suggestion').style.display = 'none';
            this.conversionData = null;
        }

        // ===== ENERGY SOURCE HANDLING =====
        
        initEnergySourceHandling() {
            const energyField = document.getElementById('id_source_energie');
            const cylindreeField = document.getElementById('id_cylindree_cm3');
            
            if (energyField && cylindreeField) {
                energyField.addEventListener('change', function() {
                    const cylindreeContainer = cylindreeField.closest('.col-lg-6');
                    if (this.value === 'Electrique') {
                        cylindreeContainer.style.display = 'none';
                        cylindreeField.value = '';
                        document.getElementById('conversion-info').style.display = 'none';
                        document.getElementById('cv-suggestion').style.display = 'none';
                    } else {
                        cylindreeContainer.style.display = 'block';
                    }
                });
            }
        }

        // ===== DOCUMENT MANAGEMENT =====
        
        initDocumentManagement() {
            const vehicleId = this.form.dataset.vehicleId;
            if (!vehicleId) return;
            
            this.vehicleId = vehicleId;
            this.csrfToken = this.getCSRFToken();
            
            // File validation constants
            this.MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
            this.ALLOWED_EXTS = new Set(['.pdf', '.jpg', '.jpeg', '.png', '.webp']);
            this.ALLOWED_MIMES = new Set(['application/pdf', 'image/jpeg', 'image/png', 'image/webp']);
            
            // Initialize upload form
            this.initDocumentUpload();
            
            // Initialize edit form
            this.initDocumentEdit();
            
            // Load documents
            this.loadDocuments();
        }

        initDocumentUpload() {
            const uploadForm = document.getElementById('document-upload-form');
            const uploadFileInput = document.getElementById('document-file');
            
            if (!uploadForm) return;
            
            // File validation on change
            if (uploadFileInput) {
                const submitBtn = uploadForm.querySelector('button[type="submit"]');
                uploadFileInput.addEventListener('change', () => {
                    const file = uploadFileInput.files && uploadFileInput.files[0];
                    const { valid, error } = this.validateFile(file);
                    if (!valid) {
                        this.showDocumentNotification('error', error);
                        uploadFileInput.value = '';
                        if (submitBtn) submitBtn.disabled = true;
                    } else if (submitBtn) {
                        submitBtn.disabled = false;
                    }
                });
            }
            
            // Form submission
            uploadForm.addEventListener('submit', (e) => this.handleDocumentUpload(e));
        }

        initDocumentEdit() {
            const editForm = document.getElementById('edit-document-form');
            const editFileInput = document.getElementById('edit-document-file');
            
            if (!editForm) return;
            
            // File validation on change
            if (editFileInput) {
                const submitBtn = editForm.querySelector('button[type="submit"]');
                editFileInput.addEventListener('change', () => {
                    if (!editFileInput.files.length) return;
                    const { valid, error } = this.validateFile(editFileInput.files[0]);
                    if (!valid) {
                        this.showDocumentNotification('error', error);
                        editFileInput.value = '';
                        if (submitBtn) submitBtn.disabled = true;
                    } else if (submitBtn) {
                        submitBtn.disabled = false;
                    }
                });
            }
            
            // Form submission
            editForm.addEventListener('submit', (e) => this.handleDocumentEdit(e));
        }

        validateFile(file) {
            if (!file) {
                return { valid: false, error: 'Veuillez sélectionner un fichier' };
            }
            if (file.size > this.MAX_FILE_SIZE) {
                return { valid: false, error: 'La taille du fichier dépasse 10MB' };
            }
            const name = file.name || '';
            const dotIndex = name.lastIndexOf('.');
            const ext = dotIndex >= 0 ? name.substring(dotIndex).toLowerCase() : '';
            if (!this.ALLOWED_EXTS.has(ext)) {
                return { valid: false, error: 'Formats autorisés: PDF, JPG, JPEG, PNG, WEBP' };
            }
            const ct = file.type || '';
            if (ct && !this.ALLOWED_MIMES.has(ct)) {
                return { valid: false, error: 'Type de fichier non supporté' };
            }
            return { valid: true };
        }

        async handleDocumentUpload(e) {
            e.preventDefault();
            
            const form = e.target;
            const fileInput = document.getElementById('document-file');
            
            if (!fileInput || !fileInput.files.length) {
                this.showDocumentNotification('error', 'Veuillez sélectionner un fichier');
                return;
            }
            
            const { valid, error } = this.validateFile(fileInput.files[0]);
            if (!valid) {
                this.showDocumentNotification('error', error);
                return;
            }

            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Téléchargement...';
            
            try {
                const response = await fetch(`/vehicles/${this.vehicleId}/documents/upload-ajax/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': this.csrfToken
                    },
                    body: formData
                });

                const data = await response.json();
                
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                
                if (data.success) {
                    this.showDocumentNotification('success', data.message);
                    form.reset();
                    const collapse = document.getElementById('upload-document-form');
                    if (collapse) {
                        const collapseInstance = bootstrap.Collapse.getInstance(collapse);
                        if (collapseInstance) {
                            collapseInstance.hide();
                        }
                    }
                    this.loadDocuments();
                } else {
                    this.showDocumentNotification('error', data.error || 'Erreur lors du téléchargement');
                    if (data.errors) {
                        console.error('Validation errors:', data.errors);
                    }
                }
            } catch (error) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                console.error('Error uploading document:', error);
                this.showDocumentNotification('error', 'Erreur lors du téléchargement du document');
            }
        }

        async handleDocumentEdit(e) {
            e.preventDefault();
            
            const form = e.target;
            const documentId = document.getElementById('edit-document-id').value;
            const editFileInput = document.getElementById('edit-document-file');
            
            if (editFileInput && editFileInput.files.length) {
                const { valid, error } = this.validateFile(editFileInput.files[0]);
                if (!valid) {
                    this.showDocumentNotification('error', error);
                    return;
                }
            }
            
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Enregistrement...';
            
            try {
                const response = await fetch(`/vehicles/${this.vehicleId}/documents/${documentId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': this.csrfToken
                    },
                    body: formData
                });

                const data = await response.json();
                
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                
                if (data.success) {
                    this.showDocumentNotification('success', data.message);
                    const modalEl = document.getElementById('editDocumentModal');
                    const modalInstance = modalEl ? bootstrap.Modal.getInstance(modalEl) : null;
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                    form.reset();
                    this.loadDocuments();
                } else {
                    this.showDocumentNotification('error', data.error || 'Erreur lors de la modification');
                }
            } catch (error) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                console.error('Error updating document:', error);
                this.showDocumentNotification('error', 'Erreur lors de la modification du document');
            }
        }

        async loadDocuments() {
            const loadingEl = document.getElementById('documents-loading');
            const listEl = document.getElementById('documents-list');
            
            if (!loadingEl || !listEl) return;
            
            loadingEl.style.display = 'block';
            listEl.style.opacity = '0.5';
            
            try {
                const response = await fetch(`/vehicles/${this.vehicleId}/documents/`, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                const data = await response.json();
                
                loadingEl.style.display = 'none';
                listEl.style.opacity = '1';
                
                if (data.success) {
                    this.renderDocuments(data.documents);
                    this.updateDocumentsCount(data.documents.length);
                } else {
                    this.showDocumentNotification('error', data.error || 'Erreur lors du chargement des documents');
                }
            } catch (error) {
                loadingEl.style.display = 'none';
                listEl.style.opacity = '1';
                console.error('Error loading documents:', error);
                this.showDocumentNotification('error', 'Erreur lors du chargement des documents');
            }
        }

        renderDocuments(documents) {
            const listEl = document.getElementById('documents-list');
            
            if (documents.length === 0) {
                listEl.innerHTML = `
                    <div class="text-center py-4 bg-light rounded">
                        <i class="ri-file-list-3-line fs-3 text-muted d-block mb-2"></i>
                        <p class="text-muted mb-0 small">Aucun document ajouté</p>
                    </div>
                `;
                return;
            }
            
            listEl.innerHTML = documents.map(doc => this.renderDocumentItem(doc)).join('');
            this.attachDocumentEventListeners();
        }

        renderDocumentItem(doc) {
            const statusBadges = {
                'verifie': '<span class="badge bg-success ms-2"><i class="ri-check-line"></i> Vérifié</span>',
                'rejete': '<span class="badge bg-danger ms-2"><i class="ri-close-line"></i> Rejeté</span>',
                'soumis': '<span class="badge bg-warning ms-2"><i class="ri-time-line"></i> Soumis</span>'
            };
            
            const statusBadge = statusBadges[doc.verification_status] || statusBadges['soumis'];
            const expirationDate = doc.expiration_date ? 
                ` | Expire le ${new Date(doc.expiration_date).toLocaleDateString('fr-FR')}` : '';
            const note = doc.note ? 
                `<div class="mt-2 small"><i class="ri-sticky-note-line me-1"></i>${doc.note}</div>` : '';
            
            return `
                <div class="document-item card mb-2" data-document-id="${doc.id}">
                    <div class="card-body p-3">
                        <div class="d-flex align-items-start justify-content-between">
                            <div class="flex-grow-1">
                                <div class="d-flex align-items-center mb-2">
                                    <i class="ri-file-text-line me-2 text-primary"></i>
                                    <strong>${doc.document_type_display}</strong>
                                    ${statusBadge}
                                </div>
                                <div class="small text-muted">
                                    <i class="ri-calendar-line me-1"></i>
                                    Ajouté le ${new Date(doc.created_at).toLocaleDateString('fr-FR')}${expirationDate}
                                </div>
                                ${note}
                            </div>
                            <div class="ms-3">
                                <div class="btn-group" role="group">
                                    <a href="${doc.file_url}" target="_blank" class="btn btn-sm btn-soft-primary" title="Voir">
                                        <i class="ri-eye-line"></i>
                                    </a>
                                    <a href="${doc.file_url}" download class="btn btn-sm btn-soft-secondary" title="Télécharger">
                                        <i class="ri-download-line"></i>
                                    </a>
                                    <button type="button" class="btn btn-sm btn-soft-info edit-document-btn" data-document-id="${doc.id}" title="Modifier">
                                        <i class="ri-edit-line"></i>
                                    </button>
                                    <button type="button" class="btn btn-sm btn-soft-danger delete-document-btn" data-document-id="${doc.id}" title="Supprimer">
                                        <i class="ri-delete-bin-line"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        attachDocumentEventListeners() {
            // Delete buttons
            document.querySelectorAll('.delete-document-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const documentId = btn.getAttribute('data-document-id');
                    this.deleteDocument(documentId);
                });
            });
            
            // Edit buttons
            document.querySelectorAll('.edit-document-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const documentId = btn.getAttribute('data-document-id');
                    this.editDocument(documentId);
                });
            });
        }

        async deleteDocument(documentId) {
            if (typeof Notifications !== 'undefined' && Notifications.confirmDelete) {
                const result = await Notifications.confirmDelete(
                    'Supprimer le document ?',
                    'Cette action est irréversible.'
                );
                if (!result.isConfirmed) return;
            } else {
                if (!confirm('Supprimer ce document ?')) return;
            }
            
            try {
                const response = await fetch(`/vehicles/${this.vehicleId}/documents/${documentId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': this.csrfToken
                    }
                });

                const data = await response.json();
                
                if (data.success) {
                    this.showDocumentNotification('success', data.message);
                    this.loadDocuments();
                } else {
                    this.showDocumentNotification('error', data.error || 'Erreur lors de la suppression');
                }
            } catch (error) {
                console.error('Error deleting document:', error);
                this.showDocumentNotification('error', 'Erreur lors de la suppression du document');
            }
        }

        async editDocument(documentId) {
            try {
                const response = await fetch(`/vehicles/${this.vehicleId}/documents/`, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                const data = await response.json();
                
                if (data.success) {
                    const doc = data.documents.find(d => d.id === documentId);
                    if (doc) {
                        // Populate modal form
                        document.getElementById('edit-document-id').value = doc.id;
                        document.getElementById('edit-document-type').value = doc.document_type;
                        document.getElementById('edit-verification-status').value = doc.verification_status;
                        document.getElementById('edit-document-expiration').value = doc.expiration_date || '';
                        document.getElementById('edit-document-note').value = doc.note || '';
                        document.getElementById('edit-verification-comment').value = doc.verification_comment || '';
                        
                        // Show modal
                        const modal = new bootstrap.Modal(document.getElementById('editDocumentModal'));
                        modal.show();
                    } else {
                        this.showDocumentNotification('error', 'Document non trouvé');
                    }
                } else {
                    this.showDocumentNotification('error', data.error || 'Erreur lors du chargement du document');
                }
            } catch (error) {
                console.error('Error loading document:', error);
                this.showDocumentNotification('error', 'Erreur lors du chargement du document');
            }
        }

        updateDocumentsCount(count) {
            const countEl = document.getElementById('documents-count');
            if (countEl) {
                countEl.textContent = count;
            }
        }

        showDocumentNotification(type, message) {
            const alertClass = type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info';
            const alertHtml = `
                <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            const documentsSection = document.getElementById('documents-section');
            if (documentsSection) {
                const existingAlert = documentsSection.querySelector('.alert');
                if (existingAlert) {
                    existingAlert.remove();
                }
                documentsSection.insertAdjacentHTML('afterbegin', alertHtml);
                
                // Auto-dismiss after 5 seconds
                setTimeout(() => {
                    const alert = documentsSection.querySelector('.alert');
                    if (alert) {
                        const bsAlert = new bootstrap.Alert(alert);
                        bsAlert.close();
                    }
                }, 5000);
            }
        }

        // ===== UTILITY FUNCTIONS =====
        
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func.apply(this, args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        showNotification(type, message) {
            if (typeof Notifications !== 'undefined') {
                Notifications[type](message);
            } else {
                alert(message);
            }
        }

        getCSRFToken() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new VehicleForm();
        });
    } else {
        new VehicleForm();
    }

})();
