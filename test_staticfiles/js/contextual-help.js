/**
 * Contextual Help System
 * Manages tooltips and detailed help modals for vehicle declaration forms
 */

(function() {
    'use strict';

    // Initialize tooltips on page load
    document.addEventListener('DOMContentLoaded', function() {
        initializeTooltips();
        initializeHelpModals();
    });

    /**
     * Initialize Bootstrap tooltips
     */
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover focus',
                placement: 'top',
                html: true
            });
        });
        
        console.log(`Initialized ${tooltipTriggerList.length} tooltips`);
    }

    /**
     * Initialize help modal triggers
     */
    function initializeHelpModals() {
        const helpIcons = document.querySelectorAll('[data-help-modal]');
        
        helpIcons.forEach(function(icon) {
            icon.addEventListener('click', function(e) {
                e.preventDefault();
                const fieldName = this.dataset.helpModal;
                showHelpModal(fieldName);
            });
        });
        
        console.log(`Initialized ${helpIcons.length} help modals`);
    }

    /**
     * Show detailed help modal for a field
     */
    function showHelpModal(fieldName) {
        // Get help data from data attribute or fetch via AJAX
        const helpData = getHelpData(fieldName);
        
        if (!helpData) {
            console.error(`No help data found for field: ${fieldName}`);
            return;
        }

        // Create or update modal
        let modal = document.getElementById('help-modal');
        if (!modal) {
            modal = createHelpModal();
        }

        // Update modal content
        updateModalContent(modal, helpData);

        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    /**
     * Create help modal element (if not already in DOM)
     * Note: The modal should be included via template partial
     */
    function createHelpModal() {
        // Check if modal already exists in DOM (from template)
        let modal = document.getElementById('help-modal');
        if (modal) {
            return modal;
        }
        
        // Fallback: create modal dynamically if not in template
        const modalHTML = `
            <div class="modal fade" id="help-modal" tabindex="-1" aria-labelledby="help-modal-label" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="help-modal-label">
                                <i class="ri-question-line me-2"></i>
                                <span id="help-modal-title">Aide</span>
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div id="help-modal-description" class="mb-4">
                                <p class="text-muted"></p>
                            </div>
                            
                            <div id="help-modal-examples" class="mb-4" style="display: none;">
                                <h6 class="text-primary mb-3">
                                    <i class="ri-lightbulb-line me-2"></i>
                                    Exemples
                                </h6>
                                <div class="card bg-light border-0">
                                    <div class="card-body">
                                        <ul id="help-modal-examples-list" class="list-unstyled mb-0"></ul>
                                    </div>
                                </div>
                            </div>
                            
                            <div id="help-modal-validation" class="mb-4" style="display: none;">
                                <h6 class="text-primary mb-3">
                                    <i class="ri-checkbox-circle-line me-2"></i>
                                    Règles de validation
                                </h6>
                                <div class="card bg-light border-0">
                                    <div class="card-body">
                                        <ul id="help-modal-validation-list" class="list-unstyled mb-0"></ul>
                                    </div>
                                </div>
                            </div>
                            
                            <div id="help-modal-legal" class="alert alert-info alert-border-left" style="display: none;">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        <i class="ri-book-line display-6"></i>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h6 class="alert-heading">Référence légale</h6>
                                        <p id="help-modal-legal-text" class="mb-0"></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="ri-close-line me-1"></i>
                                Fermer
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        const div = document.createElement('div');
        div.innerHTML = modalHTML;
        document.body.appendChild(div.firstElementChild);
        
        return document.getElementById('help-modal');
    }

    /**
     * Update modal content with help data
     */
    function updateModalContent(modal, helpData) {
        // Title
        const titleElement = modal.querySelector('#help-modal-title');
        if (titleElement) {
            titleElement.textContent = helpData.title || 'Aide';
        }
        
        // Description
        const descElement = modal.querySelector('#help-modal-description p');
        if (descElement) {
            descElement.textContent = helpData.description || '';
        } else {
            const descContainer = modal.querySelector('#help-modal-description');
            if (descContainer) {
                descContainer.innerHTML = `<p class="text-muted">${helpData.description || ''}</p>`;
            }
        }
        
        // Examples
        const examplesSection = modal.querySelector('#help-modal-examples');
        const examplesList = modal.querySelector('#help-modal-examples-list');
        if (helpData.examples && helpData.examples.length > 0) {
            if (examplesSection) examplesSection.style.display = 'block';
            if (examplesList) {
                examplesList.innerHTML = helpData.examples.map(ex => 
                    `<li class="mb-2"><i class="ri-arrow-right-s-line text-success me-2"></i>${ex}</li>`
                ).join('');
            }
        } else {
            if (examplesSection) examplesSection.style.display = 'none';
        }
        
        // Validation rules
        const validationSection = modal.querySelector('#help-modal-validation');
        const validationList = modal.querySelector('#help-modal-validation-list');
        if (helpData.validation_rules && helpData.validation_rules.length > 0) {
            if (validationSection) validationSection.style.display = 'block';
            if (validationList) {
                validationList.innerHTML = helpData.validation_rules.map(rule => 
                    `<li class="mb-2"><i class="ri-check-line text-success me-2"></i>${rule}</li>`
                ).join('');
            }
        } else {
            if (validationSection) validationSection.style.display = 'none';
        }
        
        // Legal reference
        const legalSection = modal.querySelector('#help-modal-legal');
        const legalText = modal.querySelector('#help-modal-legal-text');
        if (helpData.legal_reference) {
            if (legalSection) legalSection.style.display = 'block';
            if (legalText) legalText.textContent = helpData.legal_reference;
        } else {
            if (legalSection) legalSection.style.display = 'none';
        }
    }

    /**
     * Get help data for a field
     * This should be populated from the backend via data attributes
     */
    function getHelpData(fieldName) {
        // Try to get from data attribute first
        const element = document.querySelector(`[data-help-modal="${fieldName}"]`);
        if (element && element.dataset.helpData) {
            try {
                return JSON.parse(element.dataset.helpData);
            } catch (e) {
                console.error('Error parsing help data:', e);
            }
        }
        
        // Fallback: return null and let backend handle it
        return null;
    }

    // Expose functions globally if needed
    window.ContextualHelp = {
        initializeTooltips: initializeTooltips,
        showHelpModal: showHelpModal
    };
})();
