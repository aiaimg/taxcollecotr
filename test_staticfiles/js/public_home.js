/**
 * Public Home Page JavaScript
 * Tax Collector Platform - Madagascar
 * 
 * This script provides interactive functionality for the public-facing home page,
 * including smooth scrolling, animations, and accessibility enhancements.
 * 
 * Features:
 * - Language switcher with visual feedback
 * - Mobile menu toggle with keyboard support
 * - Smooth scrolling for anchor links
 * - CTA button click tracking (optional analytics)
 * - Accessibility enhancements (skip links, focus management, ARIA)
 * - Lazy loading for images
 * 
 * Graceful Degradation:
 * - All core functionality works without JavaScript
 * - Forms submit normally via standard HTTP
 * - Links navigate directly to their destinations
 * - Language switching uses standard form submission
 * 
 * @requires Bootstrap 5 (for collapse functionality)
 */

(function() {
    'use strict';

    /**
     * Configuration options
     */
    var CONFIG = {
        // Enable/disable CTA click tracking
        enableCTATracking: true,
        // Smooth scroll offset for fixed header
        scrollOffset: 20,
        // Debounce delay for resize events
        debounceDelay: 150,
        // Mobile breakpoint (matches Bootstrap lg)
        mobileBreakpoint: 992
    };

    /**
     * Initialize all functionality when DOM is ready
     */
    document.addEventListener('DOMContentLoaded', function() {
        initSmoothScrolling();
        initMobileMenuToggle();
        initLanguageSwitcher();
        initCTATracking();
        initAccessibilityEnhancements();
        initLazyLoading();
        initGracefulDegradation();
    });

    /**
     * Smooth scrolling for anchor links
     * Provides smooth scroll behavior for internal page links
     * Falls back to default browser behavior if smooth scroll is not supported
     */
    function initSmoothScrolling() {
        var anchorLinks = document.querySelectorAll('a[href^="#"]');
        
        anchorLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                var targetId = this.getAttribute('href');
                
                // Skip if it's just "#" or empty
                if (targetId === '#' || !targetId) {
                    return;
                }
                
                // Try to find the target element
                var targetElement;
                try {
                    targetElement = document.querySelector(targetId);
                } catch (err) {
                    // Invalid selector, let browser handle it
                    return;
                }
                
                if (targetElement) {
                    e.preventDefault();
                    
                    // Calculate offset for fixed header
                    var navbar = document.querySelector('.navbar');
                    var headerHeight = navbar ? navbar.offsetHeight : 0;
                    var targetPosition = targetElement.getBoundingClientRect().top + 
                        window.pageYOffset - headerHeight - CONFIG.scrollOffset;
                    
                    // Check for smooth scroll support
                    if ('scrollBehavior' in document.documentElement.style) {
                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    } else {
                        // Fallback for older browsers
                        window.scrollTo(0, targetPosition);
                    }
                    
                    // Update focus for accessibility
                    targetElement.setAttribute('tabindex', '-1');
                    targetElement.focus();
                    
                    // Update URL hash without jumping
                    if (history.pushState) {
                        history.pushState(null, null, targetId);
                    }
                    
                    // Announce navigation to screen readers
                    announceToScreenReader('Navigated to ' + (targetElement.getAttribute('aria-label') || targetId));
                }
            });
        });
    }

    /**
     * Mobile menu toggle functionality
     * Enhances Bootstrap's collapse with additional UX improvements:
     * - Close on outside click
     * - Close on Escape key
     * - Close on nav link click (mobile)
     * - Trap focus within menu when open
     */
    function initMobileMenuToggle() {
        var navbarToggler = document.querySelector('.navbar-toggler');
        var navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (!navbarToggler || !navbarCollapse) {
            return;
        }
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarCollapse.contains(e.target) && 
                !navbarToggler.contains(e.target) && 
                navbarCollapse.classList.contains('show')) {
                // Use Bootstrap's collapse API if available
                if (typeof bootstrap !== 'undefined' && bootstrap.Collapse) {
                    var bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    } else {
                        navbarToggler.click();
                    }
                } else {
                    navbarToggler.click();
                }
            }
        });
        
        // Close menu when pressing Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navbarCollapse.classList.contains('show')) {
                if (typeof bootstrap !== 'undefined' && bootstrap.Collapse) {
                    var bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    } else {
                        navbarToggler.click();
                    }
                } else {
                    navbarToggler.click();
                }
                navbarToggler.focus();
                announceToScreenReader('Menu closed');
            }
        });
        
        // Close menu when clicking on a nav link (mobile)
        var navLinks = navbarCollapse.querySelectorAll('.nav-link:not(.dropdown-toggle)');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth < CONFIG.mobileBreakpoint && navbarCollapse.classList.contains('show')) {
                    if (typeof bootstrap !== 'undefined' && bootstrap.Collapse) {
                        var bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                        if (bsCollapse) {
                            bsCollapse.hide();
                        } else {
                            navbarToggler.click();
                        }
                    } else {
                        navbarToggler.click();
                    }
                }
            });
        });

        // Update ARIA attributes when menu state changes
        navbarCollapse.addEventListener('shown.bs.collapse', function() {
            navbarToggler.setAttribute('aria-expanded', 'true');
            announceToScreenReader('Navigation menu opened');
        });

        navbarCollapse.addEventListener('hidden.bs.collapse', function() {
            navbarToggler.setAttribute('aria-expanded', 'false');
        });
    }

    /**
     * Language switcher functionality
     * Enhances the language dropdown with:
     * - Visual loading feedback
     * - Keyboard accessibility
     * - Screen reader announcements
     * 
     * Note: The form submits normally without JavaScript (graceful degradation)
     */
    function initLanguageSwitcher() {
        var languageSelect = document.querySelector('.language-switcher select');
        
        if (!languageSelect) {
            return;
        }
        
        // Add visual feedback on language change
        languageSelect.addEventListener('change', function() {
            var languageName = this.options[this.selectedIndex].text;
            
            // Announce language change to screen readers
            announceToScreenReader('Changing language to ' + languageName);
            
            // Show loading indicator
            var form = this.closest('form');
            if (form) {
                // Disable the select to prevent double submission
                this.disabled = true;
                
                // Create and append loading spinner
                var spinner = document.createElement('span');
                spinner.className = 'spinner-border spinner-border-sm ms-2';
                spinner.setAttribute('role', 'status');
                spinner.setAttribute('aria-label', 'Loading...');
                spinner.id = 'language-loading-spinner';
                this.parentNode.appendChild(spinner);
                
                // Add loading class to form
                form.classList.add('loading');
            }
        });
        
        // Keyboard accessibility for language switcher
        languageSelect.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.form.submit();
            }
        });

        // Handle focus for better accessibility
        languageSelect.addEventListener('focus', function() {
            this.parentNode.classList.add('focused');
        });

        languageSelect.addEventListener('blur', function() {
            this.parentNode.classList.remove('focused');
        });
    }

    /**
     * Accessibility enhancements
     * Implements WCAG 2.1 AA compliance features
     */
    function initAccessibilityEnhancements() {
        // Add skip link functionality
        addSkipLink();
        
        // Enhance focus management
        enhanceFocusManagement();
        
        // Add ARIA live region for dynamic content
        addAriaLiveRegion();

        // Enhance reduced motion support
        initReducedMotionSupport();
    }

    /**
     * Add skip link for keyboard navigation
     * Allows keyboard users to skip repetitive navigation
     */
    function addSkipLink() {
        // Check if skip link already exists
        if (document.querySelector('.skip-link')) {
            return;
        }
        
        var skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link visually-hidden-focusable';
        skipLink.textContent = 'Skip to main content';
        skipLink.setAttribute('aria-label', 'Skip to main content');
        
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Add id to main content if not present
        var mainContent = document.querySelector('main, .main-content, [role="main"], .hero-section');
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
        }

        // Handle skip link click
        skipLink.addEventListener('click', function(e) {
            var target = document.getElementById('main-content');
            if (target) {
                e.preventDefault();
                target.setAttribute('tabindex', '-1');
                target.focus();
                announceToScreenReader('Skipped to main content');
            }
        });
    }

    /**
     * Enhance focus management for better keyboard navigation
     * Distinguishes between mouse and keyboard focus
     */
    function enhanceFocusManagement() {
        // Add visible focus styles
        var interactiveElements = document.querySelectorAll(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        interactiveElements.forEach(function(element) {
            element.addEventListener('focus', function() {
                if (!document.body.classList.contains('using-mouse')) {
                    this.classList.add('keyboard-focus');
                }
            });
            
            element.addEventListener('blur', function() {
                this.classList.remove('keyboard-focus');
            });
        });
        
        // Detect mouse vs keyboard navigation
        document.addEventListener('mousedown', function() {
            document.body.classList.add('using-mouse');
        });
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                document.body.classList.remove('using-mouse');
            }
        });

        // Handle touch events for mobile
        document.addEventListener('touchstart', function() {
            document.body.classList.add('using-touch');
        });
    }

    /**
     * Add ARIA live region for dynamic content announcements
     * Used to announce changes to screen reader users
     */
    function addAriaLiveRegion() {
        // Check if live region already exists
        if (document.getElementById('aria-live-region')) {
            return;
        }
        
        var liveRegion = document.createElement('div');
        liveRegion.id = 'aria-live-region';
        liveRegion.className = 'visually-hidden';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.setAttribute('role', 'status');
        
        document.body.appendChild(liveRegion);
    }

    /**
     * Support for users who prefer reduced motion
     * Respects prefers-reduced-motion media query
     */
    function initReducedMotionSupport() {
        var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        
        function handleReducedMotion(e) {
            if (e.matches) {
                document.body.classList.add('reduced-motion');
            } else {
                document.body.classList.remove('reduced-motion');
            }
        }

        // Initial check
        handleReducedMotion(prefersReducedMotion);

        // Listen for changes
        if (prefersReducedMotion.addEventListener) {
            prefersReducedMotion.addEventListener('change', handleReducedMotion);
        } else if (prefersReducedMotion.addListener) {
            // Fallback for older browsers
            prefersReducedMotion.addListener(handleReducedMotion);
        }
    }

    /**
     * Announce message to screen readers
     * @param {string} message - Message to announce
     * @param {string} priority - 'polite' or 'assertive' (default: 'polite')
     */
    function announceToScreenReader(message, priority) {
        var liveRegion = document.getElementById('aria-live-region');
        if (liveRegion) {
            // Set priority if specified
            if (priority === 'assertive') {
                liveRegion.setAttribute('aria-live', 'assertive');
            } else {
                liveRegion.setAttribute('aria-live', 'polite');
            }

            // Clear first to ensure announcement
            liveRegion.textContent = '';
            
            // Use setTimeout to ensure the clear is processed
            setTimeout(function() {
                liveRegion.textContent = message;
            }, 50);
            
            // Clear after announcement
            setTimeout(function() {
                liveRegion.textContent = '';
            }, 3000);
        }
    }

    /**
     * Initialize CTA button click tracking
     * Tracks clicks on primary and secondary CTA buttons for analytics
     * This is optional and gracefully degrades if analytics is not available
     */
    function initCTATracking() {
        if (!CONFIG.enableCTATracking) {
            return;
        }

        // Select all CTA buttons
        var ctaButtons = document.querySelectorAll(
            '.btn-hero-primary, .btn-hero-secondary, .btn-cta-primary, .btn-cta-secondary, .feature-link'
        );

        ctaButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                var buttonText = this.textContent.trim();
                var buttonHref = this.getAttribute('href') || '';
                var buttonType = getCTAType(this);
                
                // Track the click event
                trackCTAClick({
                    type: buttonType,
                    text: buttonText,
                    href: buttonHref,
                    location: getCTALocation(this)
                });
            });
        });
    }

    /**
     * Determine the CTA button type based on its classes
     * @param {HTMLElement} button - The button element
     * @returns {string} The button type
     */
    function getCTAType(button) {
        if (button.classList.contains('btn-hero-primary')) {
            return 'hero_primary';
        } else if (button.classList.contains('btn-hero-secondary')) {
            return 'hero_secondary';
        } else if (button.classList.contains('btn-cta-primary')) {
            return 'cta_primary';
        } else if (button.classList.contains('btn-cta-secondary')) {
            return 'cta_secondary';
        } else if (button.classList.contains('feature-link')) {
            return 'feature_link';
        }
        return 'unknown';
    }

    /**
     * Determine the location of the CTA on the page
     * @param {HTMLElement} button - The button element
     * @returns {string} The section location
     */
    function getCTALocation(button) {
        var section = button.closest('section');
        if (section) {
            if (section.classList.contains('hero-section')) {
                return 'hero';
            } else if (section.classList.contains('features-section')) {
                return 'features';
            } else if (section.classList.contains('cta-section')) {
                return 'cta';
            }
        }
        return 'unknown';
    }

    /**
     * Track CTA click event
     * Sends data to analytics if available, otherwise logs to console in development
     * @param {Object} data - Click event data
     */
    function trackCTAClick(data) {
        // Google Analytics 4 (gtag)
        if (typeof gtag === 'function') {
            gtag('event', 'cta_click', {
                'event_category': 'engagement',
                'event_label': data.text,
                'cta_type': data.type,
                'cta_location': data.location,
                'destination_url': data.href
            });
            return;
        }

        // Google Analytics Universal (ga)
        if (typeof ga === 'function') {
            ga('send', 'event', 'CTA', 'click', data.text, {
                'dimension1': data.type,
                'dimension2': data.location
            });
            return;
        }

        // Matomo/Piwik
        if (typeof _paq !== 'undefined') {
            _paq.push(['trackEvent', 'CTA', 'click', data.text]);
            return;
        }

        // Development logging (only in non-production)
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1') {
            console.log('[CTA Tracking]', data);
        }
    }

    /**
     * Initialize graceful degradation enhancements
     * Adds classes and attributes to indicate JavaScript is available
     */
    function initGracefulDegradation() {
        // Add js-enabled class to body
        document.body.classList.add('js-enabled');
        document.body.classList.remove('no-js');

        // Enable enhanced features that require JavaScript
        var enhancedElements = document.querySelectorAll('[data-js-enhanced]');
        enhancedElements.forEach(function(element) {
            element.classList.add('js-enhanced');
        });

        // Update noscript fallback visibility
        var noscriptFallbacks = document.querySelectorAll('.noscript-fallback');
        noscriptFallbacks.forEach(function(element) {
            element.style.display = 'none';
        });
    }

    /**
     * Initialize lazy loading for images
     */
    function initLazyLoading() {
        // Check for native lazy loading support
        if ('loading' in HTMLImageElement.prototype) {
            var images = document.querySelectorAll('img[data-src]');
            images.forEach(function(img) {
                img.src = img.dataset.src;
                img.loading = 'lazy';
            });
        } else {
            // Fallback for browsers without native lazy loading
            initIntersectionObserverLazyLoad();
        }
    }

    /**
     * Intersection Observer based lazy loading fallback
     */
    function initIntersectionObserverLazyLoad() {
        var lazyImages = document.querySelectorAll('img[data-src]');
        
        if (lazyImages.length === 0) {
            return;
        }

        // Check for IntersectionObserver support
        if (!('IntersectionObserver' in window)) {
            // Fallback: load all images immediately
            lazyImages.forEach(function(img) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
            return;
        }
        
        var imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });
        
        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    /**
     * Utility: Debounce function for performance optimization
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    function debounce(func, wait) {
        var timeout;
        return function executedFunction() {
            var context = this;
            var args = arguments;
            var later = function() {
                timeout = null;
                func.apply(context, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Utility: Throttle function for performance optimization
     * @param {Function} func - Function to throttle
     * @param {number} limit - Time limit in milliseconds
     * @returns {Function} Throttled function
     */
    function throttle(func, limit) {
        var inThrottle;
        return function() {
            var context = this;
            var args = arguments;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(function() {
                    inThrottle = false;
                }, limit);
            }
        };
    }

    // Expose utility functions globally if needed
    window.PublicHome = {
        announceToScreenReader: announceToScreenReader,
        debounce: debounce,
        throttle: throttle,
        trackCTAClick: trackCTAClick,
        config: CONFIG
    };

})();

/**
 * Graceful Degradation Notes:
 * ==========================
 * 
 * This script is designed to enhance the user experience but is not required
 * for core functionality. Without JavaScript:
 * 
 * 1. Language Switcher: Works via standard form submission to Django's set_language view
 * 2. Mobile Menu: Bootstrap's collapse works with data attributes (requires Bootstrap JS)
 * 3. Navigation Links: All links work as standard anchor tags
 * 4. CTA Buttons: Navigate directly to their href destinations
 * 5. Forms: Submit normally via HTTP POST
 * 
 * The page is fully functional without JavaScript, with JavaScript providing
 * enhanced UX features like smooth scrolling, loading indicators, and analytics.
 */
