/**
 * Bulk Operations JavaScript
 * Handles multi-select and bulk actions for admin console lists
 */

document.addEventListener('DOMContentLoaded', function() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const bulkActionsBar = document.getElementById('bulkActionsBar');
    const selectedCountSpan = document.getElementById('selectedCount');
    const bulkActionSelect = document.getElementById('bulkActionSelect');
    const bulkActionBtn = document.getElementById('bulkActionBtn');
    
    if (!selectAllCheckbox || !bulkActionsBar) {
        return; // Not on a page with bulk operations
    }
    
    // Track selected items
    let selectedItems = new Set();
    
    /**
     * Update the UI based on selection state
     */
    function updateSelectionUI() {
        const count = selectedItems.size;
        
        if (count > 0) {
            bulkActionsBar.style.display = 'block';
            selectedCountSpan.textContent = `${count} sélectionné(s)`;
        } else {
            bulkActionsBar.style.display = 'none';
            bulkActionSelect.value = '';
        }
        
        // Update select all checkbox state
        if (count === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (count === itemCheckboxes.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }
    
    /**
     * Handle select all checkbox
     */
    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;
        
        itemCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            if (isChecked) {
                selectedItems.add(checkbox.value);
            } else {
                selectedItems.delete(checkbox.value);
            }
        });
        
        updateSelectionUI();
    });
    
    /**
     * Handle individual item checkboxes
     */
    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                selectedItems.add(this.value);
            } else {
                selectedItems.delete(this.value);
            }
            updateSelectionUI();
        });
    });
    
    /**
     * Handle bulk action button click
     */
    bulkActionBtn.addEventListener('click', function() {
        const action = bulkActionSelect.value;
        
        if (!action) {
            M.toast({html: 'Veuillez sélectionner une action', classes: 'orange'});
            return;
        }
        
        if (selectedItems.size === 0) {
            M.toast({html: 'Aucun élément sélectionné', classes: 'orange'});
            return;
        }
        
        // Confirmation dialog
        const actionText = {
            'activate': 'activer',
            'deactivate': 'désactiver',
            'delete': 'supprimer'
        }[action] || action;
        
        const confirmMessage = `Êtes-vous sûr de vouloir ${actionText} ${selectedItems.size} élément(s) ?`;
        
        // Use Notifications system if available, otherwise fallback to browser confirm
        if (window.Notifications) {
            Notifications.confirm(
                `${actionText.charAt(0).toUpperCase() + actionText.slice(1)} ${selectedItems.size} élément(s)?`,
                confirmMessage
            ).then((result) => {
                if (!result.isConfirmed) {
                    return;
                }
                proceedWithBulkAction(action, selectedItems);
            });
            return;
        } else {
            if (!confirm(confirmMessage)) {
                return;
            }
        }
        
        // Show progress indicator and perform action
        proceedWithBulkAction(action, Array.from(selectedItems));
    });
    
    /**
     * Proceed with bulk action after confirmation
     */
    function proceedWithBulkAction(action, selectedItems) {
        // Show progress indicator
        bulkActionBtn.disabled = true;
        bulkActionBtn.innerHTML = '<i class="material-icons left">hourglass_empty</i>Traitement...';
        
        // Perform bulk action via AJAX
        performBulkAction(action, selectedItems);
    }
    
    /**
     * Perform bulk action via AJAX
     */
    function performBulkAction(action, items) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         getCookie('csrftoken');
        
        fetch('/administration/api/vehicle-types/bulk-update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                action: action,
                items: items
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                M.toast({html: data.message, classes: 'green'});
                
                // Reload page after short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                M.toast({html: data.message || 'Une erreur est survenue', classes: 'red'});
                resetBulkActionButton();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            M.toast({html: 'Erreur de connexion au serveur', classes: 'red'});
            resetBulkActionButton();
        });
    }
    
    /**
     * Reset bulk action button to initial state
     */
    function resetBulkActionButton() {
        bulkActionBtn.disabled = false;
        bulkActionBtn.innerHTML = '<i class="material-icons left">done_all</i>Appliquer';
    }
    
    /**
     * Get CSRF token from cookies
     */
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
});
