/**
 * QR Code Verification Page JavaScript
 * Handles camera scanning and manual input for QR code verification
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        scannerContainerId: 'qr-reader',
        manualInputId: 'qr-code-input',
        resultContainerId: 'verification-result',
        scanModeCamera: 'camera',
        scanModeManual: 'manual',
        apiEndpoint: window.QR_VERIFICATION_URL || '/app/qr-verification/',
    };

    // State
    let state = {
        currentMode: 'manual', // 'camera' or 'manual'
        scanner: null,
        isScanning: false,
        lastScannedCode: null,
    };

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializePage();
    });

    /**
     * Initialize the page
     */
    function initializePage() {
        setupModeSwitcher();
        setupManualInput();
        setupCameraScanner();
        checkCameraSupport();
    }

    /**
     * Setup mode switcher (Camera/Manual)
     */
    function setupModeSwitcher() {
        const cameraBtn = document.getElementById('mode-camera');
        const manualBtn = document.getElementById('mode-manual');

        if (cameraBtn) {
            cameraBtn.addEventListener('click', function() {
                switchMode(CONFIG.scanModeCamera);
            });
        }

        if (manualBtn) {
            manualBtn.addEventListener('click', function() {
                switchMode(CONFIG.scanModeManual);
            });
        }
    }

    /**
     * Switch between camera and manual input modes
     */
    function switchMode(mode) {
        state.currentMode = mode;

        // Update button states
        document.querySelectorAll('.scanner-mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        const cameraBtn = document.getElementById('mode-camera');
        const manualBtn = document.getElementById('mode-manual');

        if (mode === CONFIG.scanModeCamera) {
            if (cameraBtn) cameraBtn.classList.add('active');
            showCameraScanner();
            hideManualInput();
            // Don't auto-start camera, let user click start button
        } else {
            if (manualBtn) manualBtn.classList.add('active');
            hideCameraScanner();
            showManualInput();
            stopCameraScanning();
        }

        // Hide previous results
        hideResults();
    }

    /**
     * Show camera scanner
     */
    function showCameraScanner() {
        const container = document.getElementById('camera-scanner');
        if (container) {
            container.classList.add('active');
        }
    }

    /**
     * Hide camera scanner
     */
    function hideCameraScanner() {
        const container = document.getElementById('camera-scanner');
        if (container) {
            container.classList.remove('active');
        }
        stopCameraScanning();
    }

    /**
     * Show manual input
     */
    function showManualInput() {
        const container = document.getElementById('manual-input');
        if (container) {
            container.classList.add('active');
        }
    }

    /**
     * Hide manual input
     */
    function hideManualInput() {
        const container = document.getElementById('manual-input');
        if (container) {
            container.classList.remove('active');
        }
    }

    /**
     * Setup manual input handler
     */
    function setupManualInput() {
        const input = document.getElementById(CONFIG.manualInputId);
        const verifyBtn = document.getElementById('verify-btn');
        const form = document.getElementById('qr-verification-form');

        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const code = input ? input.value.trim() : '';
                if (code) {
                    verifyQRCode(code);
                }
            });
        }

        if (verifyBtn) {
            verifyBtn.addEventListener('click', function() {
                const code = input ? input.value.trim() : '';
                if (code) {
                    verifyQRCode(code);
                } else {
                    showError('Veuillez saisir un code QR');
                }
            });
        }

        // Clear results when input changes
        if (input) {
            input.addEventListener('input', function() {
                hideResults();
            });
        }
    }

    /**
     * Setup camera scanner using html5-qrcode
     */
    function setupCameraScanner() {
        // Check if html5-qrcode is loaded
        if (typeof Html5Qrcode === 'undefined') {
            console.warn('Html5Qrcode library not loaded');
            return;
        }

        const scannerContainer = document.getElementById(CONFIG.scannerContainerId);
        if (!scannerContainer) {
            return;
        }

        // Initialize scanner
        state.scanner = new Html5Qrcode(CONFIG.scannerContainerId);
    }

    /**
     * Start camera scanning
     */
    function startCameraScanning() {
        if (!state.scanner || state.isScanning) {
            return;
        }

        const startBtn = document.getElementById('start-camera-btn');
        const stopBtn = document.getElementById('stop-camera-btn');

        // Update button states
        if (startBtn) startBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'block';

        state.isScanning = true;

        // Configuration for camera
        const config = {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0,
            supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
        };

        // Start scanning
        Html5Qrcode.getCameras().then(cameras => {
            if (cameras && cameras.length > 0) {
                const cameraId = cameras[0].id; // Use first available camera
                
                state.scanner.start(
                    cameraId,
                    config,
                    onScanSuccess,
                    onScanError
                ).catch(err => {
                    console.error('Error starting camera:', err);
                    showCameraError(err);
                    stopCameraScanning();
                });
            } else {
                showCameraError('Aucune caméra trouvée');
                stopCameraScanning();
            }
        }).catch(err => {
            console.error('Error getting cameras:', err);
            showCameraError('Erreur d\'accès à la caméra. Vérifiez les permissions.');
            stopCameraScanning();
        });
    }

    /**
     * Stop camera scanning
     */
    function stopCameraScanning() {
        if (!state.scanner || !state.isScanning) {
            return;
        }

        const startBtn = document.getElementById('start-camera-btn');
        const stopBtn = document.getElementById('stop-camera-btn');

        state.scanner.stop().then(() => {
            state.scanner.clear();
            state.isScanning = false;

            // Update button states
            if (startBtn) startBtn.style.display = 'block';
            if (stopBtn) stopBtn.style.display = 'none';
        }).catch(err => {
            console.error('Error stopping camera:', err);
            state.isScanning = false;
            if (startBtn) startBtn.style.display = 'block';
            if (stopBtn) stopBtn.style.display = 'none';
        });
    }

    /**
     * Handle successful QR code scan
     */
    function onScanSuccess(decodedText, decodedResult) {
        // Prevent duplicate scans
        if (state.lastScannedCode === decodedText) {
            return;
        }

        state.lastScannedCode = decodedText;

        // Stop scanning
        stopCameraScanning();

        // Verify the QR code
        verifyQRCode(decodedText);

        // Reset after a delay to allow re-scanning
        setTimeout(() => {
            state.lastScannedCode = null;
        }, 3000);
    }

    /**
     * Handle scan errors (ignore common errors)
     */
    function onScanError(errorMessage) {
        // Ignore common scanning errors
        // These are expected when no QR code is in view
    }

    /**
     * Verify QR code via API
     */
    function verifyQRCode(code) {
        if (!code) {
            showError('Veuillez saisir un code QR');
            return;
        }

        // Show loading
        showLoading();

        // Get CSRF token
        const csrfToken = getCSRFToken();

        // Make AJAX request
        fetch(CONFIG.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken,
            },
            body: `qr_code=${encodeURIComponent(code)}&csrfmiddlewaretoken=${csrfToken}`
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                showSuccess(data);
            } else {
                showError(data.message || 'Code QR invalide');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error verifying QR code:', error);
            showError('Erreur lors de la vérification. Veuillez réessayer.');
        });
    }

    /**
     * Show success result
     */
    function showSuccess(data) {
        const resultContainer = document.getElementById(CONFIG.resultContainerId);
        if (!resultContainer) {
            return;
        }

        const qrData = data.qr_data || {};
        const vehicule = data.vehicule || {};
        const paiement = data.paiement || {};
        const documents = data.documents || {};

        // Build HTML
        let html = `
            <div class="result-card result-success">
                <div class="result-header">
                    <div class="result-icon text-success">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="result-title text-success">QR Code Authentique</div>
                    <p>Ce QR code est valide et authentique</p>
                </div>
        `;

        // QR Code Details
        html += `
            <div class="result-details">
                <div class="detail-section">
                    <div class="detail-section-title">
                        <i class="fas fa-info-circle"></i>
                        Informations du QR Code
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Statut:</span>
                        <span class="detail-value">
                            <span class="status-badge ${data.tax_paid ? 'status-valid' : 'status-unpaid'}">
                                ${data.tax_paid ? '<i class="fas fa-check me-1"></i>Taxe Payée' : '<i class="fas fa-times me-1"></i>Taxe Non Payée'}
                            </span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Date d'expiration:</span>
                        <span class="detail-value">${data.expiration_date || 'N/A'}</span>
                    </div>
                </div>
        `;

        // Vehicle Information
        if (vehicule.plaque_immatriculation) {
            html += `
                <div class="detail-section">
                    <div class="detail-section-title">
                        <i class="fas fa-car"></i>
                        Informations du Véhicule
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Plaque d'immatriculation:</span>
                        <span class="detail-value"><strong>${vehicule.plaque_immatriculation}</strong></span>
                    </div>
            `;

            if (vehicule.vin) {
                html += `
                    <div class="detail-row">
                        <span class="detail-label">VIN:</span>
                        <span class="detail-value">${vehicule.vin}</span>
                    </div>
                `;
            }

            if (vehicule.nom_proprietaire) {
                html += `
                    <div class="detail-row">
                        <span class="detail-label">Propriétaire:</span>
                        <span class="detail-value"><strong>${vehicule.nom_proprietaire}</strong></span>
                    </div>
                `;
            }

            if (vehicule.type_vehicule_display) {
                html += `
                    <div class="detail-row">
                        <span class="detail-label">Type:</span>
                        <span class="detail-value">${vehicule.type_vehicule_display}</span>
                    </div>
                `;
            }

            html += `</div>`;
        }

        // Payment Information
        if (paiement.statut) {
            html += `
                <div class="detail-section">
                    <div class="detail-section-title">
                        <i class="fas fa-credit-card"></i>
                        Informations de Paiement
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Statut:</span>
                        <span class="detail-value">${paiement.statut_display || paiement.statut}</span>
                    </div>
            `;

            if (paiement.montant_paye) {
                html += `
                    <div class="detail-row">
                        <span class="detail-label">Montant payé:</span>
                        <span class="detail-value"><strong>${paiement.montant_paye} Ar</strong></span>
                    </div>
                `;
            }

            if (paiement.date_paiement) {
                const date = new Date(paiement.date_paiement);
                html += `
                    <div class="detail-row">
                        <span class="detail-label">Date de paiement:</span>
                        <span class="detail-value">${date.toLocaleDateString('fr-FR')}</span>
                    </div>
                `;
            }

            html += `</div>`;
        }

        // Documents
        if (documents.assurance || documents.carte_grise) {
            html += `
                <div class="detail-section">
                    <div class="detail-section-title">
                        <i class="fas fa-file-alt"></i>
                        Documents
                    </div>
                    <div class="document-images">
            `;

            if (documents.assurance && documents.assurance.present && documents.assurance.url) {
                html += `
                    <div class="document-image-card">
                        <img src="${documents.assurance.url}" 
                             alt="Assurance" 
                             class="document-image"
                             onclick="window.open('${documents.assurance.url}', '_blank')">
                        <div class="document-image-label">
                            <i class="fas fa-shield-alt me-1"></i>
                            Assurance
                            ${documents.assurance.expiration_date ? `<br><small>Expire: ${documents.assurance.expiration_date}</small>` : ''}
                        </div>
                    </div>
                `;
            }

            if (documents.carte_grise && documents.carte_grise.present && documents.carte_grise.url) {
                html += `
                    <div class="document-image-card">
                        <img src="${documents.carte_grise.url}" 
                             alt="Carte Grise" 
                             class="document-image"
                             onclick="window.open('${documents.carte_grise.url}', '_blank')">
                        <div class="document-image-label">
                            <i class="fas fa-id-card me-1"></i>
                            Carte Grise
                        </div>
                    </div>
                `;
            }

            html += `
                    </div>
                </div>
            `;
        }

        html += `
            </div>
            </div>
        `;

        resultContainer.innerHTML = html;
        resultContainer.classList.add('active');

        // Scroll to results
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Show error message
     */
    function showError(message) {
        const resultContainer = document.getElementById(CONFIG.resultContainerId);
        if (!resultContainer) {
            return;
        }

        const html = `
            <div class="result-card result-error">
                <div class="result-header">
                    <div class="result-icon text-danger">
                        <i class="fas fa-times-circle"></i>
                    </div>
                    <div class="result-title text-danger">QR Code Invalide</div>
                    <p>${message}</p>
                </div>
            </div>
        `;

        resultContainer.innerHTML = html;
        resultContainer.classList.add('active');

        // Scroll to results
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Show loading state
     */
    function showLoading() {
        const loading = document.getElementById('qr-loading');
        if (loading) {
            loading.classList.add('active');
        }
        hideResults();
    }

    /**
     * Hide loading state
     */
    function hideLoading() {
        const loading = document.getElementById('qr-loading');
        if (loading) {
            loading.classList.remove('active');
        }
    }

    /**
     * Hide results
     */
    function hideResults() {
        const resultContainer = document.getElementById(CONFIG.resultContainerId);
        if (resultContainer) {
            resultContainer.classList.remove('active');
        }
    }

    /**
     * Show camera error
     */
    function showCameraError(message) {
        const alert = document.getElementById('camera-permission-alert');
        if (alert) {
            alert.textContent = message;
            alert.classList.add('active');
        }
    }

    /**
     * Check camera support
     */
    function checkCameraSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            // Camera not supported, disable camera mode
            const cameraBtn = document.getElementById('mode-camera');
            if (cameraBtn) {
                cameraBtn.disabled = true;
                cameraBtn.title = 'Camera non supportée par votre navigateur';
            }
        }
    }

    /**
     * Get CSRF token from cookie or meta tag
     */
    function getCSRFToken() {
        // Try to get from cookie
        const name = 'csrftoken';
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

        // Try to get from meta tag
        if (!cookieValue) {
            const metaTag = document.querySelector('meta[name=csrf-token]');
            if (metaTag) {
                cookieValue = metaTag.getAttribute('content');
            }
        }

        // Try to get from form
        if (!cookieValue) {
            const form = document.getElementById('qr-verification-form');
            if (form) {
                const input = form.querySelector('input[name=csrfmiddlewaretoken]');
                if (input) {
                    cookieValue = input.value;
                }
            }
        }

        return cookieValue || '';
    }

    // Expose global functions for button clicks
    window.startCameraScanning = startCameraScanning;
    window.stopCameraScanning = stopCameraScanning;

})();

