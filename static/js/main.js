/**
 * Main JavaScript - Maqola Platform
 * UX Enhancements & Interactions
 */

(function() {
    'use strict';

    // ===================================
    // Toast Notification System
    // ===================================
    const Toast = {
        container: null,

        init() {
            if (!this.container) {
                this.container = document.createElement('div');
                this.container.className = 'toast-container';
                document.body.appendChild(this.container);
            }
        },

        show(message, type = 'info', title = '', duration = 5000) {
            this.init();

            const icons = {
                success: 'bi-check-circle-fill',
                error: 'bi-x-circle-fill',
                warning: 'bi-exclamation-triangle-fill',
                info: 'bi-info-circle-fill'
            };

            const titles = {
                success: 'Success',
                error: 'Error',
                warning: 'Warning',
                info: 'Info'
            };

            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.innerHTML = `
                <i class="bi ${icons[type]} toast-icon"></i>
                <div class="toast-content">
                    <div class="toast-title">${title || titles[type]}</div>
                    <p class="toast-message">${message}</p>
                </div>
                <button class="toast-close" aria-label="Close">
                    <i class="bi bi-x"></i>
                </button>
            `;

            this.container.appendChild(toast);

            // Close button
            toast.querySelector('.toast-close').addEventListener('click', () => {
                this.remove(toast);
            });

            // Auto remove
            if (duration > 0) {
                setTimeout(() => {
                    this.remove(toast);
                }, duration);
            }

            return toast;
        },

        remove(toast) {
            toast.classList.add('removing');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        },

        success(message, title = '') {
            return this.show(message, 'success', title);
        },

        error(message, title = '') {
            return this.show(message, 'error', title);
        },

        warning(message, title = '') {
            return this.show(message, 'warning', title);
        },

        info(message, title = '') {
            return this.show(message, 'info', title);
        }
    };

    // Make Toast globally available
    window.Toast = Toast;

    // ===================================
    // Loading Overlay
    // ===================================
    const Loading = {
        overlay: null,

        init() {
            if (!this.overlay) {
                this.overlay = document.createElement('div');
                this.overlay.className = 'loading-overlay';
                this.overlay.innerHTML = '<div class="spinner"></div>';
                document.body.appendChild(this.overlay);
            }
        },

        show() {
            this.init();
            this.overlay.classList.add('active');
        },

        hide() {
            if (this.overlay) {
                this.overlay.classList.remove('active');
            }
        }
    };

    window.Loading = Loading;

    // ===================================
    // Back to Top Button
    // ===================================
    function initBackToTop() {
        const backToTop = document.createElement('button');
        backToTop.className = 'back-to-top';
        backToTop.innerHTML = '<i class="bi bi-arrow-up"></i>';
        backToTop.setAttribute('aria-label', 'Back to top');
        document.body.appendChild(backToTop);

        // Show/hide on scroll
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });

        // Scroll to top on click
        backToTop.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ===================================
    // Form Enhancements
    // ===================================
    function initFormEnhancements() {
        // Add loading state to forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.classList.contains('btn-loading')) {
                    submitBtn.classList.add('btn-loading');
                    submitBtn.disabled = true;
                }
            });
        });

        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        });
    }

    // ===================================
    // Image Lazy Loading
    // ===================================
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');

        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('img-loading');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => {
            img.classList.add('img-loading');
            imageObserver.observe(img);
        });
    }

    // ===================================
    // Confirm Dialogs
    // ===================================
    function initConfirmDialogs() {
        document.querySelectorAll('[data-confirm]').forEach(element => {
            element.addEventListener('click', function(e) {
                const message = this.dataset.confirm;
                if (!confirm(message)) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }

    // ===================================
    // Auto-hide Alerts
    // ===================================
    function initAutoHideAlerts() {
        document.querySelectorAll('.alert[data-auto-hide]').forEach(alert => {
            const duration = parseInt(alert.dataset.autoHide) || 5000;
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, duration);
        });
    }

    // ===================================
    // Copy to Clipboard
    // ===================================
    function initCopyToClipboard() {
        document.querySelectorAll('[data-copy]').forEach(element => {
            element.addEventListener('click', function() {
                const text = this.dataset.copy;
                navigator.clipboard.writeText(text).then(() => {
                    Toast.success('Copied to clipboard!');
                }).catch(() => {
                    Toast.error('Failed to copy');
                });
            });
        });
    }

    // ===================================
    // Smooth Scroll for Anchor Links
    // ===================================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // ===================================
    // Card Hover Effects
    // ===================================
    function initCardEffects() {
        document.querySelectorAll('.card').forEach(card => {
            if (!card.classList.contains('no-hover')) {
                card.classList.add('card-hover-effect');
            }
        });
    }

    // ===================================
    // Convert Django Messages to Toasts
    // ===================================
    function convertDjangoMessages() {
        document.querySelectorAll('.alert').forEach(alert => {
            const message = alert.textContent.trim();
            const closeBtn = alert.querySelector('.btn-close');

            if (closeBtn) {
                closeBtn.remove();
            }

            let type = 'info';
            if (alert.classList.contains('alert-success')) type = 'success';
            else if (alert.classList.contains('alert-danger')) type = 'error';
            else if (alert.classList.contains('alert-warning')) type = 'warning';

            // Remove the alert and show toast instead
            if (!alert.classList.contains('alert-dark')) {
                Toast.show(message, type);
                alert.remove();
            }
        });
    }

    // ===================================
    // Initialize on DOM Ready
    // ===================================
    function init() {
        initBackToTop();
        initFormEnhancements();
        initLazyLoading();
        initConfirmDialogs();
        initAutoHideAlerts();
        initCopyToClipboard();
        initSmoothScroll();
        initCardEffects();
        convertDjangoMessages();

        // Add page transition class
        document.body.classList.add('page-transition');
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ===================================
    // AJAX Form Helper
    // ===================================
    window.submitFormAjax = function(form, successCallback, errorCallback) {
        const formData = new FormData(form);
        const url = form.action || window.location.href;
        const method = form.method || 'POST';

        Loading.show();

        fetch(url, {
            method: method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            Loading.hide();
            if (data.success) {
                if (successCallback) successCallback(data);
                else Toast.success(data.message || 'Success!');
            } else {
                if (errorCallback) errorCallback(data);
                else Toast.error(data.message || 'An error occurred');
            }
        })
        .catch(error => {
            Loading.hide();
            if (errorCallback) errorCallback(error);
            else Toast.error('Network error occurred');
        });
    };

})();
