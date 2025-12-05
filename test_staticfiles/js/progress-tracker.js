/**
 * Progress Tracker for Vehicle Declaration Forms
 * Tracks form completion and updates progress indicator in real-time
 */

(function() {
    'use strict';

    // Configuration
    const STEPS = {
        basic_info: {
            fields: ['immatriculation_aerienne', 'numero_francisation', 'plaque_immatriculation', 
                     'type_vehicule', 'date_premiere_circulation', 'nom_navire'],
            weight: 25
        },
        characteristics: {
            fields: ['marque', 'modele', 'masse_maximale_decollage_kg', 'puissance_moteur_kw',
                     'longueur_metres', 'puissance_fiscale_cv', 'cylindree_cm3', 'source_energie',
                     'numero_serie_aeronef', 'tonnage_tonneaux'],
            weight: 35
        },
        documents: {
            fields: [], // Documents are tracked separately
            weight: 25
        },
        review: {
            fields: [], // Review is manual
            weight: 15
        }
    };

    let progressTracker = null;

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        progressTracker = new ProgressTracker();
        progressTracker.init();
    });

    /**
     * ProgressTracker class
     */
    class ProgressTracker {
        constructor() {
            this.form = null;
            this.progressBar = null;
            this.completionBadge = null;
            this.currentStep = 'basic_info';
            this.completedFields = new Set();
            this.totalFields = 0;
        }

        /**
         * Initialize the progress tracker
         */
        init() {
            // Find form element
            this.form = document.querySelector('form[id*="vehicule"]');
            if (!this.form) {
                console.warn('Progress Tracker: Form not found');
                return;
            }

            // Find progress elements
            this.progressBar = document.getElementById('declaration-progress-bar');
            this.completionBadge = document.getElementById('completion-percentage');

            if (!this.progressBar || !this.completionBadge) {
                console.warn('Progress Tracker: Progress elements not found');
                return;
            }

            // Count total fields
            this.countTotalFields();

            // Attach event listeners
            this.attachEventListeners();

            // Initial calculation
            this.updateProgress();

            console.log('Progress Tracker initialized');
        }

        /**
         * Count total required fields in the form
         */
        countTotalFields() {
            const inputs = this.form.querySelectorAll('input[required], select[required], textarea[required]');
            this.totalFields = inputs.length;
            console.log(`Total required fields: ${this.totalFields}`);
        }

        /**
         * Attach event listeners to form fields
         */
        attachEventListeners() {
            // Listen to all input changes
            const inputs = this.form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                // Multiple event types to catch all changes
                ['input', 'change', 'blur'].forEach(eventType => {
                    input.addEventListener(eventType, () => {
                        this.updateProgress();
                    });
                });
            });
        }

        /**
         * Update progress based on filled fields
         */
        updateProgress() {
            this.completedFields.clear();

            // Check all form fields
            const inputs = this.form.querySelectorAll('input[required], select[required], textarea[required]');
            
            inputs.forEach(input => {
                if (this.isFieldCompleted(input)) {
                    this.completedFields.add(input.name || input.id);
                }
            });

            // Calculate percentage
            const percentage = this.totalFields > 0 
                ? Math.round((this.completedFields.size / this.totalFields) * 100)
                : 0;

            // Update UI
            this.updateProgressBar(percentage);
            this.updateCompletionBadge(percentage);
            this.updateStepIndicators(percentage);
        }

        /**
         * Check if a field is completed
         */
        isFieldCompleted(input) {
            const type = input.type;
            const value = input.value;

            // Skip hidden fields
            if (input.offsetParent === null) {
                return false;
            }

            // Check based on input type
            if (type === 'checkbox' || type === 'radio') {
                return input.checked;
            } else if (type === 'select-one' || type === 'select-multiple') {
                return value && value !== '';
            } else {
                return value && value.trim() !== '';
            }
        }

        /**
         * Update progress bar
         */
        updateProgressBar(percentage) {
            if (!this.progressBar) return;

            this.progressBar.style.width = `${percentage}%`;
            this.progressBar.setAttribute('aria-valuenow', percentage);

            // Change color based on completion
            this.progressBar.classList.remove('bg-danger', 'bg-warning', 'bg-info', 'bg-success');
            
            if (percentage < 25) {
                this.progressBar.classList.add('bg-danger');
            } else if (percentage < 50) {
                this.progressBar.classList.add('bg-warning');
            } else if (percentage < 75) {
                this.progressBar.classList.add('bg-info');
            } else {
                this.progressBar.classList.add('bg-success');
            }
        }

        /**
         * Update completion badge
         */
        updateCompletionBadge(percentage) {
            if (!this.completionBadge) return;

            this.completionBadge.textContent = `${percentage}%`;

            // Change badge color
            this.completionBadge.classList.remove('bg-danger', 'bg-warning', 'bg-info', 'bg-success');
            
            if (percentage < 25) {
                this.completionBadge.classList.add('bg-danger');
            } else if (percentage < 50) {
                this.completionBadge.classList.add('bg-warning');
            } else if (percentage < 75) {
                this.completionBadge.classList.add('bg-info');
            } else {
                this.completionBadge.classList.add('bg-success');
            }
        }

        /**
         * Update step indicators
         */
        updateStepIndicators(percentage) {
            const steps = document.querySelectorAll('.progress-step');
            
            steps.forEach((step, index) => {
                const stepPercentage = ((index + 1) / steps.length) * 100;
                
                if (percentage >= stepPercentage) {
                    step.classList.add('completed');
                } else {
                    step.classList.remove('completed');
                }
            });
        }

        /**
         * Get current completion percentage
         */
        getCompletionPercentage() {
            return this.totalFields > 0 
                ? Math.round((this.completedFields.size / this.totalFields) * 100)
                : 0;
        }

        /**
         * Get completed fields count
         */
        getCompletedFieldsCount() {
            return this.completedFields.size;
        }
    }

    // Expose to global scope
    window.ProgressTracker = ProgressTracker;
    window.progressTracker = progressTracker;
})();
