// Global variables
let isEditing = false;
let originalProfilePicture = null;

// Tab navigation
function showTab(tabName) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.style.display = 'none';
    });

    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show the selected tab pane
    document.getElementById(tabName + '-tab').style.display = 'block';

    // Add active class to the corresponding tab button
    const tabButton = document.querySelector(`.tab-button[onclick="showTab('${tabName}')"]`);
    if (tabButton) {
        tabButton.classList.add('active');
    }
}

// Preview selected image
function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const container = document.getElementById('profilePictureContainer');

            // Remove existing image or placeholder
            container.innerHTML = '';

            // Create new image element
            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = 'Profile Picture';
            img.id = 'profileImage';
            container.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
}

// Initialize the form properly when the page loads
document.addEventListener('DOMContentLoaded', function () {
    // Show the first tab by default
    showTab('details');
});
