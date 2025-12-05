/**
 * Professional Notification System for Tax Collector Platform
 * Uses SweetAlert2 for modals and Toastify for toast notifications
 */

const Notifications = {
    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {object} options - Additional Toastify options
     */
    toast: function(message, type = 'info', options = {}) {
        const defaults = {
            text: message,
            duration: 3000,
            close: true,
            gravity: "top",
            position: "right",
            stopOnFocus: true,
            className: `toast-${type}`,
            style: this.getToastStyle(type),
            onClick: function() {}
        };

        const config = { ...defaults, ...options };
        Toastify(config).showToast();
    },

    /**
     * Get toast style based on type
     */
    getToastStyle: function(type) {
        const styles = {
            success: {
                background: "linear-gradient(135deg, #0ab39c 0%, #16a085 100%)",
            },
            error: {
                background: "linear-gradient(135deg, #f06548 0%, #e74c3c 100%)",
            },
            warning: {
                background: "linear-gradient(135deg, #f7b84b 0%, #f39c12 100%)",
            },
            info: {
                background: "linear-gradient(135deg, #299cdb 0%, #3498db 100%)",
            }
        };
        return styles[type] || styles.info;
    },

    /**
     * Show success toast
     */
    success: function(message, options = {}) {
        this.toast(message, 'success', options);
    },

    /**
     * Show error toast
     */
    error: function(message, options = {}) {
        this.toast(message, 'error', { duration: 5000, ...options });
    },

    /**
     * Show warning toast
     */
    warning: function(message, options = {}) {
        this.toast(message, 'warning', { duration: 4000, ...options });
    },

    /**
     * Show info toast
     */
    info: function(message, options = {}) {
        this.toast(message, 'info', options);
    },

    /**
     * Show SweetAlert2 modal
     */
    alert: function(options = {}) {
        const defaults = {
            confirmButtonClass: 'btn btn-primary w-xs me-2 mt-2',
            cancelButtonClass: 'btn btn-danger w-xs mt-2',
            buttonsStyling: false,
            showCloseButton: true,
            customClass: {
                confirmButton: 'btn btn-primary w-xs me-2 mt-2',
                cancelButton: 'btn btn-danger w-xs mt-2'
            }
        };

        return Swal.fire({ ...defaults, ...options });
    },

    /**
     * Show success alert
     */
    alertSuccess: function(title, text = '', options = {}) {
        return this.alert({
            icon: 'success',
            title: title,
            text: text,
            confirmButtonText: 'OK',
            ...options
        });
    },

    /**
     * Show error alert
     */
    alertError: function(title, text = '', options = {}) {
        return this.alert({
            icon: 'error',
            title: title,
            text: text,
            confirmButtonText: 'OK',
            ...options
        });
    },

    /**
     * Show warning alert
     */
    alertWarning: function(title, text = '', options = {}) {
        return this.alert({
            icon: 'warning',
            title: title,
            text: text,
            confirmButtonText: 'OK',
            ...options
        });
    },

    /**
     * Show info alert
     */
    alertInfo: function(title, text = '', options = {}) {
        return this.alert({
            icon: 'info',
            title: title,
            text: text,
            confirmButtonText: 'OK',
            ...options
        });
    },

    /**
     * Show confirmation dialog
     */
    confirm: function(title, text = '', options = {}) {
        return this.alert({
            icon: 'question',
            title: title,
            text: text,
            showCancelButton: true,
            confirmButtonText: 'Oui',
            cancelButtonText: 'Non',
            ...options
        });
    },

    /**
     * Show delete confirmation
     */
    confirmDelete: function(title = 'Êtes-vous sûr?', text = 'Cette action est irréversible.', options = {}) {
        return this.alert({
            icon: 'warning',
            title: title,
            text: text,
            showCancelButton: true,
            confirmButtonText: 'Oui, supprimer',
            cancelButtonText: 'Annuler',
            confirmButtonClass: 'btn btn-danger w-xs me-2 mt-2',
            customClass: {
                confirmButton: 'btn btn-danger w-xs me-2 mt-2',
                cancelButton: 'btn btn-secondary w-xs mt-2'
            },
            ...options
        });
    },

    /**
     * Show loading alert
     */
    loading: function(title = 'Chargement...', text = 'Veuillez patienter') {
        return Swal.fire({
            title: title,
            text: text,
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
    },

    /**
     * Close any open SweetAlert
     */
    close: function() {
        Swal.close();
    },

    /**
     * Show input prompt
     */
    prompt: function(title, inputType = 'text', options = {}) {
        return this.alert({
            title: title,
            input: inputType,
            showCancelButton: true,
            confirmButtonText: 'Valider',
            cancelButtonText: 'Annuler',
            inputValidator: (value) => {
                if (!value) {
                    return 'Ce champ est requis!';
                }
            },
            ...options
        });
    },

    /**
     * Show timer alert (auto-close)
     */
    timerAlert: function(title, text = '', timer = 2000, icon = 'success') {
        return Swal.fire({
            icon: icon,
            title: title,
            text: text,
            timer: timer,
            timerProgressBar: true,
            showConfirmButton: false
        });
    },

    /**
     * Process Django messages from template
     */
    processDjangoMessages: function() {
        const messageContainer = document.getElementById('django-messages');
        if (messageContainer) {
            const messages = JSON.parse(messageContainer.textContent || '[]');
            messages.forEach(msg => {
                const type = msg.tags.includes('error') ? 'error' : 
                           msg.tags.includes('warning') ? 'warning' : 
                           msg.tags.includes('success') ? 'success' : 'info';
                this.toast(msg.message, type);
            });
        }
    }
};

// Auto-process Django messages on page load
document.addEventListener('DOMContentLoaded', function() {
    Notifications.processDjangoMessages();
});

// Make it globally available
window.Notifications = Notifications;
