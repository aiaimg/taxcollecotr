/**
 * Cash Payment System - JavaScript Module
 * Handles form validation, AJAX requests, and real-time calculations
 */

(function() {
    'use strict';

    // ============================================================================
    // FORM VALIDATION
    // ============================================================================

    /**
     * Validate required fields
     */
    function validateRequiredField(field, errorMessage) {
        const value = field.value.trim();
        const feedbackElement = field.parentElement.querySelector('.invalid-feedback') || 
                               field.parentElement.querySelector('.error-message');
        
        if (!value) {
            field.classList.add('is-invalid');
            if (feedbackElement) {
                feedbackElement.textContent = errorMessage;
                feedbackElement.style.display = 'block';
            }
            return false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (feedbackElement) {
                feedbackElement.style.display = 'none';
            }
            return true;
        }
    }

    /**
     * Validate email format
     */
    function validateEmail(emailField) {
        const email = emailField.value.trim();
        if (!email) return true; // Email is optional
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const feedbackElement = emailField.parentElement.querySelector('.invalid-feedback') || 
                               emailField.parentElement.querySelector('.error-message');
        
        if (!emailRegex.test(email)) {
            emailField.classList.add('is-invalid');
            if (feedbackElement) {
                feedbackElement.textContent = 'Format d\'email invalide';
                feedbackElement.style.display = 'block';
            }
            return false;
        } else {
            emailField.classList.remove('is-invalid');
            emailField.classList.add('is-valid');
            if (feedbackElement) {
                feedbackElement.style.display = 'none';
            }
            return true;
        }
    }

    /**
     * Validate phone number format
     */
    function validatePhone(phoneField) {
        const phone = phoneField.value.trim();
        if (!phone) return false;
        
        // Madagascar phone format: 10 digits starting with 03
        const phoneRegex = /^(03[234]\d{7}|26[123]\d{7})$/;
        const feedbackElement = phoneField.parentElement.querySelector('.invalid-feedback') || 
                               phoneField.parentElement.querySelector('.error-message');
        
        if (!phoneRegex.test(phone.replace(/\s/g, ''))) {
            phoneField.classList.add('is-invalid');
            if (feedbackElement) {
                feedbackElement.textContent = 'Format de téléphone invalide (ex: 0321234567)';
                feedbackElement.style.display = 'block';
            }
            return false;
        } else {
            phoneField.classList.remove('is-invalid');
            phoneField.classList.add('is-valid');
            if (feedbackElement) {
                feedbackElement.style.display = 'none';
            }
            return true;
        }
    }

    /**
     * Validate numeric field
     */
    function validateNumeric(field, min = 0, max = null) {
        const value = parseFloat(field.value);
        const feedbackElement = field.parentElement.querySelector('.invalid-feedback') || 
                               field.parentElement.querySelector('.error-message');
        
        if (isNaN(value) || value < min || (max !== null && value > max)) {
            field.classList.add('is-invalid');
            if (feedbackElement) {
                let message = 'Valeur numérique invalide';
                if (min > 0) message += ` (minimum: ${min})`;
                if (max !== null) message += ` (maximum: ${max})`;
                feedbackElement.textContent = message;
                feedbackElement.style.display = 'block';
            }
            return false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (feedbackElement) {
                feedbackElement.style.display = 'none';
            }
            return true;
        }
    }

    /**
     * Validate date field
     */
    function validateDate(dateField) {
        const value = dateField.value;
        const feedbackElement = dateField.parentElement.querySelector('.invalid-feedback') || 
                               dateField.parentElement.querySelector('.error-message');
        
        if (!value) {
            dateField.classList.add('is-invalid');
            if (feedbackElement) {
                feedbackElement.textContent = 'Date requise';
                feedbackElement.style.display = 'block';
            }
            return false;
        }
        
        const date = new Date(value);
        const today = new Date();
        
        if (date > today) {
            dateField.classList.add('is-invalid');
            if (feedbackElement) {
                feedbackElement.textContent = 'La date ne peut pas être dans le futur';
                feedbackElement.style.display = 'block';
            }
            return false;
        } else {
            dateField.classList.remove('is-invalid');
            dateField.classList.add('is-valid');
            if (feedbackElement) {
                feedbackElement.style.display = 'none';
            }
            return true;
        }
    }

    /**
     * Validate vehicle plate format
     */
    function validateVehiclePlate(plateField) {
        const plate = plateField.value.trim().toUpperCase();
        if (!plate) return false;
        
        // Madagascar plate format: 1234 ABC or 1234-ABC
        const plateRegex = /^\d{4}[\s-]?[A-Z]{2,3}$/;
        const feedbackElement = plateField.parentElement.querySelector('.invalid-feedback') || 
                               plateField.parentElement.querySelector('.error-message');
        
        if (!plateRegex.test(plate)) {
            plateField.classList.add('is-invalid');
            if (feedbackElement) {
                feedbackElement.textContent = 'Format de plaque invalide (ex: 1234 ABC)';
                feedbackElement.style.display = 'block';
            }
            return false;
        } else {
            plateField.classList.remove('is-invalid');
            plateField.classList.add('is-valid');
            if (feedbackElement) {
                feedbackElement.style.display = 'none';
            }
            return true;
        }
    }

    // ============================================================================
    // FORM VALIDATION SETUP
    // ============================================================================

    /**
     * Setup real-time validation for payment form
     */
    function setupFormValidation() {
        const form = document.getElementById('payment-form');
        if (!form) return;

        // Customer name validation
        const customerNameField = document.querySelector('[name="customer_name"]');
        if (customerNameField) {
            customerNameField.addEventListener('blur', function() {
                validateRequiredField(this, 'Le nom du client est requis');
            });
            customerNameField.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateRequiredField(this, 'Le nom du client est requis');
                }
            });
        }

        // Customer phone validation
        const customerPhoneField = document.querySelector('[name="customer_phone"]');
        if (customerPhoneField) {
            customerPhoneField.addEventListener('blur', function() {
                validatePhone(this);
            });
            customerPhoneField.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validatePhone(this);
                }
            });
        }

        // Customer email validation
        const customerEmailField = document.querySelector('[name="customer_email"]');
        if (customerEmailField) {
            customerEmailField.addEventListener('blur', function() {
                validateEmail(this);
            });
            customerEmailField.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateEmail(this);
                }
            });
        }

        // Vehicle plate validation
        const vehiclePlateField = document.querySelector('[name="vehicle_plate"]');
        if (vehiclePlateField) {
            vehiclePlateField.addEventListener('blur', function() {
                const hasPlateCheckbox = document.querySelector('[name="has_plate"]');
                if (!hasPlateCheckbox || hasPlateCheckbox.checked) {
                    validateVehiclePlate(this);
                }
            });
            vehiclePlateField.addEventListener('input', function() {
                this.value = this.value.toUpperCase();
                if (this.classList.contains('is-invalid')) {
                    const hasPlateCheckbox = document.querySelector('[name="has_plate"]');
                    if (!hasPlateCheckbox || hasPlateCheckbox.checked) {
                        validateVehiclePlate(this);
                    }
                }
            });
        }

        // Engine power validation
        const enginePowerField = document.querySelector('[name="engine_power_cv"]');
        if (enginePowerField) {
            enginePowerField.addEventListener('blur', function() {
                validateNumeric(this, 1, 1000);
            });
            enginePowerField.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateNumeric(this, 1, 1000);
                }
            });
        }

        // Engine capacity validation
        const engineCapacityField = document.querySelector('[name="engine_capacity_cc"]');
        if (engineCapacityField) {
            engineCapacityField.addEventListener('blur', function() {
                validateNumeric(this, 50, 10000);
            });
            engineCapacityField.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateNumeric(this, 50, 10000);
                }
            });
        }

        // First circulation date validation
        const firstCirculationField = document.querySelector('[name="first_circulation_date"]');
        if (firstCirculationField) {
            firstCirculationField.addEventListener('blur', function() {
                validateDate(this);
            });
            firstCirculationField.addEventListener('change', function() {
                if (this.classList.contains('is-invalid')) {
                    validateDate(this);
                }
            });
        }

        // Amount tendered validation
        const amountTenderedField = document.querySelector('[name="amount_tendered"]');
        if (amountTenderedField) {
            amountTenderedField.addEventListener('blur', function() {
                validateNumeric(this, 0);
            });
            amountTenderedField.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateNumeric(this, 0);
                }
            });
        }

        // Form submission validation
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const isNewCustomer = document.getElementById('is-new-customer')?.checked;

            // Validate customer fields if new customer
            if (isNewCustomer) {
                if (customerNameField && !validateRequiredField(customerNameField, 'Le nom du client est requis')) {
                    isValid = false;
                }
                if (customerPhoneField && !validatePhone(customerPhoneField)) {
                    isValid = false;
                }
                if (customerEmailField && customerEmailField.value && !validateEmail(customerEmailField)) {
                    isValid = false;
                }
            } else {
                // Validate customer selection for existing customer
                const selectedCustomerId = document.getElementById('selected-customer-id');
                if (selectedCustomerId && !selectedCustomerId.value) {
                    if (window.Notifications) {
                        window.Notifications.warning('Veuillez sélectionner un client');
                    } else {
                        alert('Veuillez sélectionner un client');
                    }
                    isValid = false;
                }
            }

            // Validate vehicle fields
            const hasPlateCheckbox = document.querySelector('[name="has_plate"]');
            if (vehiclePlateField && (!hasPlateCheckbox || hasPlateCheckbox.checked)) {
                if (!validateVehiclePlate(vehiclePlateField)) {
                    isValid = false;
                }
            }

            const vehicleTypeField = document.querySelector('[name="vehicle_type"]');
            if (vehicleTypeField && !vehicleTypeField.value) {
                if (window.Notifications) {
                    window.Notifications.warning('Veuillez sélectionner un type de véhicule');
                } else {
                    alert('Veuillez sélectionner un type de véhicule');
                }
                isValid = false;
            }

            if (enginePowerField && !validateNumeric(enginePowerField, 1, 1000)) {
                isValid = false;
            }

            if (firstCirculationField && !validateDate(firstCirculationField)) {
                isValid = false;
            }

            // Validate tax calculation
            const taxAmountField = document.getElementById('tax-amount-hidden');
            if (!taxAmountField || !taxAmountField.value || parseFloat(taxAmountField.value) === 0) {
                if (window.Notifications) {
                    window.Notifications.warning('Veuillez calculer la taxe avant de continuer');
                } else {
                    alert('Veuillez calculer la taxe avant de continuer');
                }
                isValid = false;
            }

            // Validate payment amount
            if (amountTenderedField) {
                if (!validateNumeric(amountTenderedField, 0)) {
                    isValid = false;
                }
                
                const taxAmount = parseFloat(taxAmountField?.value || 0);
                const tendered = parseFloat(amountTenderedField.value || 0);
                
                if (tendered < taxAmount) {
                    if (window.Notifications) {
                        window.Notifications.error('Le montant remis est insuffisant');
                    } else {
                        alert('Le montant remis est insuffisant');
                    }
                    isValid = false;
                }
            }

            if (!isValid) {
                e.preventDefault();
                // Scroll to first invalid field
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
            }
        });
    }

    // ============================================================================
    // SESSION FORM VALIDATION
    // ============================================================================

    /**
     * Setup validation for session open form
     */
    function setupSessionOpenValidation() {
        const form = document.getElementById('session-open-form');
        if (!form) return;

        const openingBalanceField = document.querySelector('[name="opening_balance"]');
        
        if (openingBalanceField) {
            openingBalanceField.addEventListener('blur', function() {
                validateNumeric(this, 0);
            });
        }

        form.addEventListener('submit', function(e) {
            if (openingBalanceField && !validateNumeric(openingBalanceField, 0)) {
                e.preventDefault();
                if (window.Notifications) {
                    window.Notifications.error('Veuillez entrer un solde d\'ouverture valide');
                } else {
                    alert('Veuillez entrer un solde d\'ouverture valide');
                }
            }
        });
    }

    /**
     * Setup validation for session close form
     */
    function setupSessionCloseValidation() {
        const form = document.getElementById('session-close-form');
        if (!form) return;
        
        // Skip validation if form has data-skip-validation attribute
        if (form.getAttribute('data-skip-validation') === 'true') return;

        const closingBalanceField = document.querySelector('[name="closing_balance"]');
        
        if (closingBalanceField) {
            closingBalanceField.addEventListener('blur', function() {
                validateNumeric(this, 0);
            });

            // Calculate discrepancy in real-time
            closingBalanceField.addEventListener('input', function() {
                const expectedBalance = parseFloat(document.getElementById('expected-balance')?.textContent.replace(/[^\d.-]/g, '') || 0);
                const closingBalance = parseFloat(this.value || 0);
                const discrepancy = closingBalance - expectedBalance;
                
                const discrepancyDisplay = document.getElementById('discrepancy-display');
                if (discrepancyDisplay) {
                    discrepancyDisplay.textContent = discrepancy.toLocaleString('fr-FR', {minimumFractionDigits: 2}) + ' Ar';
                    
                    if (Math.abs(discrepancy) > 0) {
                        discrepancyDisplay.classList.remove('text-success');
                        discrepancyDisplay.classList.add('text-danger');
                    } else {
                        discrepancyDisplay.classList.remove('text-danger');
                        discrepancyDisplay.classList.add('text-success');
                    }
                }
            });
        }

        form.addEventListener('submit', function(e) {
            if (closingBalanceField && !validateNumeric(closingBalanceField, 0)) {
                e.preventDefault();
                if (window.Notifications) {
                    window.Notifications.error('Veuillez entrer un solde de clôture valide');
                } else {
                    alert('Veuillez entrer un solde de clôture valide');
                }
            }
        });
    }

    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================

    /**
     * Format currency for display
     */
    function formatCurrency(amount) {
        return parseFloat(amount).toLocaleString('fr-FR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    /**
     * Show loading spinner
     */
    function showLoading(element) {
        if (element) {
            element.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Chargement...</span></div>';
            element.disabled = true;
        }
    }

    /**
     * Hide loading spinner
     */
    function hideLoading(element, originalText) {
        if (element) {
            element.innerHTML = originalText;
            element.disabled = false;
        }
    }

    // ============================================================================
    // INITIALIZATION
    // ============================================================================

    document.addEventListener('DOMContentLoaded', function() {
        // Setup form validation based on page
        setupFormValidation();
        setupSessionOpenValidation();
        setupSessionCloseValidation();

        // Add error message containers if they don't exist
        document.querySelectorAll('input, select, textarea').forEach(function(field) {
            if (!field.parentElement.querySelector('.invalid-feedback') && 
                !field.parentElement.querySelector('.error-message')) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                field.parentElement.appendChild(errorDiv);
            }
        });
    });

    // Export functions for global use
    window.CashPayment = {
        validateRequiredField: validateRequiredField,
        validateEmail: validateEmail,
        validatePhone: validatePhone,
        validateNumeric: validateNumeric,
        validateDate: validateDate,
        validateVehiclePlate: validateVehiclePlate,
        formatCurrency: formatCurrency,
        showLoading: showLoading,
        hideLoading: hideLoading
    };

})();
