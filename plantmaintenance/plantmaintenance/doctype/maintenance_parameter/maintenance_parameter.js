// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Maintenance Parameter", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Maintenance Parameter', {
    onload: function(frm) {
        frm.set_query('parameter_group', function() {
            return {
                filters: {
                    'is_active': 1
                }
            };
        });
    }
});
