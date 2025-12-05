/**
 * Tax Calculator for Public Home Page
 * Tax Collector Platform - Madagascar
 * Supports: Terrestrial, Maritime, and Aerial vehicles
 * Uses backend API for real tariff grid calculations
 */

(function() {
    'use strict';

    // API endpoint for tax simulation
    const TAX_SIMULATION_API = '/api/tax-simulation/';

    document.addEventListener('DOMContentLoaded', function() {
        initCalculator();
        initVehicleTypeSwitch();
        initYearValidation();
    });

    /**
     * Initialize vehicle type field switching
     */
    function initVehicleTypeSwitch() {
        const vehicleTypeSelect = document.getElementById('vehicle-type');
        if (!vehicleTypeSelect) return;

        vehicleTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            updateFieldsVisibility(selectedType);
        });

        // Initialize with default state
        updateFieldsVisibility(vehicleTypeSelect.value);
    }

    /**
     * Show/hide fields based on vehicle type
     */
    function updateFieldsVisibility(vehicleType) {
        // Hide all type-specific fields first
        document.querySelectorAll('.field-terrestre, .field-maritime, .field-aerien').forEach(function(el) {
            el.style.display = 'none';
            // Clear inputs when hiding
            const input = el.querySelector('input');
            if (input) input.value = '';
        });

        // Show fields for selected type
        if (vehicleType === 'terrestre') {
            document.querySelectorAll('.field-terrestre').forEach(function(el) {
                el.style.display = '';
            });
        } else if (vehicleType === 'maritime') {
            document.querySelectorAll('.field-maritime').forEach(function(el) {
                el.style.display = '';
            });
        } else if (vehicleType === 'aerien') {
            document.querySelectorAll('.field-aerien').forEach(function(el) {
                el.style.display = '';
            });
        }

        // Hide result when type changes
        const resultDiv = document.getElementById('calculator-result');
        if (resultDiv) {
            resultDiv.style.display = 'none';
        }
    }

    /**
     * Initialize calculator form
     */
    function initCalculator() {
        const form = document.getElementById('tax-calculator-form');
        const resultDiv = document.getElementById('calculator-result');
        
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            calculateTax();
        });

        form.addEventListener('reset', function() {
            setTimeout(function() {
                if (resultDiv) {
                    resultDiv.style.display = 'none';
                }
                // Reset field visibility
                updateFieldsVisibility('');
            }, 10);
        });
    }

    /**
     * Main tax calculation function - calls backend API
     */
    function calculateTax() {
        const vehicleType = document.getElementById('vehicle-type').value;
        const anneeMiseCirculation = document.getElementById('annee-mise-circulation').value;
        const anneeFiscale = document.getElementById('annee-fiscale').value;

        // Validation
        if (!vehicleType) {
            showError(getTranslation('selectVehicleType'));
            return;
        }

        if (!anneeMiseCirculation) {
            showError(getTranslation('enterServiceYear'));
            setFieldError(document.getElementById('annee-mise-circulation'), getTranslation('yearNotNumber'));
            return;
        }

        const currentYear = new Date().getFullYear();
        const yearValue = parseInt(anneeMiseCirculation, 10);
        if (isNaN(yearValue)) {
            showError(getTranslation('yearNotNumber'));
            setFieldError(document.getElementById('annee-mise-circulation'), getTranslation('yearNotNumber'));
            return;
        }
        if (yearValue < 0) {
            showError(getTranslation('yearNegative'));
            setFieldError(document.getElementById('annee-mise-circulation'), getTranslation('yearNegative'));
            return;
        }
        if (yearValue < 1900) {
            showError(getTranslation('yearTooSmall'));
            setFieldError(document.getElementById('annee-mise-circulation'), getTranslation('yearTooSmall'));
            return;
        }
        if (yearValue > currentYear) {
            showError(getTranslation('yearTooLarge'));
            setFieldError(document.getElementById('annee-mise-circulation'), getTranslation('yearTooLarge'));
            return;
        }

        // Build form data
        const formData = new FormData();
        formData.append('vehicle_type', vehicleType);
        formData.append('annee_mise_circulation', anneeMiseCirculation);
        formData.append('annee_fiscale', anneeFiscale);

        // Add type-specific fields
        if (vehicleType === 'terrestre') {
            const puissance = document.getElementById('puissance').value;
            const sourceEnergie = document.getElementById('source-energie').value;
            if (!puissance) {
                showError(getTranslation('enterPower'));
                return;
            }
            formData.append('puissance', puissance);
            formData.append('source_energie', sourceEnergie);
        } else if (vehicleType === 'maritime') {
            const longueur = document.getElementById('longueur').value;
            const tonnage = document.getElementById('tonnage').value;
            if (!longueur || !tonnage) {
                showError(getTranslation('enterMaritimeData'));
                return;
            }
            formData.append('longueur', longueur);
            formData.append('tonnage', tonnage);
        } else if (vehicleType === 'aerien') {
            const masse = document.getElementById('masse-decollage').value;
            if (!masse) {
                showError(getTranslation('enterMass'));
                return;
            }
            formData.append('masse_decollage', masse);
        }

        // Show loading state
        const submitBtn = document.querySelector('.btn-calculate');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="ri-loader-4-line me-2 spin"></i>' + getTranslation('calculating');
        submitBtn.disabled = true;

        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Call API
        fetch(TAX_SIMULATION_API, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            // Restore button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;

            if (data.success) {
                displayResults(data, vehicleType);
            } else {
                showError(data.message || getTranslation('calculationError'));
            }
        })
        .catch(function(error) {
            // Restore button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            
            console.error('Tax calculation error:', error);
            showError(getTranslation('calculationError'));
        });
    }

    /**
     * Display calculation results
     */
    function displayResults(data, vehicleType) {
        const resultDiv = document.getElementById('calculator-result');
        const totalTaxeEl = document.getElementById('total-taxe');
        const vehicleAgeEl = document.getElementById('vehicle-age');
        const gridInfoRow = document.getElementById('result-grid-info');
        const gridInfoText = document.getElementById('grid-info-text');

        if (!resultDiv) return;

        // Format total tax
        totalTaxeEl.textContent = formatCurrency(parseFloat(data.total_tax));
        
        // Display vehicle age
        if (vehicleAgeEl) {
            vehicleAgeEl.textContent = data.vehicle_age + ' ' + getTranslation('years');
        }
        
        // Display grid info if available
        if (data.grid_info && gridInfoRow && gridInfoText) {
            let gridText = '';
            if (data.grid_info.type === 'TERRESTRE') {
                gridText = data.grid_info.puissance_range + ' • ' + 
                           data.grid_info.source_energie + ' • ' + 
                           data.grid_info.age_range;
            } else if (data.grid_info.type === 'MARITIME') {
                gridText = getTranslation('maritime') + ' - ' + data.grid_info.category;
            } else if (data.grid_info.type === 'AERIEN') {
                gridText = getTranslation('aerial');
            }
            gridInfoText.textContent = gridText;
            gridInfoRow.style.display = '';
        } else if (gridInfoRow) {
            gridInfoRow.style.display = 'none';
        }

        // Show result with animation
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Announce to screen readers
        announceResult(parseFloat(data.total_tax), vehicleType);
    }

    /**
     * Format number as currency (Ariary)
     */
    function formatCurrency(amount) {
        return new Intl.NumberFormat('fr-MG', {
            style: 'decimal',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount) + ' Ar';
    }

    /**
     * Show error message
     */
    function showError(message) {
        // Remove existing error
        const existingError = document.querySelector('.calculator-error');
        if (existingError) existingError.remove();

        // Create error alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger calculator-error mt-3';
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = '<i class="ri-error-warning-line me-2"></i>' + message;
        
        const form = document.getElementById('tax-calculator-form');
        form.parentNode.insertBefore(alertDiv, form.nextSibling);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            alertDiv.remove();
        }, 5000);
    }

    /**
     * Announce result to screen readers
     */
    function announceResult(totalTax, vehicleType) {
        const liveRegion = document.getElementById('aria-live-region');
        if (liveRegion) {
            const typeLabels = {
                terrestre: 'véhicule terrestre',
                maritime: 'navire',
                aerien: 'aéronef'
            };
            liveRegion.textContent = '';
            setTimeout(function() {
                liveRegion.textContent = 'Résultat pour ' + (typeLabels[vehicleType] || 'véhicule') + ': ' + formatCurrency(totalTax);
            }, 100);
        }
    }

    function initYearValidation() {
        const input = document.getElementById('annee-mise-circulation');
        if (!input) return;
        const currentYear = new Date().getFullYear();
        input.setAttribute('min', '1900');
        input.setAttribute('max', String(currentYear));
        const validate = function() {
            clearFieldError(input);
            const v = String(input.value || '').trim();
            if (!v) return;
            const n = parseInt(v, 10);
            if (isNaN(n)) {
                setFieldError(input, getTranslation('yearNotNumber'));
                return;
            }
            if (n < 0) {
                setFieldError(input, getTranslation('yearNegative'));
                return;
            }
            if (n < 1900) {
                setFieldError(input, getTranslation('yearTooSmall'));
                return;
            }
            if (n > currentYear) {
                setFieldError(input, getTranslation('yearTooLarge'));
                return;
            }
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        };
        input.addEventListener('input', validate);
        input.addEventListener('change', validate);
        validate();
    }

    function setFieldError(el, message) {
        if (!el) return;
        el.classList.remove('is-valid');
        el.classList.add('is-invalid');
        let feedback = el.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            el.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
        feedback.classList.add('d-block');
    }

    function clearFieldError(el) {
        if (!el) return;
        el.classList.remove('is-invalid');
        const feedback = el.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.classList.remove('d-block');
            if (!feedback.textContent) {
                feedback.remove();
            }
        }
    }

    /**
     * Get translated message based on current language
     */
    function getTranslation(key) {
        // Detect current language from html lang attribute or URL
        const lang = document.documentElement.lang || 'fr';
        
        const translations = {
            fr: {
                selectVehicleType: 'Veuillez sélectionner un type de véhicule.',
                enterServiceYear: 'Veuillez entrer une année de mise en service valide.',
                enterPower: 'Veuillez entrer la puissance fiscale (CV).',
                enterMaritimeData: 'Veuillez entrer la longueur et le tonnage du navire.',
                enterMass: 'Veuillez entrer la masse maximale au décollage.',
                calculationError: 'Erreur lors du calcul de la taxe.',
                calculating: 'Calcul en cours...',
                yearNotNumber: 'Veuillez entrer une année valide.',
                yearNegative: "L'année ne peut pas être négative.",
                yearTooLarge: "L'année ne peut pas dépasser l'année en cours.",
                yearTooSmall: "L'année ne peut pas être inférieure à 1900.",
                years: 'ans',
                maritime: 'Maritime',
                aerial: 'Aérien'
            },
            mg: {
                selectVehicleType: 'Misafidiana karazana fiara azafady.',
                enterServiceYear: 'Ampidiro ny taona nanombohana nampiasa azafady.',
                enterPower: 'Ampidiro ny hery (CV) azafady.',
                enterMaritimeData: 'Ampidiro ny halava sy ny lanjan-tentina azafady.',
                enterMass: 'Ampidiro ny lanja fara-tampony amin\'ny fiakarana azafady.',
                calculationError: 'Nisy olana tamin\'ny kajiana ny hetra.',
                calculating: 'Manao kajy...',
                yearNotNumber: 'Ampidiro taona manan-kery azafady.',
                yearNegative: 'Tsy azo ho isa miiba ny taona.',
                yearTooLarge: 'Tsy azo mihoatra ny taona ankehitriny ny taona.',
                yearTooSmall: 'Tsy afaka latsaky ny 1900 ny taona.',
                years: 'taona',
                maritime: 'An-dranomasina',
                aerial: 'An-habakabaka'
            }
        };

        const langTranslations = translations[lang] || translations['fr'];
        return langTranslations[key] || translations['fr'][key] || key;
    }

    // Add CSS for spinner animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .spin {
            animation: spin 1s linear infinite;
            display: inline-block;
        }
    `;
    document.head.appendChild(style);

})();
