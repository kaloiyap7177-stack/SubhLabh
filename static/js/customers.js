// Customer-specific JavaScript functions

// Delete customer functionality
function deleteCustomer(customerId, customerName) {
    document.getElementById('customerName').textContent = customerName;
    document.getElementById('deleteForm').action = '/customers/' + customerId + '/delete/';
    document.getElementById('deleteModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

// Search functionality
function setupCustomerSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase();
            const customerRows = document.querySelectorAll('.customers-table tbody tr');
            
            customerRows.forEach(row => {
                const rowText = row.textContent.toLowerCase();
                if (rowText.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }, 300));
    }
}

// Filter functionality
function setupCustomerFilter() {
    const filterSelect = document.getElementById('filterSelect');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const filterValue = this.value;
            const customerRows = document.querySelectorAll('.customers-table tbody tr');
            
            customerRows.forEach(row => {
                if (filterValue === 'all') {
                    row.style.display = '';
                } else {
                    const hasCredit = row.querySelector('.credit-badge.has-credit');
                    if (filterValue === 'with-credit' && hasCredit) {
                        row.style.display = '';
                    } else if (filterValue === 'without-credit' && !hasCredit) {
                        row.style.display = '';
                    } else if (filterValue !== 'with-credit' && filterValue !== 'without-credit') {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        });
    }
}

// Initialize customer page
domReady(function() {
    setupCustomerSearch();
    setupCustomerFilter();
    
    // Close modals on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
});

// Export customer data
function exportCustomers() {
    window.location.href = '/customers/export/';
}

// Import customer modal
function showImportModal() {
    document.getElementById('importModal').style.display = 'flex';
}

function closeImportModal() {
    document.getElementById('importModal').style.display = 'none';
}

// Validate customer form
function validateCustomerForm(form) {
    let isValid = true;
    const nameField = form.querySelector('input[name="name"]');
    const phoneField = form.querySelector('input[name="phone"]');
    
    // Clear previous errors
    form.querySelectorAll('.error-message').forEach(el => el.remove());
    
    if (!nameField.value.trim()) {
        showError(nameField, 'Name is required');
        isValid = false;
    }
    
    if (phoneField && phoneField.value && !validatePhone(phoneField.value)) {
        showError(phoneField, 'Please enter a valid phone number');
        isValid = false;
    }
    
    return isValid;
}

function showError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = 'color: #F44336; font-size: 12px; margin-top: 5px;';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function validatePhone(phone) {
    const phoneRegex = /^[0-9]{10,15}$/;
    return phoneRegex.test(phone.replace(/[^0-9]/g, ''));
}