const passwordInput = document.querySelector('input[name="password"]');
const confirmInput = document.querySelector('input[name="confirm_password"]');
const matchDiv = document.getElementById('passwordMatch');
const submitBtn = document.getElementById('submitBtn');

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
    if (isMet) {
        element.classList.add('met');
        element.classList.remove('unmet');
    } else {
        element.classList.remove('met');
        element.classList.add('unmet');
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

passwordInput.addEventListener('input', function () {
    validatePassword(this.value);
    checkPasswordMatch();
});

confirmInput.addEventListener('input', checkPasswordMatch);

document.getElementById('passwordForm').addEventListener('submit', function (e) {
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

    const btn = submitBtn;
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');

    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    btn.disabled = true;
});

// Initialize on load
window.addEventListener('load', function () {
    if (passwordInput.value) {
        validatePassword(passwordInput.value);
    }
});
