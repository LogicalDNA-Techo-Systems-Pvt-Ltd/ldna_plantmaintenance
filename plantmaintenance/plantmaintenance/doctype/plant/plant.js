// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Plant", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Plant", {
    location: function(frm, cdt, cdn) {
        var locations = [];

        // Fetch the Plant document
        frappe.model.with_doc("Plant", frm.doc.name, function() {
            var doc = frappe.model.get_doc("Plant", frm.doc.name);

            // Loop through the locations in the table_zgxc child table
            $.each(doc.table_zgxc || [], function(idx, row) {
                locations.push(row.location);
            });

            // Log the fetched locations (example)
            // console.log("Fetched locations:", locations);
        });
    }
});
