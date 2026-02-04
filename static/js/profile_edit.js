// Preview selected image
document.getElementById('profilePictureInput').addEventListener('change', function (event) {
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
});

// Remove profile picture
function removeProfilePicture() {
    const container = document.getElementById('profilePictureContainer');
    container.innerHTML = '<div class="profile-placeholder">👤</div>';
    document.getElementById('profilePictureInput').value = '';
}

// Form validation
document.getElementById('profileEditForm').addEventListener('submit', function (e) {
    const phone = document.getElementById('phone').value.trim();
    const shopName = document.getElementById('shopName').value.trim();

    if (!phone) {
        alert('Mobile number is required!');
        e.preventDefault();
        return false;
    }

    if (!shopName) {
        alert('Shop name is required!');
        e.preventDefault();
        return false;
    }

    return true;
});
