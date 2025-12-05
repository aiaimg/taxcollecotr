// Admin Console Main JavaScript
// Handles sidebar toggle, theme switching, and common functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Materialize components
    initMaterializeComponents();
    
    // Setup sidebar toggle
    setupSidebarToggle();
    
    // Setup theme toggle
    setupThemeToggle();
    
    // Setup CSRF token for AJAX requests
    setupCSRFToken();
    
    // Auto-dismiss success messages after 5 seconds
    autoDismissMessages();
});

/**
 * Initialize Materialize CSS components
 */
function initMaterializeComponents() {
    // Initialize dropdowns
    const dropdowns = document.querySelectorAll('.dropdown-trigger');
    M.Dropdown.init(dropdowns, {
        coverTrigger: false,
        constrainWidth: false
    });
    
    // Initialize modals
    const modals = document.querySelectorAll('.modal');
    M.Modal.init(modals);
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('.tooltipped');
    M.Tooltip.init(tooltips);
    
    // Initialize select elements
    const selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);
    
    // Initialize datepickers
    const datepickers = document.querySelectorAll('.datepicker');
    M.Datepicker.init(datepickers, {
        format: 'yyyy-mm-dd',
        autoClose: true
    });
}

/**
 * Setup sidebar toggle for mobile
 */
function setupSidebarToggle() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('adminSidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (window.innerWidth <= 992) {
                if (!sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }
}

/**
 * Setup theme toggle (dark/light mode)
 */
function setupThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            
            // Save preference to localStorage
            const isDarkMode = body.classList.contains('dark-mode');
            localStorage.setItem('adminTheme', isDarkMode ? 'dark' : 'light');
            
            // Optionally save to server
            saveThemePreference(isDarkMode ? 'dark' : 'light');
        });
    }
    
    // Load theme preference from localStorage
    const savedTheme = localStorage.getItem('adminTheme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
    }
}

/**
 * Save theme preference to server
 */
function saveThemePreference(theme) {
    fetch('/administration/api/save-theme/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ theme: theme })
    }).catch(error => {
        console.error('Error saving theme preference:', error);
    });
}

/**
 * Setup CSRF token for AJAX requests
 */
function setupCSRFToken() {
    // Get CSRF token from cookie
    const csrfToken = getCSRFToken();
    
    // Set default headers for fetch requests
    window.fetchWithCSRF = function(url, options = {}) {
        options.headers = options.headers || {};
        options.headers['X-CSRFToken'] = csrfToken;
        return fetch(url, options);
    };
}

/**
 * Get CSRF token from cookie
 */
function getCSRFToken() {
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
    return cookieValue;
}

/**
 * Auto-dismiss success messages after 5 seconds
 */
function autoDismissMessages() {
    const successMessages = document.querySelectorAll('.alert-success');
    successMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
}

/**
 * Show a toast message
 */
function showMessage(message, type = 'info') {
    const colors = {
        success: 'green',
        error: 'red',
        warning: 'orange',
        info: 'blue'
    };
    
    M.toast({
        html: message,
        classes: colors[type] || 'blue',
        displayLength: 4000
    });
}

/**
 * Show loading indicator
 */
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading-spinner"></div>';
        element.disabled = true;
    }
}

/**
 * Hide loading indicator
 */
function hideLoading(element, originalText) {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

/**
 * Confirm action with modal
 */
function confirmAction(message, callback) {
    if (window.Notifications) {
        Notifications.confirm(
            'Confirmer l\'action',
            message
        ).then((result) => {
            if (result.isConfirmed) {
                callback();
            }
        });
    } else {
        // Fallback to browser confirm
        if (confirm(message)) {
            callback();
        }
    }
}

/**
 * Format number with thousand separators
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

/**
 * Format currency (Ariary)
 */
function formatCurrency(amount) {
    return formatNumber(amount) + ' Ar';
}

/**
 * Debounce function for search inputs
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

// Export functions for use in other scripts
window.AdminConsole = {
    showMessage,
    showLoading,
    hideLoading,
    confirmAction,
    formatNumber,
    formatCurrency,
    debounce,
    getCSRFToken
};
