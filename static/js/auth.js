document.addEventListener('DOMContentLoaded', function () {
    // Handle both signup and login forms
    const forms = document.querySelectorAll('.auth-form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const btn = this.querySelector('button[type="submit"]');
            if (btn) {
                const btnText = btn.querySelector('.btn-text');
                const btnLoader = btn.querySelector('.btn-loader');

                if (btnText && btnLoader) {
                    btnText.style.display = 'none';
                    btnLoader.style.display = 'flex';
                }
                btn.disabled = true;
            }
        });
    });
});

function handleGoogleSignup() {
    alert('Google login will be implemented with OAuth 2.0');
}

function handleGoogleLogin() {
    alert('Google login will be implemented with OAuth 2.0');
}