// Contraventions Module JavaScript

(function() {
    'use strict';

    // Global contraventions object
    window.Contraventions = {
        config: window.contraventions || {},
        
        // Initialize the module
        init: function() {
            this.bindEvents();
            this.initializeComponents();
        },
        
        // Bind event listeners
        bindEvents: function() {
            // Search functionality
            this.bindSearchEvents();
            
            // Form validation
            this.bindFormEvents();
            
            // Payment methods
            this.bindPaymentEvents();
            
            // Photo management
            this.bindPhotoEvents();
            
            // Status updates
            this.bindStatusEvents();
        },
        
        // Initialize components
        initializeComponents: function() {
            this.initializeTooltips();
            this.initializeDatePickers();
            this.initializeSelect2();
        },
        
        // Search functionality
        bindSearchEvents: function() {
            const self = this;
            
            // Vehicle search
            const vehicleSearch = document.getElementById('vehicleSearch');
            if (vehicleSearch) {
                let vehicleSearchTimeout;
                vehicleSearch.addEventListener('input', function() {
                    clearTimeout(vehicleSearchTimeout);
                    vehicleSearchTimeout = setTimeout(() => {
                        self.searchVehicles(this.value);
                    }, 500);
                });
            }
            
            // Conducteur search
            const conducteurSearch = document.getElementById('conducteurSearch');
            if (conducteurSearch) {
                let conducteurSearchTimeout;
                conducteurSearch.addEventListener('input', function() {
                    clearTimeout(conducteurSearchTimeout);
                    conducteurSearchTimeout = setTimeout(() => {
                        self.searchConducteurs(this.value);
                    }, 500);
                });
            }
        },
        
        // Search vehicles
        searchVehicles: function(query) {
            if (query.length < 2) {
                this.clearSearchResults('vehicleResults');
                return;
            }
            
            this.showLoading('vehicleResults');
            
            fetch(`${this.config.ajaxUrl}?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.config.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.displayVehicleResults(data.vehicles);
                } else {
                    this.showSearchError('vehicleResults', data.message || 'Erreur lors de la recherche');
                }
            })
            .catch(error => {
                console.error('Vehicle search error:', error);
                this.showSearchError('vehicleResults', 'Erreur de connexion');
            });
        },
        
        // Search conducteurs
        searchConducteurs: function(query) {
            if (query.length < 2) {
                this.clearSearchResults('conducteurResults');
                return;
            }
            
            this.showLoading('conducteurResults');
            
            fetch(`${this.config.ajaxUrl.replace('search-vehicle', 'search-conducteur')}?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.config.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.displayConducteurResults(data.conducteurs);
                } else {
                    this.showSearchError('conducteurResults', data.message || 'Erreur lors de la recherche');
                }
            })
            .catch(error => {
                console.error('Conducteur search error:', error);
                this.showSearchError('conducteurResults', 'Erreur de connexion');
            });
        },
        
        // Display vehicle search results
        displayVehicleResults: function(vehicles) {
            const resultsContainer = document.getElementById('vehicleResults');
            if (!resultsContainer) return;
            
            if (vehicles.length === 0) {
                resultsContainer.innerHTML = '<div class="alert alert-info">Aucun véhicule trouvé</div>';
                return;
            }
            
            let html = '<div class="list-group">';
            vehicles.forEach(vehicle => {
                html += `
                    <a href="#" class="list-group-item list-group-item-action vehicle-item" data-id="${vehicle.id}">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${vehicle.numero_plaque}</h6>
                            <small>${vehicle.marque} ${vehicle.modele}</small>
                        </div>
                        <p class="mb-1">Châssis: ${vehicle.numero_chassis}</p>
                        <small>Propriétaire: ${vehicle.proprietaire_nom}</small>
                    </a>
                `;
            });
            html += '</div>';
            
            resultsContainer.innerHTML = html;
            
            // Add click handlers
            resultsContainer.querySelectorAll('.vehicle-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.selectVehicle(item.dataset.id);
                });
            });
        },
        
        // Display conducteur search results
        displayConducteurResults: function(conducteurs) {
            const resultsContainer = document.getElementById('conducteurResults');
            if (!resultsContainer) return;
            
            if (conducteurs.length === 0) {
                resultsContainer.innerHTML = '<div class="alert alert-info">Aucun conducteur trouvé</div>';
                return;
            }
            
            let html = '<div class="list-group">';
            conducteurs.forEach(conducteur => {
                html += `
                    <a href="#" class="list-group-item list-group-item-action conducteur-item" data-id="${conducteur.id}">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${conducteur.nom} ${conducteur.prenom}</h6>
                            <small>${conducteur.numero_permis}</small>
                        </div>
                        <p class="mb-1">Téléphone: ${conducteur.telephone}</p>
                        <small>Adresse: ${conducteur.adresse}</small>
                    </a>
                `;
            });
            html += '</div>';
            
            resultsContainer.innerHTML = html;
            
            // Add click handlers
            resultsContainer.querySelectorAll('.conducteur-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.selectConducteur(item.dataset.id);
                });
            });
        },
        
        // Select vehicle
        selectVehicle: function(vehicleId) {
            fetch(`${this.config.ajaxUrl}?id=${vehicleId}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.config.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const vehicle = data.vehicle;
                    document.getElementById('id_vehicule').value = vehicle.id;
                    
                    document.getElementById('vehicleDetails').innerHTML = `
                        <strong>${vehicle.numero_plaque}</strong><br>
                        ${vehicle.marque} ${vehicle.modele}<br>
                        Propriétaire: ${vehicle.proprietaire_nom}
                    `;
                    
                    document.getElementById('selectedVehicle').classList.remove('d-none');
                    this.clearSearchResults('vehicleResults');
                    document.getElementById('vehicleSearch').value = '';
                    
                    // Check for récidive
                    this.checkRecidive();
                }
            });
        },
        
        // Select conducteur
        selectConducteur: function(conducteurId) {
            fetch(`${this.config.ajaxUrl.replace('search-vehicle', 'search-conducteur')}?id=${conducteurId}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.config.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const conducteur = data.conducteur;
                    document.getElementById('id_conducteur').value = conducteur.id;
                    
                    document.getElementById('conducteurDetails').innerHTML = `
                        <strong>${conducteur.nom} ${conducteur.prenom}</strong><br>
                        Permis: ${conducteur.numero_permis}<br>
                        Téléphone: ${conducteur.telephone}
                    `;
                    
                    document.getElementById('selectedConducteur').classList.remove('d-none');
                    this.clearSearchResults('conducteurResults');
                    document.getElementById('conducteurSearch').value = '';
                    
                    // Check for récidive
                    this.checkRecidive();
                }
            });
        },
        
        // Check for récidive
        checkRecidive: function() {
            const vehicleId = document.getElementById('id_vehicule').value;
            const conducteurId = document.getElementById('id_conducteur').value;
            const typeId = document.getElementById('id_type_infraction').value;
            
            if (!vehicleId && !conducteurId) return;
            
            const params = new URLSearchParams();
            if (vehicleId) params.append('vehicule_id', vehicleId);
            if (conducteurId) params.append('conducteur_id', conducteurId);
            if (typeId) params.append('type_infraction_id', typeId);
            
            fetch(`${this.config.ajaxUrl.replace('search-vehicle', 'check-recidive')}?${params}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.config.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.has_recidive) {
                    const recidiveInfo = document.getElementById('recidiveInfo');
                    const recidiveDetails = document.getElementById('recidiveDetails');
                    
                    recidiveDetails.innerHTML = `
                        <strong>${data.message}</strong><br>
                        Nombre de récidives: ${data.recidive_count}<br>
                        Majoration: ${data.majoration} Ar
                    `;
                    
                    recidiveInfo.classList.remove('d-none');
                    
                    // Update total amount
                    const montantAmende = document.getElementById('montantAmende');
                    if (montantAmende.value) {
                        const baseAmount = parseFloat(montantAmende.value);
                        const totalAmount = baseAmount + data.majoration;
                        montantAmende.value = totalAmount;
                    }
                } else {
                    document.getElementById('recidiveInfo').classList.add('d-none');
                }
            });
        },
        
        // Form events
        bindFormEvents: function() {
            // Form validation
            const forms = document.querySelectorAll('.needs-validation');
            forms.forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!form.checkValidity()) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                    form.classList.add('was-validated');
                });
            });
            
            // Type infraction change
            const typeInfractionSelect = document.getElementById('id_type_infraction');
            if (typeInfractionSelect) {
                typeInfractionSelect.addEventListener('change', () => {
                    this.updateAmendeDetails();
                });
            }
        },
        
        // Update amende details
        updateAmendeDetails: function() {
            const typeId = document.getElementById('id_type_infraction').value;
            if (!typeId) {
                document.getElementById('montantAmende').value = '';
                document.getElementById('amendeDetails').innerHTML = '';
                return;
            }
            
            fetch(`${this.config.ajaxUrl.replace('search-vehicle', 'get-infraction-details')}?type_id=${typeId}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.config.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('montantAmende').value = data.montant;
                    document.getElementById('amendeDetails').innerHTML = `
                        Montant de base: ${data.montant_base} Ar<br>
                        Montant variable: ${data.montant_variable ? 'Oui' : 'Non'}<br>
                        Fourrière obligatoire: ${data.fourriere_obligatoire ? 'Oui' : 'Non'}
                    `;
                    
                    this.checkRecidive();
                }
            });
        },
        
        // Payment events
        bindPaymentEvents: function() {
            const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
            paymentMethods.forEach(method => {
                method.addEventListener('change', () => {
                    this.showPaymentDetails(method.value);
                });
            });
        },
        
        // Show payment details
        showPaymentDetails: function(method) {
            const details = document.querySelectorAll('.payment-method-details');
            details.forEach(detail => detail.classList.add('d-none'));
            
            const selectedDetail = document.getElementById(method + 'Details');
            if (selectedDetail) {
                selectedDetail.classList.remove('d-none');
            }
        },
        
        // Photo events
        bindPhotoEvents: function() {
            // Photo upload
            const photoInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
            photoInputs.forEach(input => {
                input.addEventListener('change', (e) => {
                    this.handlePhotoUpload(e.target);
                });
            });
            
            // Photo delete buttons
            const deleteButtons = document.querySelectorAll('.delete-photo-btn');
            deleteButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.deletePhoto(btn.dataset.photoId);
                });
            });
        },
        
        // Handle photo upload
        handlePhotoUpload: function(input) {
            const files = input.files;
            if (files.length === 0) return;
            
            const previewContainer = document.getElementById('photoPreview');
            if (!previewContainer) return;
            
            previewContainer.innerHTML = '';
            
            Array.from(files).forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'img-thumbnail me-2 mb-2';
                        img.style.maxWidth = '150px';
                        img.style.maxHeight = '150px';
                        img.style.objectFit = 'cover';
                        
                        previewContainer.appendChild(img);
                    };
                    reader.readAsDataURL(file);
                }
            });
        },
        
        // Delete photo
        deletePhoto: function(photoId) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cette photo ?')) {
                return;
            }
            
            fetch(`/contraventions/photos/${photoId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.config.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const photoElement = document.querySelector(`[data-photo-id="${photoId}"]`);
                    if (photoElement) {
                        photoElement.remove();
                    }
                } else {
                    alert('Erreur lors de la suppression de la photo');
                }
            });
        },
        
        // Status events
        bindStatusEvents: function() {
            // Status update buttons
            const statusButtons = document.querySelectorAll('.update-status-btn');
            statusButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.updateStatus(btn.dataset.contraventionId, btn.dataset.newStatus);
                });
            });
        },
        
        // Update status
        updateStatus: function(contraventionId, newStatus) {
            if (!confirm(`Êtes-vous sûr de vouloir changer le statut de cette contravention ?`)) {
                return;
            }
            
            fetch(`/contraventions/ajax/update-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.config.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    contravention_id: contraventionId,
                    status: newStatus
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Erreur lors de la mise à jour du statut');
                }
            });
        },
        
        // Utility functions
        showLoading: function(elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Chargement...</span></div></div>';
            }
        },
        
        clearSearchResults: function(elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = '';
            }
        },
        
        showSearchError: function(elementId, message) {
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = `<div class="alert alert-danger">${message}</div>`;
            }
        },
        
        // Initialize tooltips
        initializeTooltips: function() {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        },
        
        // Initialize date pickers
        initializeDatePickers: function() {
            const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
            dateInputs.forEach(input => {
                // Set current date/time as default if empty
                if (!input.value) {
                    const now = new Date();
                    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
                    input.value = now.toISOString().slice(0, 16);
                }
            });
        },
        
        // Initialize Select2 (if available)
        initializeSelect2: function() {
            if (typeof $ !== 'undefined' && $.fn.select2) {
                $('select').select2({
                    theme: 'bootstrap-5',
                    width: '100%'
                });
            }
        }
    };
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        Contraventions.init();
    });
    
    // Export for global access
    window.Contraventions = Contraventions;
    
})();