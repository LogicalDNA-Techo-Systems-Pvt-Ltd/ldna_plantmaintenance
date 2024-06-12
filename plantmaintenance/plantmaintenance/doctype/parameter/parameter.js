// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Parameter", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on('Parameter', {
    validate: function(frm) {
        if (!frm.doc.numeric && !frm.doc.binary) {
            frappe.msgprint(__('Either "Numeric" or "Binary" check field must be checked.'));
            frappe.validated = false;
        }

    }
});





 