// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material', {
    spare: function(frm) {
        if (frm.doc.spare) {
            frm.set_value('consumable', 0);  
        }
    },
    consumable: function(frm) {
        if (frm.doc.consumable) {
            frm.set_value('spare', 0);  
        }
    }
});
