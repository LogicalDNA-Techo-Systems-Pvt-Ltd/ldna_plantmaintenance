// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt



frappe.ui.form.on('Activity Group', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Activity'), function() {
                frappe.new_doc('Activity');
            }, __("Create"));
        }
    },
});