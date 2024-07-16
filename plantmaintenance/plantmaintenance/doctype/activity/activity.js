// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Activity", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Activity', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Parameter'), function() {
                frappe.new_doc('Parameter');
            }, __("Create"));
        }
    },
});