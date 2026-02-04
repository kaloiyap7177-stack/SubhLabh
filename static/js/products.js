// Product-specific JavaScript functions

// Delete product functionality
function deleteProduct(productId, productName) {
    document.getElementById('productName').textContent = productName;
    document.getElementById('deleteForm').action = '/products/' + productId + '/delete/';
    document.getElementById('deleteModal').style.display = 'flex';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

// Product type toggle
function toggleProductFields() {
    const productType = document.getElementById('product_type');
    if (!productType) return;
    
    const productTypeValue = productType.value;
    const stockFields = document.querySelector('.stock-fields');
    const serviceFields = document.querySelector('.service-fields');
    
    if (productTypeValue === 'product') {
        if (stockFields) stockFields.style.display = 'grid';
        if (serviceFields) serviceFields.style.display = 'none';
        
        const stockQuantity = document.getElementById('stock_quantity');
        const unit = document.getElementById('unit');
        if (stockQuantity) stockQuantity.required = true;
        if (unit) unit.required = true;
    } else {
        if (stockFields) stockFields.style.display = 'none';
        if (serviceFields) serviceFields.style.display = 'block';
        
        const stockQuantity = document.getElementById('stock_quantity');
        const unit = document.getElementById('unit');
        if (stockQuantity) {
            stockQuantity.required = false;
            stockQuantity.value = '0';
        }
        if (unit) {
            unit.required = false;
            unit.value = '';
        }
    }
}

// Product search functionality
function setupProductSearch() {
    const searchInput = document.getElementById('productSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', debounce(function() {
        const searchTerm = this.value.toLowerCase();
        const productCards = document.querySelectorAll('.product-card');
        
        productCards.forEach(card => {
            const cardText = card.textContent.toLowerCase();
            if (cardText.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }, 300));
}

// Product filtering
function setupProductFilter() {
    const categoryFilter = document.getElementById('categoryFilter');
    if (!categoryFilter) return;
    
    categoryFilter.addEventListener('change', function() {
        const selectedCategory = this.value;
        const productCards = document.querySelectorAll('.product-card');
        
        productCards.forEach(card => {
            if (selectedCategory === 'all') {
                card.style.display = 'block';
            } else {
                const categoryTag = card.querySelector('.product-category');
                if (categoryTag && categoryTag.textContent.toLowerCase().includes(selectedCategory.toLowerCase())) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            }
        });
    });
}

// Show import modal
function showImportModal() {
    document.getElementById('importModal').style.display = 'flex';
}

// Close import modal
function closeImportModal() {
    document.getElementById('importModal').style.display = 'none';
}

// Export products
function exportProducts() {
    window.location.href = '/products/export/';
}

// Initialize product page
domReady(function() {
    setupProductSearch();
    setupProductFilter();
    
    // Initialize product type toggle if on form page
    const productTypeSelect = document.getElementById('product_type');
    if (productTypeSelect) {
        toggleProductFields();
        productTypeSelect.addEventListener('change', toggleProductFields);
    }
    
    // Close modals on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
    
    // Product type selection
    const typeOptions = document.querySelectorAll('.type-option');
    typeOptions.forEach(option => {
        option.addEventListener('click', function() {
            typeOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            const selectedType = this.dataset.type;
            const typeInput = document.getElementById('product_type');
            if (typeInput) {
                typeInput.value = selectedType;
                toggleProductFields();
            }
        });
    });
});

// Validate product form
function validateProductForm(form) {
    let isValid = true;
    const nameField = form.querySelector('input[name="name"]');
    const priceField = form.querySelector('input[name="selling_price"]');
    
    // Clear previous errors
    form.querySelectorAll('.error-message').forEach(el => el.remove());
    
    if (!nameField.value.trim()) {
        showError(nameField, 'Product name is required');
        isValid = false;
    }
    
    if (priceField && parseFloat(priceField.value) <= 0) {
        showError(priceField, 'Selling price must be greater than 0');
        isValid = false;
    }
    
    return isValid;
}