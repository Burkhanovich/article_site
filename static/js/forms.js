/**
 * Form Validation & Enhancement
 */

(function() {
    'use strict';

    // Real-time form validation
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');

        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();

                    // Show first error
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                        Toast.error('Please fill in all required fields correctly');
                    }
                }
                form.classList.add('was-validated');
            }, false);

            // Real-time validation on input
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    if (this.checkValidity()) {
                        this.classList.remove('is-invalid');
                        this.classList.add('is-valid');
                    } else {
                        this.classList.remove('is-valid');
                        this.classList.add('is-invalid');
                    }
                });
            });
        });
    }

    // Character counter for textareas
    function initCharacterCounter() {
        document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
            const maxLength = textarea.getAttribute('maxlength');
            const counter = document.createElement('small');
            counter.className = 'form-text text-muted char-counter';
            textarea.parentNode.appendChild(counter);

            function updateCounter() {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${remaining} characters remaining`;

                if (remaining < 50) {
                    counter.classList.add('text-warning');
                } else {
                    counter.classList.remove('text-warning');
                }
            }

            textarea.addEventListener('input', updateCounter);
            updateCounter();
        });
    }

    // Password strength indicator
    function initPasswordStrength() {
        document.querySelectorAll('input[type="password"]').forEach(input => {
            if (input.name.includes('password') && !input.name.includes('confirm')) {
                const indicator = document.createElement('div');
                indicator.className = 'password-strength mt-2';
                indicator.innerHTML = `
                    <div class="progress" style="height: 5px;">
                        <div class="progress-bar" role="progressbar"></div>
                    </div>
                    <small class="form-text"></small>
                `;
                input.parentNode.appendChild(indicator);

                input.addEventListener('input', function() {
                    const strength = calculatePasswordStrength(this.value);
                    const progressBar = indicator.querySelector('.progress-bar');
                    const text = indicator.querySelector('.form-text');

                    progressBar.style.width = strength.percent + '%';
                    progressBar.className = 'progress-bar ' + strength.class;
                    text.textContent = strength.text;
                    text.className = 'form-text ' + strength.textClass;
                });
            }
        });
    }

    function calculatePasswordStrength(password) {
        let strength = 0;

        if (password.length >= 8) strength += 25;
        if (password.length >= 12) strength += 25;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
        if (/\d/.test(password)) strength += 15;
        if (/[^a-zA-Z0-9]/.test(password)) strength += 10;

        if (strength < 40) {
            return { percent: strength, class: 'bg-danger', text: 'Weak', textClass: 'text-danger' };
        } else if (strength < 70) {
            return { percent: strength, class: 'bg-warning', text: 'Medium', textClass: 'text-warning' };
        } else {
            return { percent: strength, class: 'bg-success', text: 'Strong', textClass: 'text-success' };
        }
    }

    // File input preview
    function initFilePreview() {
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', function() {
                const file = this.files[0];
                if (!file) return;

                // Show file info
                const info = document.createElement('div');
                info.className = 'alert alert-info mt-2 d-flex align-items-center';
                info.innerHTML = `
                    <i class="bi bi-file-earmark me-2"></i>
                    <div>
                        <strong>${file.name}</strong><br>
                        <small>${(file.size / 1024 / 1024).toFixed(2)} MB</small>
                    </div>
                `;

                // Remove previous info
                const prevInfo = this.parentNode.querySelector('.alert');
                if (prevInfo) prevInfo.remove();

                this.parentNode.appendChild(info);

                // Image preview
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const preview = document.createElement('img');
                        preview.src = e.target.result;
                        preview.className = 'img-thumbnail mt-2';
                        preview.style.maxWidth = '200px';
                        info.appendChild(preview);
                    };
                    reader.readAsDataURL(file);
                }
            });
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initFormValidation();
            initCharacterCounter();
            initPasswordStrength();
            initFilePreview();
        });
    } else {
        initFormValidation();
        initCharacterCounter();
        initPasswordStrength();
        initFilePreview();
    }

})();
