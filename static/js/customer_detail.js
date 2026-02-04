// Payment Modal Functions
function showPaymentModal() {
    document.getElementById('paymentModal').style.display = 'flex';
}

function closePaymentModal() {
    document.getElementById('paymentModal').style.display = 'none';
}

// WhatsApp Message Functions
function showWhatsAppModal() {
    console.log(' WhatsApp button clicked');

    const dataStore = document.getElementById('whatsapp-data-store');
    console.log('Data store element:', dataStore);

    if (!dataStore) {
        console.error('Data store not found!');
        alert('Error: Customer data not loaded. Please refresh the page and try again.');
        return;
    }

    try {
        // Generate the WhatsApp message
        const message = generateWhatsAppMessage();
        console.log('Generated message length:', message.length);

        const textarea = document.getElementById('whatsappMessageContent');
        const modal = document.getElementById('whatsappModal');

        if (!textarea || !modal) {
            console.error('Modal or textarea not found! Textarea:', textarea, 'Modal:', modal);
            alert('Error: Modal elements not found. Please refresh the page.');
            return;
        }

        // Populate the modal textarea
        textarea.value = message;

        // Show the modal
        modal.style.display = 'flex';
        console.log('✅ Modal displayed successfully');
    } catch (error) {
        console.error('❌ Error in showWhatsAppModal:', error);
        alert('Error opening WhatsApp modal: ' + error.message);
    }
}

function generateWhatsAppMessage() {
    const dataStore = document.getElementById('whatsapp-data-store');

    // Get data from data store
    const customerName = dataStore.getAttribute('data-customer-name') || 'Customer';
    const customerPhone = dataStore.getAttribute('data-customer-phone') || '';
    const totalUdhar = parseFloat(dataStore.getAttribute('data-customer-purchased') || 0);
    const totalPaid = parseFloat(dataStore.getAttribute('data-total-paid') || 0);
    const remainingBalance = parseFloat(dataStore.getAttribute('data-customer-udhar') || 0);
    const paymentStatus = dataStore.getAttribute('data-payment-status') || 'Due';
    const shopName = dataStore.getAttribute('data-shop-name') || 'My Shop';
    const shopPhone = dataStore.getAttribute('data-shop-phone') || '';
    const shopAddress = dataStore.getAttribute('data-shop-address') || '';

    // Get current date and time
    const now = new Date();
    const currentDate = now.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
    const currentTime = now.toLocaleTimeString('en-IN', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });

    // Build the message following the exact template format
    let message = `Shop Name : ${shopName}\n`;
    message += `━━━━━━━━━━━━━━━━━━━━\n`;
    message += `━━━━━━━━━━━━━━━━━━━━\n`;
    message += `SALE RECEIPT\n`;
    message += `Date: ${currentDate} | ${currentTime}\n`;
    message += `━━━━━━━━━━━━━━━━━━━━\n`;
    message += `Customer: ${customerName}\n`;
    message += `Phone: ${customerPhone}\n`;
    message += `━━━━━━━━━━━━━━━━━━━━\n`;
    message += `ACCOUNT SUMMARY:\n`;
    message += `Total Udhar: ₹${totalUdhar.toFixed(2)}\n`;
    message += `Paid Amount: ₹${totalPaid.toFixed(2)}\n`;
    message += `Remaining Balance: ₹${remainingBalance.toFixed(2)}\n`;
    message += `━━━━━━━━━━━━━━━━━━━━\n`;
    message += `Payment Status: ${paymentStatus}\n`;
    message += `━━━━━━━━━━━━━━━━━━━━`;

    return message;
}

function closeWhatsAppModal() {
    document.getElementById('whatsappModal').style.display = 'none';
    console.log('Modal closed');
}

function sendWhatsAppMessage() {
    console.log('📱 Sending WhatsApp message');

    const dataStore = document.getElementById('whatsapp-data-store');
    const customerPhone = dataStore.getAttribute('data-customer-phone') || '';

    // Get the edited message from textarea
    let message = document.getElementById('whatsappMessageContent').value;

    // Append the locked footer section
    const footer = `\n\nThank You for Shopping!\nComputer Generated Bill\nPowered by SubhLabh - Shop Management Simplified`;
    message += footer;

    // Format phone number (add country code if needed)
    let phone = customerPhone.replace(/\D/g, ''); // Remove non-digits
    if (phone && !phone.startsWith('91') && phone.length === 10) {
        phone = '91' + phone;
    }

    console.log('Phone number:', phone);
    console.log('Message length:', message.length);

    // Encode the message for URL
    const encodedMessage = encodeURIComponent(message);

    // Build WhatsApp URL
    const whatsappUrl = phone
        ? `https://api.whatsapp.com/send?phone=${phone}&text=${encodedMessage}`
        : `https://api.whatsapp.com/send?text=${encodedMessage}`;

    console.log('Opening WhatsApp URL');

    // Open WhatsApp in new window
    window.open(whatsappUrl, '_blank');

    // Close the modal
    closeWhatsAppModal();
}

// Close modal on outside click
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Customer detail page loaded');

    const paymentModal = document.getElementById('paymentModal');
    if (paymentModal) {
        paymentModal.addEventListener('click', function (e) {
            if (e.target === this) {
                closePaymentModal();
            }
        });
    }

    const whatsappModal = document.getElementById('whatsappModal');
    if (whatsappModal) {
        whatsappModal.addEventListener('click', function (e) {
            if (e.target === this) {
                closeWhatsAppModal();
            }
        });
        console.log('✅ WhatsApp modal event listener attached');
    } else {
        console.warn('⚠️ WhatsApp modal not found on page load');
    }

    // Close modals on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closePaymentModal();
            closeWhatsAppModal();
        }
    });

    // Check if data store exists
    const dataStore = document.getElementById('whatsapp-data-store');
    if (dataStore) {
        console.log('✅ WhatsApp data store found');
        console.log('Customer:', dataStore.getAttribute('data-customer-name'));
        console.log('Shop:', dataStore.getAttribute('data-shop-name'));
    } else {
        console.warn('⚠️ WhatsApp data store not found');
    }
});
