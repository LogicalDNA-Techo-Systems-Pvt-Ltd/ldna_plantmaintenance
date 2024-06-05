// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.ui.form.on("Schedule List", {
	refresh(frm) {

        frm.add_custom_button(__('Schedule Task'), function() {
            // Handle button click event
            // Redirect to another DocType
            frappe.set_route('Form', 'Task Allocation');
        });

	},
});
