document.addEventListener('DOMContentLoaded', function () {
    // Password validation
    const passwordInput = document.querySelector('input[name="new_password1"]');
    const confirmInput = document.querySelector('input[name="new_password2"]');
    const matchDiv = document.getElementById('passwordMatch');

    // Event listeners
    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            validatePassword(this.value);
            checkPasswordMatch();
        });

        // Initialize on load if value exists
        if (passwordInput.value) {
            validatePassword(passwordInput.value);
        }
    }

    if (confirmInput) {
        confirmInput.addEventListener('input', checkPasswordMatch);
    }

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
