/**
 * Enhanced Navigation Bar JavaScript
 * Based on reusable navbar design with scroll effects, active link highlighting, and mobile menu handling
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        const navbar = document.querySelector('.navbar-enhanced');
        const navLinks = document.querySelectorAll('.navbar-enhanced .navbar-nav .nav-link');
        const navbarToggler = document.querySelector('.navbar-enhanced .navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-enhanced .navbar-collapse');

        if (!navbar) {
            return; // Navbar not found, exit
        }

        // Sticky-on-scroll
        function handleNavbarScroll() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }

        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(handleNavbarScroll, 10);
        });
        handleNavbarScroll();

        // Active link highlighting by URL path
        function updateActiveNavigation() {
            const currentPath = window.location.pathname;
            let bestMatch = null;
            let bestMatchLength = 0;

            navLinks.forEach(link => {
                link.classList.remove('active');
                
                // Skip dropdown toggles and buttons
                if (link.classList.contains('dropdown-toggle') || link.classList.contains('btn')) {
                    return;
                }

                try {
                    const linkUrl = new URL(link.href, window.location.origin);
                    const linkPath = linkUrl.pathname;

                    if (linkPath === currentPath || (linkPath !== '/' && currentPath.startsWith(linkPath))) {
                        if (linkPath.length > bestMatchLength) {
                            bestMatch = link;
                            bestMatchLength = linkPath.length;
                        }
                    } else if (linkPath === '/' && (currentPath === '/' || currentPath === '')) {
                        if (bestMatchLength === 0) {
                            bestMatch = link;
                            bestMatchLength = 1;
                        }
                    }
                } catch (e) {
                    // Invalid URL, skip
                    console.warn('Invalid link URL:', link.href);
                }
            });

            if (bestMatch) {
                bestMatch.classList.add('active');
                bestMatch.style.transition = 'all 0.3s ease';
                
                // Scroll active link into view on mobile
                if (window.innerWidth <= 991 && navbarCollapse && navbarCollapse.classList.contains('show')) {
                    setTimeout(() => {
                        bestMatch.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'nearest', 
                            inline: 'center' 
                        });
                    }, 100);
                }
            }
        }

        updateActiveNavigation();

        // Link interactions
        navLinks.forEach(link => {
            // Skip dropdown toggles
            if (link.classList.contains('dropdown-toggle')) {
                return;
            }

            link.addEventListener('click', function(e) {
                // Don't prevent default for dropdowns or external links
                if (this.classList.contains('dropdown-toggle') || 
                    this.getAttribute('target') === '_blank' ||
                    this.href.startsWith('#')) {
                    return;
                }

                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);

                // Close mobile menu on link click
                if (window.innerWidth <= 991 && navbarCollapse && navbarCollapse.classList.contains('show')) {
                    if (navbarToggler) {
                        navbarToggler.click();
                    }
                }
            });

            link.addEventListener('mouseenter', function() {
                if (!this.classList.contains('active') && !this.classList.contains('btn')) {
                    this.style.transform = 'translateY(-2px)';
                }
            });

            link.addEventListener('mouseleave', function() {
                if (!this.classList.contains('active') && !this.classList.contains('btn')) {
                    this.style.transform = '';
                }
            });
        });

        // Mobile menu handling
        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', function() {
                setTimeout(() => {
                    if (navbarCollapse.classList.contains('show')) {
                        navbarCollapse.style.animation = 'slideInDown 0.3s ease forwards';
                    }
                }, 10);
            });

            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!navbar.contains(e.target) && 
                    navbarCollapse.classList.contains('show')) {
                    if (navbarToggler) {
                        navbarToggler.click();
                    }
                }
            });

            // Close menu on Escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && navbarCollapse.classList.contains('show')) {
                    if (navbarToggler) {
                        navbarToggler.click();
                    }
                }
            });
        }

        // Browser history and optional HTMX hooks
        window.addEventListener('popstate', () => {
            setTimeout(updateActiveNavigation, 100);
        });

        if (typeof htmx !== 'undefined') {
            document.addEventListener('htmx:afterRequest', () => {
                setTimeout(updateActiveNavigation, 100);
            });
            document.addEventListener('htmx:historyRestore', () => {
                setTimeout(updateActiveNavigation, 100);
            });
        }

        // Smooth scroll for hash anchors accounting for fixed navbar
        document.querySelectorAll('.navbar-enhanced a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#' || !href) {
                    return;
                }

                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    const navbarHeight = navbar.offsetHeight || 0;
                    const targetPosition = targetElement.offsetTop - navbarHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });

                    // Close mobile menu
                    if (window.innerWidth <= 991 && navbarCollapse && navbarCollapse.classList.contains('show')) {
                        if (navbarToggler) {
                            navbarToggler.click();
                        }
                    }
                }
            });
        });

        // Optional loading icon animation on nav link click
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                // Skip if external link or hash link
                if (this.hostname !== window.location.hostname || 
                    this.getAttribute('href').startsWith('#') ||
                    this.classList.contains('dropdown-toggle')) {
                    return;
                }

                const originalHTML = this.innerHTML;
                const icon = this.querySelector('i');
                
                if (icon && !icon.classList.contains('fa-spinner')) {
                    const iconClass = icon.className;
                    icon.className = 'fas fa-spinner fa-spin me-1';
                    
                    // Reset after timeout or page navigation
                    setTimeout(() => {
                        if (this.innerHTML === originalHTML || icon.parentElement === this) {
                            this.innerHTML = originalHTML;
                        }
                    }, 2000);
                }
            });
        });

        // Inject small CSS for animations if missing
        if (!document.getElementById('enhanced-navbar-styles')) {
            const style = document.createElement('style');
            style.id = 'enhanced-navbar-styles';
            style.textContent = `
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                @keyframes slideOutUp {
                    from {
                        opacity: 1;
                        transform: translateY(0);
                    }
                    to {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                }
                .spin {
                    animation: spin 1s linear infinite;
                }
            `;
            document.head.appendChild(style);
        }

        // IntersectionObserver for visibility flag (optional styling hook)
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        navbar.classList.add('visible');
                    } else {
                        navbar.classList.remove('visible');
                    }
                });
            }, { threshold: 0.1 });

            observer.observe(navbar);
        }

        // Add padding to body if navbar is fixed
        if (navbar.classList.contains('fixed-top')) {
            const navbarHeight = navbar.offsetHeight;
            document.body.style.paddingTop = navbarHeight + 'px';
            
            // Update on resize
            window.addEventListener('resize', function() {
                const newHeight = navbar.offsetHeight;
                document.body.style.paddingTop = newHeight + 'px';
            });
        }
    });
})();

