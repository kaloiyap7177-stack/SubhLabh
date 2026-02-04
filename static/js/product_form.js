document.addEventListener('DOMContentLoaded', function () {
    // Set initial state based on product type
    toggleProductFields();
});

function toggleProductFields() {
    const productType = document.getElementById('product_type').value;
    const productFields = document.getElementById('productFields');
    const serviceFields = document.getElementById('serviceFields');

    if (productType === 'product') {
        productFields.style.display = 'block';
        serviceFields.style.display = 'none';
        // Make product fields required
        document.getElementById('unit').required = true;
        document.getElementById('stock_quantity').required = true;
    } else {
        productFields.style.display = 'none';
        serviceFields.style.display = 'block';
        // Remove required from product fields
        document.getElementById('unit').required = false;
        document.getElementById('stock_quantity').required = false;
        // Clear product fields
        document.getElementById('unit').value = '';
        document.getElementById('stock_quantity').value = '0';
    }
}
