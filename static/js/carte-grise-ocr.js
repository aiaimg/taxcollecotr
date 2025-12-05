/**
 * Carte Grise Biométrique OCR Handler
 * Handles automatic form filling from carte grise biométrique images (recto + verso)
 */

(function () {
    'use strict';

    // OCR Handler Class
    class CarteGriseOCR {
        constructor() {
            this.rectoInput = document.getElementById('carte-grise-recto');
            this.versoInput = document.getElementById('carte-grise-verso');
            this.rectoDropZone = document.getElementById('ocr-drop-zone-recto');
            this.versoDropZone = document.getElementById('ocr-drop-zone-verso');
            this.processBtn = document.getElementById('process-ocr-btn');
            this.progressDiv = document.getElementById('ocr-progress');
            this.resultDiv = document.getElementById('ocr-result');

            this.rectoFile = null;
            this.versoFile = null;

            // Bind methods to instance (older browser compatibility)
            this.processOCR = this.processOCR.bind(this);
            this.handleFileSelect = this.handleFileSelect.bind(this);

            this.init();
        }

        init() {
            if (!this.rectoInput || !this.versoInput || !this.processBtn) {
                console.warn('OCR elements not found on page');
                return;
            }

            // Initialize Bootstrap tooltips if available
            try {
                if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                    tooltipTriggerList.map(function (tooltipTriggerEl) {
                        return new bootstrap.Tooltip(tooltipTriggerEl);
                    });
                }
            } catch (e) {
                console.warn('Bootstrap tooltips not available:', e);
            }

            // Bind events for recto
            this.setupDropZone(this.rectoDropZone, this.rectoInput, 'recto');
            this.rectoInput.addEventListener('change', (e) => this.handleFileSelect(e, 'recto'));

            // Bind events for verso
            this.setupDropZone(this.versoDropZone, this.versoInput, 'verso');
            this.versoInput.addEventListener('change', (e) => this.handleFileSelect(e, 'verso'));

            // Clear buttons
            const clearRectoBtn = document.getElementById('clear-recto');
            const clearVersoBtn = document.getElementById('clear-verso');

            if (clearRectoBtn) {
                clearRectoBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.clearFile('recto');
                });
            }

            if (clearVersoBtn) {
                clearVersoBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.clearFile('verso');
                });
            }

            // Process button
            this.processBtn.addEventListener('click', () => this.processOCR());
        }

        setupDropZone(dropZone, input, side) {
            if (!dropZone || !input) {
                console.warn(`Drop zone or input not found for ${side}`);
                return;
            }

            console.log(`Setting up drop zone for ${side}`);

            // Click to upload
            dropZone.addEventListener('click', (e) => {
                // Don't trigger if clicking a clear button
                if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                    return;
                }
                console.log(`Click on ${side} drop zone - triggering file input`);
                input.click();
            });

            // Prevent default drag behaviors on document
            ['dragenter', 'dragover'].forEach(eventName => {
                document.addEventListener(eventName, (e) => {
                    e.preventDefault();
                }, false);
            });

            // Drag and drop on drop zone
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                }, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => {
                    console.log(`Drag ${eventName} on ${side}`);
                    dropZone.classList.add('drag-over');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => {
                    dropZone.classList.remove('drag-over');
                }, false);
            });

            dropZone.addEventListener('drop', (e) => {
                console.log(`Drop on ${side}`);
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleDroppedFile(files[0], side);
                }
            }, false);
        }

        clearFile(side) {
            if (side === 'recto') {
                this.rectoFile = null;
                this.rectoInput.value = '';
                document.getElementById('recto-preview').style.display = 'none';
                this.rectoDropZone.classList.remove('has-file');
            } else {
                this.versoFile = null;
                this.versoInput.value = '';
                document.getElementById('verso-preview').style.display = 'none';
                this.versoDropZone.classList.remove('has-file');
            }

            this.updateProcessButton();
            this.hideResult();
        }

        updateProcessButton() {
            // Show process button only if at least recto is uploaded
            if (this.rectoFile) {
                this.processBtn.style.display = 'block';
            } else {
                this.processBtn.style.display = 'none';
            }
        }

        handleFileSelect(event, side) {
            const file = event.target.files[0];
            if (!file) return;

            this.handleDroppedFile(file, side);
        }

        handleDroppedFile(file, side) {
            // Validate file type
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                this.showError('Format non supporté. Utilisez JPG, PNG ou WEBP.');
                return;
            }

            // Validate file size (max 10MB)
            if (file.size > 10 * 1024 * 1024) {
                this.showError('Fichier trop volumineux. Max 10MB.');
                return;
            }

            // Store file
            if (side === 'recto') {
                this.rectoFile = file;
            } else {
                this.versoFile = file;
            }

            // Show preview
            this.showImagePreview(file, side);
            this.updateProcessButton();
            this.hideResult();
        }

        showImagePreview(file, side) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const previewDiv = document.getElementById(`${side}-preview`);
                const dropZone = document.getElementById(`ocr-drop-zone-${side}`);

                if (previewDiv) {
                    const img = previewDiv.querySelector('img');
                    if (img) {
                        img.src = e.target.result;
                    }
                    previewDiv.style.display = 'block';
                    dropZone.classList.add('has-file');
                }
            };
            reader.readAsDataURL(file);
        }

        async processOCR() {
            if (!this.rectoFile) {
                this.showError('Veuillez télécharger au moins le recto');
                return;
            }

            // Show progress
            this.showProgress();
            this.processBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('carte_grise_recto', this.rectoFile);
                if (this.versoFile) {
                    formData.append('carte_grise_verso', this.versoFile);
                }
                formData.append('csrfmiddlewaretoken', this.getCSRFToken());

                const response = await fetch('/vehicles/ajax/ocr/carte-grise/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                const result = await response.json();

                this.hideProgress();
                this.processBtn.disabled = false;

                if (result.success) {
                    this.handleSuccess(result);
                } else {
                    this.showError(result.error || 'Erreur lors de l\'extraction');
                }

            } catch (error) {
                console.error('OCR Error:', error);
                this.hideProgress();
                this.processBtn.disabled = false;
                this.showError('Erreur de connexion.');
            }
        }

        handleSuccess(result) {
            const { data, confidence } = result;

            // Fill form fields
            this.fillFormFields(data);

            // Show success message
            const fieldsExtracted = Object.values(data).filter(v => v !== null && v !== '').length;
            const totalFields = Object.keys(data).length;

            this.showSuccess(
                `✓ ${fieldsExtracted}/${totalFields} champs extraits (${confidence}% de confiance)`,
                data
            );

            // Scroll to form
            document.getElementById('vehicule-form').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }

        fillFormFields(data) {
            // Map OCR data to form fields
            const fieldMapping = {
                'plaque_immatriculation': data.plaque_immatriculation,
                'vin': data.vin,
                'nom_proprietaire': data.nom_proprietaire,
                'marque': data.marque,
                'modele': data.modele,
                'couleur': data.couleur,
                'date_premiere_circulation': data.date_premiere_circulation,
                'puissance_fiscale_cv': data.puissance_fiscale_cv,
                'cylindree_cm3': data.cylindree_cm3,
                'source_energie': data.source_energie
            };

            // Fill each field
            Object.keys(fieldMapping).forEach(fieldName => {
                const value = fieldMapping[fieldName];
                if (value !== null && value !== '') {
                    const field = document.getElementById(`id_${fieldName}`);
                    if (field) {
                        field.value = value;

                        // Highlight filled field
                        field.classList.add('border-success');
                        setTimeout(() => {
                            field.classList.remove('border-success');
                        }, 2000);

                        // Trigger change event for dependent fields
                        field.dispatchEvent(new Event('change', { bubbles: true }));
                        field.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }
            });
        }

        showProgress() {
            this.progressDiv.style.display = 'block';
            this.resultDiv.style.display = 'none';
        }

        hideProgress() {
            this.progressDiv.style.display = 'none';
        }

        showSuccess(message, data) {
            const extractedCount = Object.values(data).filter(v => v !== null && v !== '').length;

            this.resultDiv.innerHTML = `
                <div class="alert alert-success alert-sm mb-0 p-2">
                    <div class="d-flex align-items-center">
                        <i class="ri-checkbox-circle-line me-2"></i>
                        <small><strong>${extractedCount} champs extraits</strong></small>
                    </div>
                    <small class="text-muted d-block mt-1">
                        <i class="ri-information-line me-1"></i>
                        Vérifiez les données
                    </small>
                </div>
            `;
            this.resultDiv.style.display = 'block';
        }

        showError(message) {
            this.resultDiv.innerHTML = `
                <div class="alert alert-danger alert-sm mb-0 p-2">
                    <small><i class="ri-error-warning-line me-1"></i>${message}</small>
                </div>
            `;
            this.resultDiv.style.display = 'block';
        }

        hideResult() {
            this.resultDiv.style.display = 'none';
        }

        getCSRFToken() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new CarteGriseOCR();
        });
    } else {
        new CarteGriseOCR();
    }

})();
