document.addEventListener('DOMContentLoaded', function () {
    // Toggle sidebar on mobile
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function (event) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnMenuToggle = menuToggle.contains(event.target);

            if (!isClickInsideSidebar && !isClickOnMenuToggle && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        });
    }

    // messages auto-hide section

    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });

    // Global event listener for delete buttons
    document.addEventListener('click', function (e) {
        if (e.target.closest('.btn-action.delete')) {
            e.preventDefault();
            const button = e.target.closest('.btn-action.delete');
            const offerId = button.getAttribute('data-offer-id');
            const offerName = button.getAttribute('data-offer-name');
            // This relies on deleteOffer being defined globally, likely in common.js or specific page js
            // The original code in base.html checked if deleteOffer function exists
            if (typeof deleteOffer === 'function' && offerId && offerName) {
                deleteOffer(offerId, offerName);
            }
        }
    });
});
