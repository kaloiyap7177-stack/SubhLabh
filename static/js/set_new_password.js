document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.querySelector('input[name="password"]');
    const confirmInput = document.querySelector('input[name="confirm_password"]');
    const matchDiv = document.getElementById('passwordMatch');
    const submitBtn = document.getElementById('submitBtn');

    if (passwordInput && confirmInput) {
        passwordInput.addEventListener('input', function () {
            validatePassword(this.value);
            checkPasswordMatch();
        });

        confirmInput.addEventListener('input', checkPasswordMatch);

        // Initialize on load
        if (passwordInput.value) {
            validatePassword(passwordInput.value);
        }
    }

    const form = document.getElementById('setPasswordForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            // Validate before submission
            if (!validatePassword(passwordInput.value)) {
                e.preventDefault();
                alert('Please meet all password requirements.');
                return;
            }

            if (passwordInput.value !== confirmInput.value) {
                e.preventDefault();
                alert('Passwords do not match.');
                return;
            }

            // Loader handling is done by auth.js generic handler if class is auth-form
            // But we can keep specific logic here if auth.js isn't loaded or to be safe
            // However, auth.js logic will also trigger.
        });
    }

    function checkPasswordMatch() {
        if (!confirmInput.value) {
            matchDiv.innerHTML = '';
            return;
        }

        if (passwordInput.value === confirmInput.value) {
            matchDiv.innerHTML = '<span class="match-success">✓ Passwords match</span>';
            matchDiv.className = 'password-match match';
        } else {
            matchDiv.innerHTML = '<span class="match-error">✗ Passwords do not match</span>';
            matchDiv.className = 'password-match mismatch';
        }
    }
});

// Password validation requirements
function validatePassword(password) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        number: /[0-9]/.test(password)
    };

    updateRequirement('req-length', requirements.length);
    updateRequirement('req-uppercase', requirements.uppercase);
    updateRequirement('req-number', requirements.number);

    return requirements.length && requirements.uppercase && requirements.number;
}

function updateRequirement(elementId, isMet) {
    const element = document.getElementById(elementId);
    if (element) {
        if (isMet) {
            element.classList.add('met');
            element.classList.remove('unmet');
        } else {
            element.classList.remove('met');
            element.classList.add('unmet');
        }
    }
}
