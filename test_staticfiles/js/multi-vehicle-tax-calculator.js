/**
 * Multi-Vehicle Tax Calculator
 * Real-time tax calculation for terrestrial, aerial, and maritime vehicles
 * 
 * Requirements: 5.7, 7.3
 */

(function() {
    'use strict';

    // CSRF token helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    /**
     * Debounce function to limit API calls
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Format currency for display
     */
    function formatCurrency(amount) {
        if (!amount) return '0 Ar';
        return new Intl.NumberFormat('fr-MG', {
            style: 'decimal',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount) + ' Ar';
    }

    /**
     * Calculate tax for terrestrial vehicles
     */
    function calculateTerrestrialTax() {
        const puissanceInput = document.getElementById('id_puissance_fiscale_cv');
        const sourceEnergieInput = document.getElementById('id_source_energie');
        const dateCirculationInput = document.getElementById('id_date_premiere_circulation');
        const categorieInput = document.getElementById('id_categorie_vehicule');
        const resultContainer = document.getElementById('tax-calculation-result');

        if (!puissanceInput || !sourceEnergieInput || !dateCirculationInput || !resultContainer) {
            return;
        }

        const puissance = puissanceInput.value;
        const sourceEnergie = sourceEnergieInput.value;
        const dateCirculation = dateCirculationInput.value;
        const categorie = categorieInput ? categorieInput.value : 'Personnel';

        // Check if all required fields are filled
        if (!puissance || !sourceEnergie || !dateCirculation) {
            resultContainer.innerHTML = '<div class="alert alert-info"><i class="ri-information-line"></i> Remplissez tous les champs pour calculer la taxe</div>';
            return;
        }

        // Show loading state
        resultContainer.innerHTML = '<div class="alert alert-info"><i class="ri-loader-4-line spin"></i> Calcul en cours...</div>';

        // Make AJAX request
        fetch('/vehicles/ajax/calculate-tax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            },
            body: new URLSearchParams({
                vehicle_category: 'TERRESTRE',
                puissance_fiscale_cv: puissance,
                source_energie: sourceEnergie,
                date_premiere_circulation: dateCirculation,
                categorie_vehicule: categorie
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.is_exempt) {
                    resultContainer.innerHTML = `
                        <div class="alert alert-success">
                            <i class="ri-shield-check-line"></i>
                            <strong>Véhicule exonéré</strong>
                            <p class="mb-0">Ce véhicule est exonéré de taxe.</p>
                        </div>
                    `;
                } else {
                    resultContainer.innerHTML = `
                        <div class="alert alert-success">
                            <i class="ri-money-dollar-circle-line"></i>
                            <strong>Taxe annuelle: ${formatCurrency(data.tax_amount)}</strong>
                            <p class="mb-0 small">${data.calculation_method || 'Grille progressive'}</p>
                        </div>
                    `;
                }
            } else {
                resultContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="ri-error-warning-line"></i>
                        ${data.message || 'Impossible de calculer la taxe'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error calculating tax:', error);
            resultContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="ri-error-warning-line"></i>
                    Erreur lors du calcul de la taxe
                </div>
            `;
        });
    }

    /**
     * Calculate tax for aerial vehicles
     */
    function calculateAerialTax() {
        const masseInput = document.getElementById('id_masse_maximale_decollage_kg');
        const puissanceInput = document.getElementById('id_puissance_moteur_kw');
        const dateCirculationInput = document.getElementById('id_date_premiere_circulation');
        const categorieInput = document.getElementById('id_categorie_vehicule');
        const resultContainer = document.getElementById('tax-calculation-result');

        if (!resultContainer) {
            return;
        }

        const masse = masseInput ? masseInput.value : '';
        const puissance = puissanceInput ? puissanceInput.value : '';
        const dateCirculation = dateCirculationInput ? dateCirculationInput.value : '';
        const categorie = categorieInput ? categorieInput.value : 'Personnel';

        // Show loading state
        resultContainer.innerHTML = '<div class="alert alert-info"><i class="ri-loader-4-line spin"></i> Calcul en cours...</div>';

        // Make AJAX request
        fetch('/vehicles/ajax/calculate-tax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            },
            body: new URLSearchParams({
                vehicle_category: 'AERIEN',
                masse_maximale_decollage_kg: masse,
                puissance_moteur_kw: puissance,
                date_premiere_circulation: dateCirculation,
                categorie_vehicule: categorie
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.is_exempt) {
                    resultContainer.innerHTML = `
                        <div class="alert alert-success">
                            <i class="ri-shield-check-line"></i>
                            <strong>Véhicule exonéré</strong>
                            <p class="mb-0">Cet aéronef est exonéré de taxe.</p>
                        </div>
                    `;
                } else {
                    resultContainer.innerHTML = `
                        <div class="alert alert-success">
                            <i class="ri-plane-line"></i>
                            <strong>Taxe annuelle: ${formatCurrency(data.tax_amount)}</strong>
                            <p class="mb-0 small">${data.calculation_method || 'Tarif forfaitaire aérien'}</p>
                        </div>
                    `;
                }
            } else {
                resultContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="ri-error-warning-line"></i>
                        ${data.message || 'Impossible de calculer la taxe'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error calculating tax:', error);
            resultContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="ri-error-warning-line"></i>
                    Erreur lors du calcul de la taxe
                </div>
            `;
        });
    }

    /**
     * Calculate tax and classify maritime vehicles
     */
    function calculateMaritimeTax() {
        const longueurInput = document.getElementById('id_longueur_metres');
        const puissanceCVInput = document.getElementById('id_puissance_fiscale_cv');
        const puissanceKWInput = document.getElementById('id_puissance_moteur_kw');
        const typeVehiculeInput = document.getElementById('id_type_vehicule');
        const dateCirculationInput = document.getElementById('id_date_premiere_circulation');
        const categorieInput = document.getElementById('id_categorie_vehicule');
        const resultContainer = document.getElementById('tax-calculation-result');
        const classificationContainer = document.getElementById('maritime-classification-result');

        if (!resultContainer) {
            return;
        }

        const longueur = longueurInput ? longueurInput.value : '';
        const puissanceCV = puissanceCVInput ? puissanceCVInput.value : '';
        const puissanceKW = puissanceKWInput ? puissanceKWInput.value : '';
        const typeVehicule = typeVehiculeInput ? typeVehiculeInput.value : '';
        const dateCirculation = dateCirculationInput ? dateCirculationInput.value : '';
        const categorie = categorieInput ? categorieInput.value : 'Personnel';

        // Show loading state
        resultContainer.innerHTML = '<div class="alert alert-info"><i class="ri-loader-4-line spin"></i> Calcul en cours...</div>';
        if (classificationContainer) {
            classificationContainer.innerHTML = '<div class="alert alert-info"><i class="ri-loader-4-line spin"></i> Classification en cours...</div>';
        }

        // Make AJAX request for classification
        fetch('/vehicles/ajax/classify-maritime/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            },
            body: new URLSearchParams({
                longueur_metres: longueur,
                puissance_fiscale_cv: puissanceCV,
                puissance_moteur_kw: puissanceKW,
                type_vehicule: typeVehicule
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display classification
                if (classificationContainer) {
                    const confidenceBadge = data.confidence === 'HIGH' 
                        ? '<span class="badge bg-success">Haute confiance</span>'
                        : '<span class="badge bg-warning">Confiance moyenne</span>';
                    
                    classificationContainer.innerHTML = `
                        <div class="alert alert-info">
                            <i class="ri-ship-line"></i>
                            <strong>Classification: ${data.classification_display}</strong>
                            ${confidenceBadge}
                            <p class="mb-0 small mt-2">${data.explanation}</p>
                            ${data.allow_override ? '<p class="mb-0 small text-muted mt-1">Classification automatique. Contactez un administrateur si incorrecte.</p>' : ''}
                        </div>
                    `;
                }

                // Display tax amount
                if (data.tax_amount) {
                    resultContainer.innerHTML = `
                        <div class="alert alert-success">
                            <i class="ri-money-dollar-circle-line"></i>
                            <strong>Taxe annuelle: ${formatCurrency(data.tax_amount)}</strong>
                            <p class="mb-0 small">Tarif forfaitaire maritime (${data.classification_display})</p>
                        </div>
                    `;
                } else {
                    resultContainer.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="ri-error-warning-line"></i>
                            Classification effectuée mais tarif non disponible
                        </div>
                    `;
                }
            } else {
                resultContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="ri-error-warning-line"></i>
                        ${data.message || 'Impossible de calculer la taxe'}
                    </div>
                `;
                if (classificationContainer) {
                    classificationContainer.innerHTML = '';
                }
            }
        })
        .catch(error => {
            console.error('Error calculating maritime tax:', error);
            resultContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="ri-error-warning-line"></i>
                    Erreur lors du calcul de la taxe
                </div>
            `;
            if (classificationContainer) {
                classificationContainer.innerHTML = '';
            }
        });
    }

    /**
     * Convert power units (CV ↔ kW)
     */
    function convertPower(value, sourceUnit, targetInputId) {
        if (!value || value <= 0) {
            return;
        }

        fetch('/vehicles/ajax/convert-power/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            },
            body: new URLSearchParams({
                value: value,
                source_unit: sourceUnit
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const targetInput = document.getElementById(targetInputId);
                if (targetInput) {
                    targetInput.value = data.converted_value;
                    
                    // Show conversion info
                    const infoContainer = document.getElementById('power-conversion-info');
                    if (infoContainer) {
                        infoContainer.innerHTML = `
                            <small class="text-muted">
                                <i class="ri-information-line"></i>
                                ${data.formula}
                            </small>
                        `;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error converting power:', error);
        });
    }

    /**
     * Initialize terrestrial vehicle form
     */
    function initTerrestrialForm() {
        const puissanceInput = document.getElementById('id_puissance_fiscale_cv');
        const sourceEnergieInput = document.getElementById('id_source_energie');
        const dateCirculationInput = document.getElementById('id_date_premiere_circulation');

        if (!puissanceInput || !sourceEnergieInput || !dateCirculationInput) {
            return;
        }

        const debouncedCalculate = debounce(calculateTerrestrialTax, 500);

        puissanceInput.addEventListener('input', debouncedCalculate);
        sourceEnergieInput.addEventListener('change', debouncedCalculate);
        dateCirculationInput.addEventListener('change', debouncedCalculate);

        // Initial calculation if fields are pre-filled
        if (puissanceInput.value && sourceEnergieInput.value && dateCirculationInput.value) {
            calculateTerrestrialTax();
        }
    }

    /**
     * Initialize aerial vehicle form
     */
    function initAerialForm() {
        const masseInput = document.getElementById('id_masse_maximale_decollage_kg');
        const puissanceInput = document.getElementById('id_puissance_moteur_kw');
        const dateCirculationInput = document.getElementById('id_date_premiere_circulation');

        if (!masseInput && !puissanceInput && !dateCirculationInput) {
            return;
        }

        const debouncedCalculate = debounce(calculateAerialTax, 500);

        if (masseInput) masseInput.addEventListener('input', debouncedCalculate);
        if (puissanceInput) puissanceInput.addEventListener('input', debouncedCalculate);
        if (dateCirculationInput) dateCirculationInput.addEventListener('change', debouncedCalculate);

        // Initial calculation
        calculateAerialTax();
    }

    /**
     * Initialize maritime vehicle form
     */
    function initMaritimeForm() {
        const longueurInput = document.getElementById('id_longueur_metres');
        const puissanceCVInput = document.getElementById('id_puissance_fiscale_cv');
        const puissanceKWInput = document.getElementById('id_puissance_moteur_kw');
        const typeVehiculeInput = document.getElementById('id_type_vehicule');
        const unitSelector = document.getElementById('id_puissance_moteur_unit');

        if (!longueurInput && !puissanceCVInput && !puissanceKWInput) {
            return;
        }

        const debouncedCalculate = debounce(calculateMaritimeTax, 500);

        // Listen to changes for tax calculation
        if (longueurInput) longueurInput.addEventListener('input', debouncedCalculate);
        if (puissanceCVInput) puissanceCVInput.addEventListener('input', debouncedCalculate);
        if (puissanceKWInput) puissanceKWInput.addEventListener('input', debouncedCalculate);
        if (typeVehiculeInput) typeVehiculeInput.addEventListener('change', debouncedCalculate);

        // Power unit conversion
        if (unitSelector && puissanceCVInput && puissanceKWInput) {
            unitSelector.addEventListener('change', function() {
                const selectedUnit = this.value;
                
                if (selectedUnit === 'CV' && puissanceCVInput.value) {
                    // Convert CV to kW
                    convertPower(puissanceCVInput.value, 'CV', 'id_puissance_moteur_kw');
                } else if (selectedUnit === 'kW' && puissanceKWInput.value) {
                    // Convert kW to CV
                    convertPower(puissanceKWInput.value, 'kW', 'id_puissance_fiscale_cv');
                }
            });

            // Auto-convert when user enters value
            puissanceCVInput.addEventListener('input', debounce(function() {
                if (this.value && unitSelector.value === 'CV') {
                    convertPower(this.value, 'CV', 'id_puissance_moteur_kw');
                }
            }, 500));

            puissanceKWInput.addEventListener('input', debounce(function() {
                if (this.value && unitSelector.value === 'kW') {
                    convertPower(this.value, 'kW', 'id_puissance_fiscale_cv');
                }
            }, 500));
        }

        // Initial calculation if fields are pre-filled
        if ((longueurInput && longueurInput.value) || 
            (puissanceCVInput && puissanceCVInput.value) || 
            (puissanceKWInput && puissanceKWInput.value)) {
            calculateMaritimeTax();
        }
    }

    /**
     * Initialize on page load
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Detect which form is present and initialize accordingly
        const vehicleCategory = document.body.dataset.vehicleCategory;

        if (vehicleCategory === 'TERRESTRE' || document.getElementById('id_source_energie')) {
            initTerrestrialForm();
        } else if (vehicleCategory === 'AERIEN' || document.getElementById('id_immatriculation_aerienne')) {
            initAerialForm();
        } else if (vehicleCategory === 'MARITIME' || document.getElementById('id_numero_francisation')) {
            initMaritimeForm();
        }
    });

    // Add CSS for spin animation
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
