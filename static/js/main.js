// ============================================
// SUBHLABH - Main JavaScript
// Authentication & Form Handling
// ============================================

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Debounce function
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
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Get CSRF token from DOM
 */
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

/**
 * Format time remaining (MM:SS)
 */
function formatTimeRemaining(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ============================================
// OTP HANDLING
// ============================================

class OTPHandler {
    constructor() {
        this.resendDelay = 30;
        this.resendCounter = 0;
    }

    /**
     * Initialize OTP input with auto-focus and formatting
     */
    initOTPInput() {
        const otpInput = document.querySelector('input[name="otp"]');
        if (!otpInput) return;

        otpInput.addEventListener('input', (e) => {
            // Only allow digits
            e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 6);

            // Animate each digit entry
            this.animateOTPEntry(e.target);

            // Auto-submit when 6 digits are entered (optional)
            // if (e.target.value.length === 6) {
            //     e.target.form.submit();
            // }
        });

        // Focus on load
        otpInput.focus();
    }

    /**
     * Animate OTP digit entry
     */
    animateOTPEntry(input) {
        input.style.animation = 'none';
        setTimeout(() => {
            input.style.animation = 'pulse 0.3s ease-in-out';
        }, 10);
    }

    /**
     * Handle resend OTP
     */
    async resendOTP(email, purpose = 'signup') {
        const btn = document.getElementById('resendBtn');
        if (!btn || btn.disabled) return;

        btn.disabled = true;
        this.resendCounter = this.resendDelay;
        this.updateResendTimer();

        try {
            const response = await fetch('/resend-otp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: `email=${encodeURIComponent(email)}&purpose=${encodeURIComponent(purpose)}`
            });

            const data = await response.json();

            if (data.success) {
                showToast('OTP resent successfully!', 'success');
                const otpInput = document.querySelector('input[name="otp"]');
                if (otpInput) {
                    otpInput.value = '';
                    otpInput.focus();
                }
            } else {
                showToast(data.message || 'Failed to resend OTP', 'error');
                btn.disabled = false;
                this.resendCounter = 0;
                this.updateResendTimer();
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Failed to resend OTP', 'error');
            btn.disabled = false;
            this.resendCounter = 0;
            this.updateResendTimer();
        }
    }

    /**
     * Update resend timer display
     */
    updateResendTimer() {
        const btn = document.getElementById('resendBtn');
        const timerSpan = document.getElementById('timer');

        if (!btn || !timerSpan) return;

        if (this.resendCounter > 0) {
            timerSpan.textContent = ` (${this.resendCounter}s)`;
            timerSpan.style.display = 'inline';
            this.resendCounter--;
            setTimeout(() => this.updateResendTimer(), 1000);
        } else {
            btn.disabled = false;
            timerSpan.textContent = '';
            timerSpan.style.display = 'none';
        }
    }

    /**
     * Start initial resend delay
     */
    startInitialDelay() {
        this.resendCounter = 5;
        this.updateResendTimer();
    }
}

// ============================================
// PASSWORD VALIDATION
// ============================================

class PasswordValidator {
    constructor() {
        this.requirements = {
            length: { regex: /.{8,}/, element: 'req-length' },
            uppercase: { regex: /[A-Z]/, element: 'req-uppercase' },
            number: { regex: /[0-9]/, element: 'req-number' }
        };
    }

    /**
     * Validate password against requirements
     */
    validate(password) {
        const results = {};
        for (const [key, req] of Object.entries(this.requirements)) {
            results[key] = req.regex.test(password);
            this.updateRequirement(req.element, results[key]);
        }
        return Object.values(results).every(v => v);
    }

    /**
     * Update requirement indicator
     */
    updateRequirement(elementId, isMet) {
        const element = document.getElementById(elementId);
        if (!element) return;

        if (isMet) {
            element.classList.add('met');
            element.classList.remove('unmet');
        } else {
            element.classList.remove('met');
            element.classList.add('unmet');
        }
    }

    /**
     * Check if passwords match
     */
    checkMatch(password, confirmPassword) {
        const matchDiv = document.getElementById('passwordMatch');
        if (!matchDiv) return;

        if (!confirmPassword) {
            matchDiv.innerHTML = '';
            return;
        }

        if (password === confirmPassword) {
            matchDiv.innerHTML = '<span class="match-success">✓ Passwords match</span>';
            matchDiv.className = 'password-match match';
            return true;
        } else {
            matchDiv.innerHTML = '<span class="match-error">✗ Passwords do not match</span>';
            matchDiv.className = 'password-match mismatch';
            return false;
        }
    }
}

// ============================================
// PASSWORD SHOW/HIDE TOGGLE
// ============================================

class PasswordToggle {
    /**
     * Initialize password toggles using event delegation
     */
    init() {
        // Use event delegation on document to handle current and future toggles
        document.addEventListener('click', (e) => {
            const toggle = e.target.closest('.password-toggle-icon');
            if (toggle) {
                // Prevent any other actions (like form submission if icon is a button)
                e.preventDefault();
                e.stopPropagation();

                const wrapper = toggle.closest('.password-toggle-wrapper');
                if (!wrapper) return;

                const input = wrapper.querySelector('input');
                const icon = toggle.querySelector('i');

                if (!input || !icon) return;

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                    toggle.title = 'Hide password';
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                    toggle.title = 'Show password';
                }
            }
        });
    }
}

// ============================================
// FORM HANDLING
// ============================================

class FormHandler {
    constructor() {
        this.setupEventListeners();
    }

    /**
     * Setup form event listeners
     */
    setupEventListeners() {
        // Prevent double submission
        document.addEventListener('submit', (e) => {
            const form = e.target;
            const submitBtn = form.querySelector('button[type="submit"]');

            if (submitBtn) {
                submitBtn.disabled = true;
                const btnText = submitBtn.querySelector('.btn-text');
                const btnLoader = submitBtn.querySelector('.btn-loader');

                if (btnText && btnLoader) {
                    btnText.style.display = 'none';
                    btnLoader.style.display = 'flex';
                }
            }
        });

        // Password form validation
        const passwordForm = document.getElementById('passwordForm');
        if (passwordForm) {
            this.setupPasswordForm(passwordForm);
        }

        // Set new password form validation
        const setPasswordForm = document.getElementById('setPasswordForm');
        if (setPasswordForm) {
            this.setupPasswordForm(setPasswordForm);
        }
    }

    /**
     * Setup password form validation
     */
    setupPasswordForm(form) {
        const validator = new PasswordValidator();
        const passwordInput = form.querySelector('input[name="password"]');
        const confirmInput = form.querySelector('input[name="confirm_password"]');
        const submitBtn = form.querySelector('button[type="submit"]');

        if (!passwordInput) return;

        passwordInput.addEventListener('input', () => {
            validator.validate(passwordInput.value);
            if (confirmInput) {
                validator.checkMatch(passwordInput.value, confirmInput.value);
            }
        });

        if (confirmInput) {
            confirmInput.addEventListener('input', () => {
                validator.checkMatch(passwordInput.value, confirmInput.value);
            });
        }

        form.addEventListener('submit', (e) => {
            if (!validator.validate(passwordInput.value)) {
                e.preventDefault();
                showToast('Please meet all password requirements', 'error');
                return;
            }

            if (confirmInput && passwordInput.value !== confirmInput.value) {
                e.preventDefault();
                showToast('Passwords do not match', 'error');
                return;
            }
        });

        // Initialize on load
        if (passwordInput.value) {
            validator.validate(passwordInput.value);
        }
    }
}

// ============================================
// EMAIL VALIDATION
// ============================================

class EmailValidator {
    /**
     * Validate email input in real-time
     */
    setupEmailValidation() {
        const emailInputs = document.querySelectorAll('input[type="email"]');

        emailInputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                if (e.target.value && !isValidEmail(e.target.value)) {
                    showToast('Please enter a valid email address', 'warning');
                }
            });

            // Real-time visual feedback
            input.addEventListener('input', (e) => {
                if (e.target.value && isValidEmail(e.target.value)) {
                    e.target.style.borderColor = 'var(--success)';
                } else if (e.target.value) {
                    e.target.style.borderColor = 'var(--error)';
                } else {
                    e.target.style.borderColor = '#e0e0e0';
                }
            });
        });
    }
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    // Initialize form handler
    new FormHandler();

    // Initialize email validation
    const emailValidator = new EmailValidator();
    emailValidator.setupEmailValidation();

    const otpHandler = new OTPHandler();
    otpHandler.initOTPInput();
    otpHandler.startInitialDelay();

    // Initialize password toggle
    const passwordToggle = new PasswordToggle();
    passwordToggle.init();

    // Make OTP handler available globally for resend
    window.resendOTP = function () {
        const email = document.querySelector('.form-subtitle strong')?.textContent || '';
        const purpose = document.querySelector('input[type="hidden"][name="purpose"]')?.value || 'signup';
        otpHandler.resendOTP(email, purpose);
    };

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Add keyboard navigation
    const authForm = document.querySelector('.auth-form');
    if (authForm) {
        const inputs = authForm.querySelectorAll('input, button, [role="button"]');
        inputs.forEach((input, index) => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && input.tagName === 'INPUT') {
                    const nextInput = inputs[index + 1];
                    if (nextInput && nextInput.tagName === 'INPUT') {
                        nextInput.focus();
                    } else if (index === inputs.length - 2) {
                        // Last input, submit form
                        authForm.submit();
                    }
                }
            });
        });
    }

    // Disable submit button after first click
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            const btn = this.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                setTimeout(() => {
                    btn.disabled = false;
                }, 5000); // Re-enable after 5 seconds
            }
        });
    });

    // Add animation to alerts on load
    document.querySelectorAll('.alert').forEach((alert, index) => {
        alert.style.animation = `fadeIn 0.4s ease-in-out ${index * 0.1}s both`;
    });
});

// ============================================
// GLOBAL ERROR HANDLER
// ============================================

window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (event.error instanceof TypeError) {
        console.error('TypeError caught:', event.error.message);
    }
});

// ============================================
// PERFORMANCE OPTIMIZATION
// ============================================

// Lazy load images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img.lazy').forEach(img => imageObserver.observe(img));
}

// ============================================
// ACCESSIBILITY IMPROVEMENTS
// ============================================

// Add focus indicators
document.addEventListener('focusin', (e) => {
    if (e.target.matches('input, button, a')) {
        e.target.style.outline = '2px solid var(--primary)';
        e.target.style.outlineOffset = '2px';
    }
});

document.addEventListener('focusout', (e) => {
    if (e.target.matches('input, button, a')) {
        e.target.style.outline = '';
    }
});

// Add skip to main content link
if (!document.querySelector('a.skip-to-main')) {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-to-main';
    skipLink.textContent = 'Skip to main content';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 0;
        background: var(--primary);
        color: white;
        padding: 8px;
        text-decoration: none;
        z-index: 100;
    `;
    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '0';
    });
    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
    });
    document.body.insertBefore(skipLink, document.body.firstChild);
}

console.log('✓ Subhlabh Authentication System Initialized');
