// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt


frappe.ui.form.on("Settings", {
    validate: function(frm) {
        if (frm.doc.end_date && frm.doc.start_date && frm.doc.end_date < frm.doc.start_date) {
            frappe.msgprint(__('End Date should be greater than or equal to Start Date'));
            frappe.validated = false;
        }
    },
    onload: function(frm){
        frappe.call({
            method:"plantmaintenance.plantmaintenance.doctype.settings.settings.get_context",
            callback: function(r){
                console.log(frm)
                    var data = r.message
                    $(frm.fields_dict["subscribe_and_unsubscribe"].wrapper).html(data);
                    refresh_field("subscribe_and_unsubscribe");
            }
        })
    }
});
