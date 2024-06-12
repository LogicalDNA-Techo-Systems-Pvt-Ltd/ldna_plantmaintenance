// // Copyright (c) 2024, LogicalDNA and contributors
// // For license information, please see license.txt


frappe.ui.form.on('Task Allocation', {
    refresh: function(frm) {
        frm.add_custom_button(__('Load Tasks'), function() {
            load_tasks(frm);
        });

        frm.add_custom_button(__('Download Tasks'), function() {
            download_tasks(frm);
        });

        frm.add_custom_button(__('Upload Tasks'), function() {
            upload_tasks(frm);
        });
    }
});

