const OTP_RESEND_DELAY = 30; // seconds
let resendCounter = 0;

// Auto-focus and format OTP input
document.addEventListener('DOMContentLoaded', function () {
    const otpInput = document.querySelector('input[name="otp"]');
    if (otpInput) {
        otpInput.addEventListener('input', function (e) {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 6);
            if (this.value.length === 6) {
                // Auto-submit form when 6 digits are entered
                // document.getElementById('otpForm').submit();
            }
        });
        otpInput.focus();
    }

    // Start timer on page load
    const startDelay = 5; // 5 second initial delay before resend is available
    resendCounter = startDelay;
    updateResendTimer();
});

function resendOTP() {
    const config = window.otpConfig || {};
    const email = config.email;
    const purpose = config.purpose || 'signup';
    const btn = document.getElementById('resendBtn');

    // Disable button and start countdown
    btn.disabled = true;
    resendCounter = OTP_RESEND_DELAY;
    updateResendTimer();

    fetch(config.resendUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
        },
        body: `email=${encodeURIComponent(email)}&purpose=${encodeURIComponent(purpose)}`
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', data.message);
                // Clear previous OTP input
                const otpInput = document.querySelector('input[name="otp"]');
                if (otpInput) {
                    otpInput.value = '';
                    otpInput.focus();
                }
            } else {
                showAlert('error', data.message);
                btn.disabled = false;
                resendCounter = 0;
                updateResendTimer();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Failed to resend OTP. Please try again.');
            btn.disabled = false;
            resendCounter = 0;
            updateResendTimer();
        });
}

function updateResendTimer() {
    const btn = document.getElementById('resendBtn');
    const timerSpan = document.getElementById('timer');

    if (resendCounter > 0) {
        timerSpan.textContent = ` (${resendCounter}s)`;
        timerSpan.style.display = 'inline';
        resendCounter--;
        setTimeout(updateResendTimer, 1000);
    } else {
        btn.disabled = false;
        timerSpan.textContent = '';
        timerSpan.style.display = 'none';
    }
}

function showAlert(type, message) {
    const container = document.querySelector('.messages-container') || createMessagesContainer();
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.innerHTML = `
        <span class="alert-icon">${type.charAt(0).toUpperCase()}</span>
        <span class="alert-text">${message}</span>
        <button type="button" class="alert-close" onclick="this.parentElement.style.display='none';">&times;</button>
    `;
    container.insertBefore(alertDiv, container.firstChild);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    const authForm = document.querySelector('.auth-form');
    if (authForm) {
        authForm.parentNode.insertBefore(container, authForm);
    }
    return container;
}
