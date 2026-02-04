// Offer-specific JavaScript functions

// Delete offer functionality
function deleteOffer(offerId, offerName) {
    document.getElementById('offerName').textContent = offerName;
    document.getElementById('deleteForm').action = '/offers/' + offerId + '/delete/';
    document.getElementById('deleteModal').style.display = 'flex';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

// Offer type toggle for form
function toggleOfferFields() {
    const offerTypeSelect = document.getElementById('offer_type');
    if (!offerTypeSelect) return;
    
    const type = offerTypeSelect.value;
    const valueFields = document.getElementById('value-fields');
    const bogoFields = document.getElementById('bogo-fields');
    const discountLabel = document.getElementById('discount-label');
    const discountHelp = document.getElementById('discount-help');

    if (type === 'bogo') {
        if (valueFields) valueFields.style.display = 'none';
        if (bogoFields) bogoFields.style.display = 'block';
    } else {
        if (valueFields) valueFields.style.display = 'block';
        if (bogoFields) bogoFields.style.display = 'none';

        if (type === 'percentage') {
            if (discountLabel) discountLabel.textContent = 'Discount Percentage (%) *';
            if (discountHelp) discountHelp.textContent = 'Enter percentage (0-100)';
        } else {
            if (discountLabel) discountLabel.textContent = 'Discount Amount (₹) *';
            if (discountHelp) discountHelp.textContent = 'Enter flat amount in ₹';
        }
    }
}

// Initialize offer form
function initOfferForm() {
    const offerTypeSelect = document.getElementById('offer_type');
    if (offerTypeSelect) {
        // Set up change event
        offerTypeSelect.addEventListener('change', toggleOfferFields);
        
        // Initialize on page load
        toggleOfferFields();
    }
}

// Validate offer form
function validateOfferForm(form) {
    let isValid = true;
    const nameField = form.querySelector('input[name="name"]');
    const typeField = form.querySelector('select[name="offer_type"]');
    const discountField = document.getElementById('discount_value');
    
    // Clear previous errors
    form.querySelectorAll('.error-message').forEach(el => el.remove());
    
    if (!nameField.value.trim()) {
        showError(nameField, 'Offer name is required');
        isValid = false;
    }
    
    if (!typeField.value) {
        showError(typeField, 'Offer type is required');
        isValid = false;
    }
    
    if (discountField && typeField.value !== 'bogo') {
        const discountValue = parseFloat(discountField.value);
        if (isNaN(discountValue) || discountValue <= 0) {
            showError(discountField, 'Discount value must be greater than 0');
            isValid = false;
        }
        
        // Additional validation based on type
        if (typeField.value === 'percentage' && discountValue > 100) {
            showError(discountField, 'Percentage discount cannot be greater than 100%');
            isValid = false;
        }
    }
    
    // BOGO specific validation
    if (typeField.value === 'bogo') {
        const buyField = form.querySelector('input[name="buy_quantity"]');
        const getField = form.querySelector('input[name="get_quantity"]');
        
        if (buyField && (!buyField.value || parseInt(buyField.value) <= 0)) {
            showError(buyField, 'Buy quantity is required for BOGO offers');
            isValid = false;
        }
        
        if (getField && (!getField.value || parseInt(getField.value) <= 0)) {
            showError(getField, 'Get quantity is required for BOGO offers');
            isValid = false;
        }
    }
    
    return isValid;
}

// Offer search functionality
function setupOfferSearch() {
    const searchInput = document.getElementById('offerSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', debounce(function() {
        const searchTerm = this.value.toLowerCase();
        const offerCards = document.querySelectorAll('.offer-card');
        
        offerCards.forEach(card => {
            const cardText = card.textContent.toLowerCase();
            if (cardText.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }, 300));
}

// Initialize offer page
domReady(function() {
    initOfferForm();
    setupOfferSearch();
    
    // Close modals on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
});