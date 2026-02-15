// Search on Enter key
document.getElementById('searchInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        applyFilters();
    }
});

// Download sales data for a specific period
function downloadForPeriod(months) {
    // Calculate date range
    const today = new Date();
    const startDate = new Date();
    startDate.setMonth(today.getMonth() - months);

    // Format dates as YYYY-MM-DD
    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Set the date inputs
    document.getElementById('dateFrom').value = formatDate(startDate);
    document.getElementById('dateTo').value = formatDate(today);

    // Trigger download
    downloadSalesData();
}

// Download sales data
function downloadSalesData() {
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    const payment = document.getElementById('paymentFilter').value;
    const search = document.getElementById('searchInput').value;

    // Build URL with parameters
    const params = new URLSearchParams();
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    if (payment) params.set('payment_method', payment);
    if (search) params.set('search', search);
    params.set('format', 'csv');

    // Note: The salesDownloadUrl should be set by the template
    window.location.href = salesDownloadUrl + '?' + params.toString();
}

// Apply filters
function applyFilters() {
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    const payment = document.getElementById('paymentFilter').value;
    const search = document.getElementById('searchInput').value;

    // Build URL with parameters
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    if (payment) params.set('payment_method', payment);

    // Note: The salesHistoryUrl should be set by the template
    window.location.href = salesHistoryUrl + '?' + params.toString();
}

// Reset filters
function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    document.getElementById('paymentFilter').value = '';

    // Note: The salesHistoryUrl should be set by the template
    window.location.href = salesHistoryUrl;
}

// Set view (table or cards)
function setView(viewType) {
    const tableView = document.getElementById('tableView');
    const cardsView = document.getElementById('cardsView');
    const tableBtn = document.querySelector('.view-btn[onclick="setView(\'table\')"]');
    const cardsBtn = document.querySelector('.view-btn[onclick="setView(\'cards\')"]');

    if (viewType === 'table') {
        tableView.style.display = 'block';
        cardsView.style.display = 'none';
        tableBtn.classList.add('active');
        cardsBtn.classList.remove('active');
    } else {
        tableView.style.display = 'none';
        cardsView.style.display = 'grid';
        tableBtn.classList.remove('active');
        cardsBtn.classList.add('active');
    }
}

// View sale details
function viewSale(saleId) {
    fetch(`/sales/${saleId}/details/`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('saleDetailsContent').innerHTML = html;
            document.getElementById('saleDetailsModal').style.display = 'flex';
        })
        .catch(error => {
            showNotification('Error loading sale details', 'error');
        });
}

// Print bill
function printBill(saleId) {
    window.open(`/sales/${saleId}/print/`, '_blank');
}

// Delete sale - show confirmation modal
let saleToDelete = null;

function deleteSale(saleId) {
    saleToDelete = saleId;
    document.getElementById('deleteModal').style.display = 'flex';
}

// Close delete modal
function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    saleToDelete = null;
}

// Confirm delete
function confirmDelete() {
    if (!saleToDelete || isNaN(saleToDelete) || saleToDelete === 'undefined') {
        showNotification('Invalid sale ID', 'error');
        closeDeleteModal();
        return;
    }

    fetch(`/sales/${saleToDelete}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Reload the page to reflect changes
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showNotification(data.message, 'error');
            }
            closeDeleteModal();
        })
        .catch(error => {
            showNotification('Error deleting sale', 'error');
            closeDeleteModal();
        });
}

// Close sale details modal
function closeSaleDetails() {
    document.getElementById('saleDetailsModal').style.display = 'none';
}

// Show notification
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // Add to body
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Change page
function changePage(page) {
    if (!page || page === 'undefined') {
        return;
    }
    const url = new URL(window.location);
    url.searchParams.set('page', page);
    window.location.href = url.toString();
}

// Close modals on outside click
window.onclick = function (event) {
    const saleModal = document.getElementById('saleDetailsModal');
    const deleteModal = document.getElementById('deleteModal');

    if (event.target === saleModal) {
        closeSaleDetails();
    }
    if (event.target === deleteModal) {
        closeDeleteModal();
    }
}

// Send WhatsApp Bill from Details Modal
function sendWhatsAppBillFromDetail() {
    const dataStore = document.getElementById('sale-data-store');
    if (!dataStore) {
        showNotification('Error loading sale data', 'error');
        return;
    }

    try {
        // Get data from attributes
        // Note: Attribute values are strings, need to be parsed
        // We used single quotes for attributes in HTML so double quotes in JSON are preserved
        // But better to be safe with parsing
        let dataStr = dataStore.getAttribute('data-sale-json');
        let configStr = dataStore.getAttribute('data-shop-json');

        // Handle potential None/null from Python which might be 'null' in JSON string
        // or Python None might come as 'None' string if not json.dumped properly? 
        // We used json.dumps, so it should be valid JSON

        const saleData = JSON.parse(dataStr);
        const shopConfig = JSON.parse(configStr);

        let phone = '';
        if (saleData.customer && saleData.customer.phone) {
            phone = saleData.customer.phone.replace(/\D/g, '');
            if (!phone.startsWith('91') && phone.length === 10) {
                phone = '91' + phone;
            }
        }

        // Parse sale date and format
        const saleDate = new Date(saleData.sale_date);
        const currentDate = saleDate.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
        const currentTime = saleDate.toLocaleTimeString('en-IN', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });

        // Construct the professional bill message matching print format
        let message = `*${shopConfig.shopName}*\n`;
        message += `━━━━━━━━━━━━━━━━━━━━\n`;
        if (shopConfig.shopAddress) {
            message += `Address: ${shopConfig.shopAddress}\n`;
        }
        if (shopConfig.shopPhone) {
            message += `Phone: ${shopConfig.shopPhone}\n`;
        }
        message += `━━━━━━━━━━━━━━━━━━━━\n`;
        message += `*SALE RECEIPT*\n`;
        message += `Date: ${currentDate} | ${currentTime}\n`;
        message += `━━━━━━━━━━━━━━━━━━━━\n`;

        // Add customer details if available
        if (saleData.customer && saleData.customer.name) {
            message += `*Customer:* ${saleData.customer.name}\n`;
            if (saleData.customer.phone) {
                message += `Phone: ${saleData.customer.phone}\n`;
            }
            message += `━━━━━━━━━━━━━━━━━━━━\n`;
        }

        message += `*Items:*\n`;
        // Add individual bill items
        saleData.items.forEach((item, index) => {
            message += `${index + 1}. ${item.name}\n`;
            message += `   ${item.quantity} x ₹${item.price.toFixed(2)} = ₹${item.total.toFixed(2)}\n`;
        });

        message += `━━━━━━━━━━━━━━━━━━━━\n`;

        // Add payment method and status
        const paymentMethodDisplay = saleData.payment_method === 'cash' ? 'Cash' :
            saleData.payment_method === 'upi' ? 'UPI/PhonePe/GPay' :
                saleData.payment_method === 'card' ? 'Card' : 'Credit'
        message += `*Payment:* ${paymentMethodDisplay}\n`;

        if (!saleData.is_paid) {
            message += `*Status:* Credit/Pending\n`;
        } else {
            message += `*Status:* Paid\n`;
        }

        message += `━━━━━━━━━━━━━━━━━━━━\n`;
        message += `*GRAND TOTAL: ₹${saleData.total_amount.toFixed(2)}*\n`;
        message += `━━━━━━━━━━━━━━━━━━━━\n`;

        // Add notes if any
        if (saleData.notes) {
            message += `${saleData.notes}\n`;
            message += `━━━━━━━━━━━━━━━━━━━━\n`;
        }

        message += `Thank You for Shopping!\n`;
        message += `Computer Generated Bill\n`;
        message += `Powered by SubhLabh - Shop Management Simplified`;

        // Encode the message
        const encodedMessage = encodeURIComponent(message);

        // Construct dynamic WhatsApp URL
        const whatsappUrl = phone ? `https://api.whatsapp.com/send?phone=${phone}&text=${encodedMessage}` : `https://api.whatsapp.com/send?text=${encodedMessage}`;

        window.open(whatsappUrl, '_blank');

    } catch (e) {
        console.error('Error sending WhatsApp bill', e);
        showNotification('Error generating WhatsApp bill', 'error');
    }
}
