# Sync WhatsApp Bill with Print Format

## Tasks
- [ ] Update `templates/customers/billing.html` to include `shopAddress` and `shopPhone` in `billingConfig`
- [ ] Update `static/js/billing.js` `sendWhatsAppBill` to use uniform template matching `sale_print.html`
- [ ] Update `customers/app_views.py` `SaleDetailView.get` to pass items and sale details to JavaScript
- [ ] Update `customers/app_views.py` `sendWhatsAppBillFromDetail` to use uniform template
- [ ] Replace hardcoded shop name with dynamic profile.shop_name (fallback to user full name)
- [ ] Add "Powered by Subhlabh" branding
- [ ] Remove "Bill No:" and show formatted date/time from sale_date

## Followup
- [ ] Test WhatsApp message generation from billing page
- [ ] Test WhatsApp message generation from sale detail page
