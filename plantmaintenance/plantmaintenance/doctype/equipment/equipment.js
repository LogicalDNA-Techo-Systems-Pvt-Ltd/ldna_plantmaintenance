// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Equipment", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Equipment', {
    on_hold: function(frm) {
        if (frm.doc.on_hold) {
            frm.set_value('on_scrap', 0);
        }
    },
    on_scrap: function(frm) {
        if (frm.doc.on_scrap) {
            frm.set_value('on_hold', 0);
        }
    }
});
