// Global variables
let billItems = [];
let lastSaleId = null;
let products = [];
let customers = [];
let offers = [];
let selectedCustomer = null;
let currentDiscount = 0;
let selectedOfferId = null;

// Initialize data from global config
function initializeBillingData() {
    if (window.billingConfig) {
        products = JSON.parse(window.billingConfig.productsJson);
        customers = JSON.parse(window.billingConfig.customersJson);
        offers = JSON.parse(window.billingConfig.offersJson);
    }
}

// Customer search and selection
function searchCustomers() {
    const searchTerm = document.getElementById('customerSearchInput').value.toLowerCase();
    const results = document.getElementById('customerResults');

    if (searchTerm.length === 0) {
        // Show walk-in option
        results.innerHTML = `
        <div class="customer-result-item" onclick="selectCustomer(null, 'Walk-in Customer')">
            <span class="customer-result-name">🚶 Walk-in Customer (No Credit)</span>
        </div>
    `;
        results.classList.add('show');
        return;
    }

    const filtered = customers.filter(c =>
        c.name.toLowerCase().includes(searchTerm) ||
        c.phone.includes(searchTerm)
    );

    if (filtered.length > 0) {
        results.innerHTML = `
        <div class="customer-result-item" onclick="selectCustomer(null, 'Walk-in Customer')">
            <span class="customer-result-name">🚶 Walk-in Customer (No Credit)</span>
        </div>
    ` + filtered.map(c => `
        <div class="customer-result-item" onclick='selectCustomer(${c.id}, "${c.name.replace(/"/g, '&quot;')}", "${c.phone}", ${c.credit_amount})'>
            <span class="customer-result-name">${c.name}</span>
            <span class="customer-result-details">
                📞 ${c.phone}
                ${parseFloat(c.credit_amount) > 0 ? ` | <span class="customer-result-credit">Credit: ₹${parseFloat(c.credit_amount).toFixed(2)}</span>` : ''}
            </span>
        </div>
    `).join('');
        results.classList.add('show');
    } else {
        results.innerHTML = `
        <div class="customer-result-item" onclick="selectCustomer(null, 'Walk-in Customer')">
            <span class="customer-result-name">🚶 Walk-in Customer (No Credit)</span>
        </div>
        <div class="add-customer-result" onclick="showInlineAddCustomerForm('${searchTerm}')">
            <span class="add-customer-icon">➕</span>
            <span class="add-customer-text">Add "${searchTerm}" as new customer</span>
        </div>
    `;
        results.classList.add('show');
    }
}

function showCustomerResults() {
    document.getElementById('customerResults').classList.add('show');
}

function selectCustomer(id, name, phone = '', credit = 0) {
    selectedCustomer = id ? { id, name, phone, credit } : null;
    document.getElementById('selectedCustomerId').value = id || '';
    document.getElementById('customerSearchInput').value = name;
    document.getElementById('customerResults').classList.remove('show');

    const info = document.getElementById('customerInfo');
    if (id) {
        document.getElementById('customerName').textContent = name;
        document.getElementById('customerPhone').textContent = phone;
        document.getElementById('customerCredit').textContent = '₹' + parseFloat(credit).toFixed(2);
        info.style.display = 'block';
    } else {
        info.style.display = 'none';
    }
}

function clearCustomer() {
    selectedCustomer = null;
    document.getElementById('selectedCustomerId').value = '';
    document.getElementById('customerSearchInput').value = '';
    document.getElementById('customerInfo').style.display = 'none';
    showNotification('Customer cleared', 'success');
}

// Update customer info when selected (legacy function for compatibility)
function updateCustomerInfo() {
    // This function is now handled by selectCustomer
}

// Search products including services
function searchProducts() {
    const searchTerm = document.getElementById('productSearch').value.toLowerCase();
    const results = document.getElementById('productResults');

    if (searchTerm.length < 2) {
        results.classList.remove('show');
        return;
    }

    const filtered = products.filter(p =>
        p.name.toLowerCase().includes(searchTerm) && p.is_active
    );

    if (filtered.length > 0) {
        results.innerHTML = filtered.map(p => `
        <div class="product-item" onclick="addProduct(${p.id})">
            <span class="product-name">${p.name}</span>
            <span class="product-details">
                ₹${parseFloat(p.price).toFixed(2)} ${p.product_type === 'service' ? '' : 'per ' + p.unit}
                ${p.product_type === 'service' ? '<span class="service-badge">Service</span>' : ''}
                ${p.product_type === 'product' ? '| Stock: <span class="product-stock ' + (parseFloat(p.stock_quantity) < 10 ? 'low' : '') + '">' + parseFloat(p.stock_quantity).toFixed(2) + '</span>' : ''}
            </span>
        </div>
    `).join('');
        results.classList.add('show');
    } else {
        results.innerHTML = '<div class="product-item">No products or services found</div>';
        results.classList.add('show');
    }
}

// Add product/service to bill
function addProduct(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    // Check if already in bill
    const existing = billItems.find(item => item.id === productId && item.type === 'product');
    if (existing) {
        const newQty = existing.quantity + (product.product_type === 'service' ? 1 : 1);
        if (product.product_type === 'product' && newQty > parseFloat(product.stock_quantity)) {
            showNotification('Cannot exceed available stock!', 'error');
            return;
        }
        existing.quantity = newQty;
        updateBillDisplay();
        showNotification('Quantity increased', 'success');
        return;
    }

    // Add new item
    const item = {
        id: product.id,
        name: product.name,
        price: parseFloat(product.price),
        quantity: product.product_type === 'service' ? 1 : 1,
        type: 'product', // product or service
        product_type: product.product_type
    };

    if (product.product_type === 'product') {
        item.unit = product.unit;
        item.stock = parseFloat(product.stock_quantity);
    }

    billItems.push(item);

    updateBillDisplay();
    document.getElementById('productSearch').value = '';
    document.getElementById('productResults').classList.remove('show');
    showNotification('Item added to bill', 'success');
}

// Show custom item modal
function showCustomItemModal() {
    document.getElementById('customItemForm').reset();
    document.getElementById('customItemModal').style.display = 'flex';
    document.getElementById('productResults').classList.remove('show');
}

// Close custom item modal
function closeCustomItemModal() {
    document.getElementById('customItemModal').style.display = 'none';
}

// Add custom item to bill
function addCustomItem(event) {
    event.preventDefault();

    const name = document.getElementById('customItemName').value.trim();
    const description = document.getElementById('customItemDescription').value.trim();
    const price = parseFloat(document.getElementById('customItemPrice').value);
    const quantity = parseFloat(document.getElementById('customItemQuantity').value) || 1;

    if (!name || isNaN(price) || price <= 0) {
        showNotification('Please fill all required fields!', 'error');
        return;
    }

    // Add custom item
    const item = {
        id: 'custom_' + Date.now(), // Unique ID for custom items
        name: name,
        description: description,
        price: price,
        quantity: quantity,
        type: 'custom',
        product_type: 'service' // Treat custom items as services
    };

    billItems.push(item);

    updateBillDisplay();
    closeCustomItemModal();
    showNotification('Custom item added to bill', 'success');
}

// Update bill display with service support
function updateBillDisplay() {
    const container = document.getElementById('billItems');
    const summaryItems = document.getElementById('summaryItems');

    if (billItems.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>🛍️ No items added yet</p></div>';
        summaryItems.innerHTML = '<p class="no-items">No items added</p>';
        document.getElementById('subtotal').textContent = '₹0.00';
        document.getElementById('totalAmount').textContent = '₹0.00';
        document.getElementById('itemCount').textContent = '0';
        document.getElementById('totalQty').textContent = '0';
        document.getElementById('printBillBtn').disabled = true;
        return;
    }

    // Update bill items
    container.innerHTML = billItems.map((item, index) => {
        if (item.type === 'custom') {
            // Custom item
            return `
            <div class="bill-item">
                <div class="item-name">${item.name}${item.description ? `<br><small>${item.description}</small>` : ''}</div>
                <div class="item-price">₹${item.price.toFixed(2)}</div>
                <div class="item-qty">
                    <input 
                        type="number" 
                        id="qty-${index}"
                        class="qty-input" 
                        value="${item.quantity}" 
                        min="0.01"
                        step="0.01"
                        onchange="handleQuantityInput(${index})"
                        onblur="handleQuantityInput(${index})"
                    >
                    <span class="qty-unit">unit</span>
                </div>
                <div class="item-total">₹${(item.price * item.quantity).toFixed(2)}</div>
                <button class="item-remove" onclick="removeItem(${index})">🗑️</button>
            </div>
        `;
        } else if (item.product_type === 'service') {
            // Service item
            return `
            <div class="bill-item">
                <div class="item-name">${item.name} <span class="service-badge">Service</span></div>
                <div class="item-price">₹${item.price.toFixed(2)}</div>
                <div class="item-qty">
                    <input 
                        type="number" 
                        id="qty-${index}"
                        class="qty-input" 
                        value="${item.quantity}" 
                        min="1"
                        step="1"
                        onchange="handleQuantityInput(${index})"
                        onblur="handleQuantityInput(${index})"
                    >
                    <span class="qty-unit">unit</span>
                </div>
                <div class="item-total">₹${(item.price * item.quantity).toFixed(2)}</div>
                <button class="item-remove" onclick="removeItem(${index})">🗑️</button>
            </div>
        `;
        } else {
            // Product item
            return `
            <div class="bill-item">
                <div class="item-name">${item.name}</div>
                <div class="item-price">₹${item.price.toFixed(2)} / ${item.unit}</div>
                <div class="item-qty">
                    <input 
                        type="number" 
                        id="qty-${index}"
                        class="qty-input" 
                        value="${item.quantity}" 
                        min="0.01"
                        step="0.01"
                        max="${item.stock}"
                        onchange="handleQuantityInput(${index})"
                        onblur="handleQuantityInput(${index})"
                    >
                    <span class="qty-unit">${item.unit}</span>
                </div>
                <div class="item-total">₹${(item.price * item.quantity).toFixed(2)}</div>
                <button class="item-remove" onclick="removeItem(${index})">🗑️</button>
            </div>
        `;
        }
    }).join('');

    // Update summary
    summaryItems.innerHTML = billItems.map(item => {
        if (item.type === 'custom') {
            return `
            <div class="summary-item">
                <div>
                    <div class="summary-item-name">${item.name}${item.description ? ` (${item.description})` : ''}</div>
                    <div class="summary-item-details">${item.quantity} unit x ₹${item.price.toFixed(2)}</div>
                </div>
                <div class="summary-item-price">₹${(item.price * item.quantity).toFixed(2)}</div>
            </div>
        `;
        } else if (item.product_type === 'service') {
            return `
            <div class="summary-item">
                <div>
                    <div class="summary-item-name">${item.name} <span class="service-badge">Service</span></div>
                    <div class="summary-item-details">${item.quantity} unit x ₹${item.price.toFixed(2)}</div>
                </div>
                <div class="summary-item-price">₹${(item.price * item.quantity).toFixed(2)}</div>
            </div>
        `;
        } else {
            return `
            <div class="summary-item">
                <div>
                    <div class="summary-item-name">${item.name}</div>
                    <div class="summary-item-details">${item.quantity} ${item.unit} x ₹${item.price.toFixed(2)}</div>
                </div>
                <div class="summary-item-price">₹${(item.price * item.quantity).toFixed(2)}</div>
            </div>
        `;
        }
    }).join('');

    // Calculate totals
    const total = billItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const totalQty = billItems.reduce((sum, item) => sum + item.quantity, 0);

    // Calculate Discount
    updateOfferDropdown(total);
    currentDiscount = calculateDiscount(total);
    const finalTotal = Math.max(0, total - currentDiscount);

    document.getElementById('subtotal').textContent = '₹' + total.toFixed(2);
    document.getElementById('discountAmount').textContent = '-₹' + currentDiscount.toFixed(2);
    document.getElementById('totalAmount').textContent = '₹' + finalTotal.toFixed(2);
    document.getElementById('itemCount').textContent = billItems.length;
    document.getElementById('totalQty').textContent = totalQty.toFixed(2);
    document.getElementById('printBillBtn').disabled = false;
}

// Update quantity with service support
function updateQuantity(index, value) {
    const item = billItems[index];
    const inputElement = document.getElementById(`qty-${index}`);

    // Parse value
    const qty = parseFloat(value);

    // Validation
    if (isNaN(qty) || qty <= 0) {
        inputElement.classList.add('error');
        showNotification('Please enter a valid quantity!', 'error');
        return false;
    }

    // For services and custom items, quantity can be any positive number
    if (item.product_type === 'product' && qty > item.stock) {
        inputElement.classList.add('error');
        showNotification(`Only ${item.stock} ${item.unit} available!`, 'error');
        inputElement.value = item.quantity;
        return false;
    }

    // Update quantity
    item.quantity = qty;
    inputElement.classList.remove('error');
    updateBillDisplay();
    return true;
}

// Handle quantity input change
function handleQuantityInput(index) {
    const inputElement = document.getElementById(`qty-${index}`);
    const value = inputElement.value;

    if (updateQuantity(index, value)) {
        inputElement.classList.remove('error');
    }
}

// Remove item
function removeItem(index) {
    billItems.splice(index, 1);
    updateBillDisplay();
    showNotification('Item removed', 'success');
}

// Update payment status
function updatePaymentStatus() {
    const method = document.getElementById('paymentMethod').value;
    const statusDiv = document.getElementById('paymentStatus');

    if (method === 'credit') {
        statusDiv.innerHTML = '<span class="status-badge credit">Credit</span>';

        // Check if customer is selected
        const customerId = document.getElementById('selectedCustomerId').value;
        if (!customerId) {
            showNotification('Please select a customer for credit sales!', 'error');
        }
    } else {
        statusDiv.innerHTML = '<span class="status-badge paid">Paid</span>';
    }
}

// Save sale with service support
async function saveSale() {
    if (billItems.length === 0) {
        showNotification('Please add at least one item!', 'error');
        return;
    }

    // Validate all quantities
    let hasError = false;
    billItems.forEach((item, index) => {
        const inputElement = document.getElementById(`qty-${index}`);
        const qty = parseFloat(inputElement.value);

        if (isNaN(qty) || qty <= 0) {
            inputElement.classList.add('error');
            hasError = true;
        } else if (item.product_type === 'product' && qty > item.stock) {
            inputElement.classList.add('error');
            hasError = true;
        }
    });

    if (hasError) {
        showNotification('Please fix quantity errors before saving!', 'error');
        return;
    }

    const customerId = document.getElementById('selectedCustomerId').value;
    const paymentMethod = document.getElementById('paymentMethod').value;

    if (paymentMethod === 'credit' && !customerId) {
        showNotification('Please select a customer for credit sales!', 'error');
        return;
    }

    const isPaid = paymentMethod !== 'credit';
    const notes = document.getElementById('saleNotes').value;

    const saleData = {
        customer_id: customerId || null,
        payment_method: paymentMethod,
        is_paid: isPaid,
        notes: notes,
        offer_id: selectedOfferId,
        discount_amount: currentDiscount,
        items: billItems.map(item => {
            if (item.type === 'custom') {
                // For custom items, we'll create a temporary product on the backend
                return {
                    product_id: null,
                    custom_name: item.name,
                    custom_description: item.description || '',
                    custom_price: item.price,
                    quantity: item.quantity
                };
            } else {
                // For regular products/services
                return {
                    product_id: item.id,
                    quantity: item.quantity,
                    price: item.price
                };
            }
        })
    };

    try {
        document.getElementById('saveSaleBtn').disabled = true;
        document.getElementById('saveSaleBtn').textContent = 'Saving...';

        const response = await fetch(window.billingConfig.billingUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.billingConfig.csrfToken
            },
            body: JSON.stringify(saleData)
        });

        const data = await response.json();

        if (data.success) {
            lastSaleId = data.sale_id;
            const totalAmount = parseFloat(data.total_amount).toFixed(2);
            showSuccessActions(data.sale_id, totalAmount);

            // Update product stock in local data for products only
            billItems.forEach(item => {
                if (item.type === 'product' && item.product_type === 'product') {
                    const product = products.find(p => p.id === item.id);
                    if (product) {
                        product.stock_quantity = (parseFloat(product.stock_quantity) - item.quantity).toString();
                    }
                }
            });
        } else {
            showNotification(data.message || 'Error saving sale!', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        document.getElementById('saveSaleBtn').disabled = false;
        document.getElementById('saveSaleBtn').textContent = '💾 Save Sale';
    }
}

// Show success actions in summary card
function showSuccessActions(saleId, amount) {
    document.getElementById('saleIdDisplay').innerHTML = `Total Amount: <strong>₹${amount}</strong>`;

    // Swap buttons
    document.getElementById('mainSummaryActions').style.display = 'none';
    document.getElementById('postSaleActions').style.display = 'block';

    // Disable inputs to prevent changes after save
    disableBillingInputs(true);

    showNotification('Sale recorded successfully!', 'success');
}

// Disable/Enable billing inputs
function disableBillingInputs(disabled) {
    const selectors = [
        '#customerSearchInput',
        '#productSearch',
        '#paymentMethod',
        '#saleNotes',
        '#offerSelect',
        '.qty-input',
        '.item-remove',
        '.btn-link'
    ];

    selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
            if (el.tagName === 'BUTTON' || el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA') {
                el.disabled = disabled;
                if (disabled) el.style.opacity = '0.7';
                else el.style.opacity = '1';
            }
        });
    });
}

// Print bill
function printLastBill() {
    if (lastSaleId) {
        window.open('/sales/' + lastSaleId + '/print/', '_blank');
    }
}

// Print current bill (after save)
function printBill() {
    if (lastSaleId) {
        printLastBill();
    }
}

// New sale
function newSale() {
    resetForm();
}

// Send bill via WhatsApp
function sendWhatsAppBill() {
    console.log('sendWhatsAppBill called');
    console.log('lastSaleId:', lastSaleId);

    if (!lastSaleId) {
        showNotification('No sale record found! Save the sale first.', 'error');
        return;
    }

    try {
        // Get customer phone number
        let phone = '';
        if (selectedCustomer && selectedCustomer.phone) {
            phone = selectedCustomer.phone.toString().replace(/\D/g, '');
            // Add India country code (91) if it's a 10-digit number
            if (phone.length === 10) {
                phone = '91' + phone;
            }
        }

        // Get sale details from UI
        const saleId = lastSaleId;
        const totalAmountText = document.getElementById('totalAmount').textContent;
        const currentDate = new Date().toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
        const currentTime = new Date().toLocaleTimeString('en-IN', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });

        // Get shop details from config
        const shopName = window.billingConfig && window.billingConfig.shopName ? window.billingConfig.shopName : "SubhLabh";
        const shopAddress = window.billingConfig && window.billingConfig.shopAddress ? window.billingConfig.shopAddress : "";
        const shopPhone = window.billingConfig && window.billingConfig.shopPhone ? window.billingConfig.shopPhone : "";

        // Construct the professional bill message matching print format
        let message = `*${shopName}*\n`;
        message += `━━━━━━━━━━━━━━━━━━━━\n`;
        if (shopAddress) {
            message += `Address: ${shopAddress}\n`;
        }
        if (shopPhone) {
            message += `Phone: ${shopPhone}\n`;
        }
        message += `━━━━━━━━━━━━━━━━━━━━\n`;
        message += `*SALE RECEIPT*\n`;
        message += `Date: ${currentDate} | ${currentTime}\n`;
        message += `━━━━━━━━━━━━━━━━━━━━\n`;

        // Add customer details if available
        if (selectedCustomer && selectedCustomer.name) {
            message += `*Customer:* ${selectedCustomer.name}\n`;
            if (selectedCustomer.phone) {
                message += `Phone: ${selectedCustomer.phone}\n`;
            }
            message += `━━━━━━━━━━━━━━━━━━━━\n`;
        }

        message += `*Items:*\n`;
        // Add individual bill items
        billItems.forEach((item, index) => {
            const itemTotal = (item.price * item.quantity).toFixed(2);
            if (item.type === 'product' && item.product_type === 'product') {
                message += `${index + 1}. ${item.name}\n`;
                message += `   ${item.quantity} x ₹${item.price.toFixed(2)} = ₹${itemTotal}\n`;
            } else {
                message += `${index + 1}. ${item.name}\n`;
                message += `   ${item.quantity} x ₹${item.price.toFixed(2)} = ₹${itemTotal}\n`;
            }
        });

        message += `━━━━━━━━━━━━━━━━━━━━\n`;

        // Add payment method and status
        const paymentMethod = document.getElementById('paymentMethod') ? document.getElementById('paymentMethod').value : 'cash';
        const paymentMethodDisplay = paymentMethod === 'cash' ? 'Cash' :
                                   paymentMethod === 'upi' ? 'UPI/PhonePe/GPay' :
                                   paymentMethod === 'card' ? 'Card' : 'Credit'
        message += `*Payment:* ${paymentMethodDisplay}\n`;

        if (paymentMethod === 'credit') {
            message += `*Status:* Credit/Pending\n`;
        } else {
            message += `*Status:* Paid\n`;
        }

        message += `━━━━━━━━━━━━━━━━━━━━\n`;
        message += `*GRAND TOTAL: ₹${totalAmountText.replace('₹', '')}*\n`;
        message += `━━━━━━━━━━━━━━━━━━━━\n`;

        // Add notes if any
        const notes = document.getElementById('saleNotes') ? document.getElementById('saleNotes').value.trim() : '';
        if (notes) {
            message += `${notes}\n`;
            message += `━━━━━━━━━━━━━━━━━━━━\n`;
        }

        message += `Thank You for Shopping!\n`;
        message += `Computer Generated Bill\n`;
        message += `Powered by SubhLabh - Shop Management Simplified`;

        // Encode the message
        const encodedMessage = encodeURIComponent(message);

        // Construct dynamic WhatsApp URL
        let whatsappUrl;
        if (phone && phone.length >= 10) {
            // Direct chat if phone number exists
            whatsappUrl = `https://api.whatsapp.com/send?phone=${phone}&text=${encodedMessage}`;
        } else {
            // Generic share if no phone
            whatsappUrl = `https://api.whatsapp.com/send?text=${encodedMessage}`;
            showNotification('Customer phone missing. Please select contact manually.', 'info');
        }

        console.log('Opening WhatsApp URL:', whatsappUrl);
        window.open(whatsappUrl, '_blank');

    } catch (error) {
        console.error('WhatsApp Error:', error);
        showNotification('Something went wrong while sending WhatsApp message.', 'error');
    }
}

// Reset form
function resetForm() {
    billItems = [];
    lastSaleId = null;
    selectedCustomer = null;
    document.getElementById('selectedCustomerId').value = '';
    document.getElementById('customerSearchInput').value = '';
    document.getElementById('paymentMethod').value = 'cash';
    document.getElementById('saleNotes').value = '';
    document.getElementById('productSearch').value = '';
    document.getElementById('customerInfo').style.display = 'none';
    updatePaymentStatus();
    updateBillDisplay();

    // Reset buttons
    document.getElementById('mainSummaryActions').style.display = 'flex';
    document.getElementById('postSaleActions').style.display = 'none';

    // Re-enable inputs
    disableBillingInputs(false);

    showNotification('Form reset', 'success');
}

// Add customer modal
function showAddCustomerModal() {
    document.getElementById('addCustomerModal').style.display = 'flex';
    document.getElementById('customerResults').classList.remove('show');
}

function closeAddCustomerModal() {
    document.getElementById('addCustomerModal').style.display = 'none';
    document.getElementById('addCustomerForm').reset();
}

async function saveNewCustomer(event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append('name', document.getElementById('newCustomerName').value);
    formData.append('phone', document.getElementById('newCustomerPhone').value);
    formData.append('notes', document.getElementById('newCustomerNotes').value);

    try {
        const response = await fetch(window.billingConfig.customerCreateUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.billingConfig.csrfToken,
                'X-Requested-With': 'XMLHttpRequest'  // Indicate AJAX request
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Add new customer to the customers array
            const newCustomer = {
                id: data.customer_id,
                name: document.getElementById('newCustomerName').value,
                phone: document.getElementById('newCustomerPhone').value,
                credit_amount: "0.00"
            };
            customers.push(newCustomer);

            // Close modal and reset form
            closeAddCustomerModal();
            document.getElementById('addCustomerForm').reset();

            showNotification('Customer added successfully!', 'success');
        } else {
            showNotification(data.error || 'Error adding customer', 'error');
        }
    } catch (error) {
        showNotification('Network error', 'error');
    }
}

// Show inline add customer form
function showInlineAddCustomerForm(searchTerm) {
    // Close the dropdown
    document.getElementById('customerResults').classList.remove('show');

    // Create inline form
    const customerSelectDiv = document.querySelector('.customer-select');
    const inlineForm = document.createElement('div');
    inlineForm.className = 'inline-add-customer-form';
    inlineForm.id = 'inlineAddCustomerForm';
    inlineForm.innerHTML = `
    <h4 style="margin: 0 0 15px 0; color: var(--dark);">➕ Add New Customer</h4>
    <div class="form-group">
        <label class="form-label">Name *</label>
        <input type="text" id="inlineCustomerName" class="form-input" value="${searchTerm}" required>
        <div id="inlineNameError" class="error-message">Please enter customer name</div>
    </div>
    <div class="form-group">
        <label class="form-label">Phone *</label>
        <input type="tel" id="inlineCustomerPhone" class="form-input" pattern="[0-9]{10}" required>
        <div id="inlinePhoneError" class="error-message">Please enter a valid 10-digit phone number</div>
    </div>
    <div class="form-group">
        <label class="form-label">Address (Optional)</label>
        <input type="text" id="inlineCustomerAddress" class="form-input">
    </div>
    <div class="form-group">
        <label class="form-label">Notes (Optional)</label>
        <textarea id="inlineCustomerNotes" class="form-textarea" rows="2"></textarea>
    </div>
    <div class="form-actions">
        <button type="button" class="btn-cancel-inline" onclick="cancelInlineAddCustomer()">Cancel</button>
        <button type="button" class="btn-submit-inline" onclick="saveInlineCustomer()">Add Customer</button>
    </div>
`;

    // Insert the form after the customer search input
    customerSelectDiv.appendChild(inlineForm);

    // Focus on the phone field
    document.getElementById('inlineCustomerPhone').focus();
}

// Cancel inline add customer
function cancelInlineAddCustomer() {
    const inlineForm = document.getElementById('inlineAddCustomerForm');
    if (inlineForm) {
        inlineForm.remove();
    }
    document.getElementById('customerSearchInput').focus();
}

// Save inline customer
async function saveInlineCustomer() {
    const name = document.getElementById('inlineCustomerName').value.trim();
    const phone = document.getElementById('inlineCustomerPhone').value.trim();
    const address = document.getElementById('inlineCustomerAddress').value.trim();
    const notes = document.getElementById('inlineCustomerNotes').value.trim();

    // Reset error messages
    document.getElementById('inlineNameError').style.display = 'none';
    document.getElementById('inlinePhoneError').style.display = 'none';

    // Validation
    let hasError = false;
    if (!name) {
        document.getElementById('inlineNameError').style.display = 'block';
        hasError = true;
    }

    if (!phone || phone.length !== 10 || !/^\d+$/.test(phone)) {
        document.getElementById('inlinePhoneError').style.display = 'block';
        hasError = true;
    }

    if (hasError) {
        return;
    }

    try {
        // Create form data
        const formData = new FormData();
        formData.append('name', name);
        formData.append('phone', phone);
        formData.append('address', address);
        formData.append('notes', notes);

        // Show loading state
        const submitBtn = document.querySelector('.btn-submit-inline');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Saving...';
        submitBtn.disabled = true;

        const response = await fetch(window.billingConfig.customerCreateUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.billingConfig.csrfToken
            },
            body: formData
        });

        if (response.ok) {
            // Parse JSON response
            const data = await response.json();

            if (data.success) {
                // Add new customer to the customers array
                const newCustomer = {
                    id: data.customer_id,
                    name: name,
                    phone: phone,
                    credit_amount: "0.00"
                };
                customers.push(newCustomer);

                // Select the new customer
                selectCustomer(data.customer_id, name, phone, 0);

                // Remove the inline form
                cancelInlineAddCustomer();

                // Show success notification
                showNotification('Customer added and selected successfully!', 'success');
            } else {
                showNotification(data.error || 'Error adding customer', 'error');
            }
        } else {
            showNotification('Error adding customer', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        // Restore button state
        const submitBtn = document.querySelector('.btn-submit-inline');
        if (submitBtn) {
            submitBtn.textContent = 'Add Customer';
            submitBtn.disabled = false;
        }
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Close dropdowns when clicking outside
document.addEventListener('click', function (e) {
    if (!e.target.closest('.product-search')) {
        document.getElementById('productResults').classList.remove('show');
    }
    if (!e.target.closest('.customer-select')) {
        document.getElementById('customerResults').classList.remove('show');
    }
});

// Prevent form submission on Enter key in quantity inputs
document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target.classList.contains('qty-input')) {
        e.preventDefault();
        e.target.blur();
    }
});

// Offer Functions
function handleOfferChange() {
    const offerSelect = document.getElementById('offerSelect');
    selectedOfferId = offerSelect.value || null;
    updateBillDisplay();
}

function updateOfferDropdown(total) {
    const offerSelect = document.getElementById('offerSelect');
    const currentVal = offerSelect.value;

    offerSelect.innerHTML = '<option value="">None</option>';

    offers.forEach(offer => {
        if (total >= parseFloat(offer.min_purchase_amount)) {
            const option = document.createElement('option');
            option.value = offer.id;

            // Format label based on offer type
            let label = offer.name;
            const value = parseFloat(offer.discount_value);

            if (offer.type === 'percentage') {
                label += ` (${value}% off)`;
            } else if (offer.type === 'flat') {
                label += ` (₹${value} off)`;
            } else if (offer.type === 'bogo') {
                label += ` (Buy ${offer.buy_quantity} Get ${offer.get_quantity})`;
            }

            option.textContent = label;
            if (offer.id == currentVal) option.selected = true;
            offerSelect.appendChild(option);
        }
    });
}

function calculateDiscount(total) {
    if (!selectedOfferId) return 0;

    const offer = offers.find(o => o.id == selectedOfferId);
    if (!offer) return 0;

    if (total < parseFloat(offer.min_purchase_amount)) {
        selectedOfferId = null;
        document.getElementById('offerSelect').value = '';
        return 0;
    }

    let discount = 0;
    const value = parseFloat(offer.discount_value);

    if (offer.type === 'percentage') {
        discount = total * (value / 100);
        // Check for max discount amount if it exists (though not currently passed in JSON, safe to omit or check if added later)
        if (offer.max_discount_amount && discount > parseFloat(offer.max_discount_amount)) {
            discount = parseFloat(offer.max_discount_amount);
        }
    } else if (offer.type === 'flat') {
        discount = value;
    } else if (offer.type === 'bogo') {
        // For BOGO, we might need more complex logic. 
        // For now, if it's just a label, we might not apply a monetary discount on the total
        // OR we assume the user manually adjusts items?
        // Let's assume 0 monetary discount for now strictly from this function unless BOGO has a specific value.
        // If discount_value > 0 even for BOGO, we use it.
        discount = value > 0 ? value : 0;
    }

    return discount;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    initializeBillingData();
    updatePaymentStatus();
    updateBillDisplay();
});