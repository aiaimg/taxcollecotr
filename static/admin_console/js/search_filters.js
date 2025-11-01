/**
 * Search and Filter JavaScript
 * Handles debounced search and filter functionality for admin console
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search');
    const filterForm = document.getElementById('filterForm');
    const filterSelects = filterForm?.querySelectorAll('select');
    
    if (!filterForm) {
        return; // Not on a page with filters
    }
    
    // Initialize Materialize selects
    if (filterSelects) {
        M.FormSelect.init(filterSelects);
    }
    
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
     * Handle search input with debouncing
     */
    if (searchInput) {
        const debouncedSearch = debounce(function() {
            // Auto-submit form after user stops typing
            filterForm.submit();
        }, 800); // Wait 800ms after user stops typing
        
        searchInput.addEventListener('input', function() {
            // Show loading indicator
            const label = this.nextElementSibling;
            if (label && this.value.length > 0) {
                label.textContent = 'Recherche en cours...';
            }
            
            debouncedSearch();
        });
        
        // Clear search button
        const clearSearchBtn = document.createElement('i');
        clearSearchBtn.className = 'material-icons prefix clickable';
        clearSearchBtn.textContent = 'clear';
        clearSearchBtn.style.cursor = 'pointer';
        clearSearchBtn.style.right = '10px';
        clearSearchBtn.style.left = 'auto';
        clearSearchBtn.title = 'Effacer la recherche';
        
        if (searchInput.value) {
            searchInput.parentElement.appendChild(clearSearchBtn);
        }
        
        clearSearchBtn.addEventListener('click', function() {
            searchInput.value = '';
            filterForm.submit();
        });
        
        searchInput.addEventListener('input', function() {
            if (this.value) {
                if (!searchInput.parentElement.contains(clearSearchBtn)) {
                    searchInput.parentElement.appendChild(clearSearchBtn);
                }
            } else {
                if (searchInput.parentElement.contains(clearSearchBtn)) {
                    clearSearchBtn.remove();
                }
            }
        });
    }
    
    /**
     * Handle filter select changes
     */
    if (filterSelects) {
        filterSelects.forEach(select => {
            select.addEventListener('change', function() {
                // Show loading toast
                M.toast({html: 'Application des filtres...', classes: 'blue'});
                
                // Submit form
                filterForm.submit();
            });
        });
    }
    
    /**
     * Preserve scroll position on page reload
     */
    if (sessionStorage.getItem('scrollPosition')) {
        window.scrollTo(0, parseInt(sessionStorage.getItem('scrollPosition')));
        sessionStorage.removeItem('scrollPosition');
    }
    
    // Save scroll position before form submit
    filterForm.addEventListener('submit', function() {
        sessionStorage.setItem('scrollPosition', window.scrollY);
    });
    
    /**
     * Handle URL parameters for filter state
     */
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        const results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }
    
    /**
     * Update URL without page reload
     */
    function updateUrlParameter(key, value) {
        const url = new URL(window.location);
        if (value) {
            url.searchParams.set(key, value);
        } else {
            url.searchParams.delete(key);
        }
        window.history.replaceState({}, '', url);
    }
    
    /**
     * Active filter indicator
     */
    function updateActiveFiltersIndicator() {
        const activeFilters = [];
        
        if (searchInput && searchInput.value) {
            activeFilters.push('Recherche');
        }
        
        if (filterSelects) {
            filterSelects.forEach(select => {
                if (select.value) {
                    const label = select.parentElement.querySelector('label');
                    if (label) {
                        activeFilters.push(label.textContent);
                    }
                }
            });
        }
        
        // Display active filters count
        const filterTitle = document.querySelector('.card-title');
        if (filterTitle && activeFilters.length > 0) {
            const badge = document.createElement('span');
            badge.className = 'new badge blue';
            badge.setAttribute('data-badge-caption', 'filtre(s) actif(s)');
            badge.textContent = activeFilters.length;
            
            // Remove existing badge if any
            const existingBadge = filterTitle.querySelector('.badge');
            if (existingBadge) {
                existingBadge.remove();
            }
            
            filterTitle.appendChild(badge);
        }
    }
    
    updateActiveFiltersIndicator();
    
    /**
     * Keyboard shortcuts
     */
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape' && searchInput && document.activeElement === searchInput) {
            searchInput.value = '';
            searchInput.blur();
        }
    });
    
    /**
     * Export functionality with current filters
     */
    const exportButtons = document.querySelectorAll('[href*="export"]');
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            M.toast({html: 'Préparation de l\'export...', classes: 'blue'});
        });
    });
});
