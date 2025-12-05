/**
 * Topbar functionality fixes
 * Ensures fullscreen, theme switcher, and notifications work properly
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Fullscreen toggle
    const fullscreenBtn = document.querySelector('[data-toggle="fullscreen"]');
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (!document.fullscreenElement && !document.mozFullScreenElement && 
                !document.webkitFullscreenElement && !document.msFullscreenElement) {
                // Enter fullscreen
                if (document.documentElement.requestFullscreen) {
                    document.documentElement.requestFullscreen();
                } else if (document.documentElement.msRequestFullscreen) {
                    document.documentElement.msRequestFullscreen();
                } else if (document.documentElement.mozRequestFullScreen) {
                    document.documentElement.mozRequestFullScreen();
                } else if (document.documentElement.webkitRequestFullscreen) {
                    document.documentElement.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
                }
                document.body.classList.add('fullscreen-enable');
            } else {
                // Exit fullscreen
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                } else if (document.mozCancelFullScreen) {
                    document.mozCancelFullScreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                }
                document.body.classList.remove('fullscreen-enable');
            }
        });
    }
    
    // Listen for fullscreen changes
    document.addEventListener('fullscreenchange', exitHandler);
    document.addEventListener('webkitfullscreenchange', exitHandler);
    document.addEventListener('mozfullscreenchange', exitHandler);
    document.addEventListener('MSFullscreenChange', exitHandler);
    
    function exitHandler() {
        if (!document.fullscreenElement && !document.webkitIsFullScreen && 
            !document.mozFullScreen && !document.msFullscreenElement) {
            document.body.classList.remove('fullscreen-enable');
        }
    }
    
    // Theme switcher (light/dark mode)
    const themeSwitcher = document.querySelector('.light-dark-mode');
    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', function(e) {
            e.preventDefault();
            
            const htmlElement = document.documentElement;
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            
            if (currentTheme === 'dark') {
                htmlElement.setAttribute('data-bs-theme', 'light');
                sessionStorage.setItem('data-bs-theme', 'light');
                // Update icon
                const icon = this.querySelector('i');
                if (icon) {
                    icon.classList.remove('bx-sun');
                    icon.classList.add('bx-moon');
                }
            } else {
                htmlElement.setAttribute('data-bs-theme', 'dark');
                sessionStorage.setItem('data-bs-theme', 'dark');
                // Update icon
                const icon = this.querySelector('i');
                if (icon) {
                    icon.classList.remove('bx-moon');
                    icon.classList.add('bx-sun');
                }
            }
            
            // Trigger resize event for charts and other components
            window.dispatchEvent(new Event('resize'));
        });
        
        // Set initial icon based on current theme
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const icon = themeSwitcher.querySelector('i');
        if (icon && currentTheme === 'dark') {
            icon.classList.remove('bx-moon');
            icon.classList.add('bx-sun');
        }
    }
    
    // Notification dropdown functionality
    const notificationDropdown = document.getElementById('page-header-notifications-dropdown');
    if (notificationDropdown) {
        // Mark notifications as read when dropdown is opened
        notificationDropdown.addEventListener('click', function() {
            // You can add AJAX call here to mark notifications as read
            console.log('Notification dropdown clicked');
        });
        
        // Handle notification item clicks
        const notificationItems = document.querySelectorAll('.notification-item');
        notificationItems.forEach(function(item) {
            item.addEventListener('click', function(e) {
                // Don't close dropdown when clicking checkbox
                if (!e.target.classList.contains('form-check-input')) {
                    // Handle notification click
                    console.log('Notification item clicked');
                }
            });
        });
        
        // Handle notification checkboxes
        const notificationChecks = document.querySelectorAll('.notification-check input');
        notificationChecks.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                const checkedCount = document.querySelectorAll('.notification-check input:checked').length;
                const actionsDiv = document.getElementById('notification-actions');
                const selectContent = document.getElementById('select-content');
                
                if (actionsDiv) {
                    actionsDiv.style.display = checkedCount > 0 ? 'block' : 'none';
                }
                
                if (selectContent) {
                    selectContent.textContent = checkedCount;
                }
                
                // Toggle active class on notification item
                const notificationItem = this.closest('.notification-item');
                if (notificationItem) {
                    notificationItem.classList.toggle('active', this.checked);
                }
            });
        });
    }
    
    // Vehicle quick access button
    const vehicleBtn = document.querySelector('[href*="vehicle"]');
    if (vehicleBtn) {
        vehicleBtn.addEventListener('click', function(e) {
            console.log('Vehicle button clicked');
        });
    }
    
    console.log('Topbar functionality initialized');
});
