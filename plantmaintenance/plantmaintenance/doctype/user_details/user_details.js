// Copyright (c) 2025, LogicalDNA and contributors
// For license information, please see license.txt

frappe.ui.form.on('User Details', {
    refresh: function(frm) {
        frm.fields_dict['user_name'].get_query = function() {
            return {
                query: "plantmaintenance.plantmaintenance.doctype.user_details.user_details.get_maintenance_managers"
            };
        };

        frm.fields_dict['maintenance_users'].get_query = function() {
            return {
                query: "plantmaintenance.plantmaintenance.doctype.user_details.user_details.get_maintenance_users"
            };
        };
        frm.fields_dict['process_manager'].get_query = function() {
            return {
                query: "plantmaintenance.plantmaintenance.doctype.user_details.user_details.get_process_managers"
            };
        };
    }
});
