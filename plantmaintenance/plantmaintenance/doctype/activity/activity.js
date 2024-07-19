// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Activity", {
// 	refresh(frm) {

// 	},
// }); 

frappe.ui.form.on('Activity', {
    refresh: function(frm) {
        if (!frm.is_new()&& frappe.user.has_role('System Manager')) {
            frm.add_custom_button(__('Parameter'), function() {
                frappe.new_doc('Parameter');
            }, __("Create"));
            frm.add_custom_button(__('Equipment'), function() {
                frappe.set_route('List', 'Equipment');
            }, __("View")); 
        }
    },
}); 




