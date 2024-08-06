// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt


frappe.ui.form.on("Setting", {
    validate: function(frm) {
        if (frm.doc.end_date && frm.doc.start_date && frm.doc.end_date < frm.doc.start_date) {
            frappe.msgprint(__('End Date should be greater than or equal to Start Date'));
            frappe.validated = false;
        }
    },
});
