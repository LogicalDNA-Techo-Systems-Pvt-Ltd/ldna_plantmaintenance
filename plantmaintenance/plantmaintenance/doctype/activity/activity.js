// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Activity", {
// 	refresh(frm) {

// 	},
// }); 

frappe.ui.form.on('Activity', {
    refresh: function(frm) {
        if (!frm.is_new()&& frappe.user.has_role('System Manager')) {
            frm.add_custom_button(__('Parameter'), function() {
                frappe.new_doc('Parameter');
            }, __("Create"));
            frm.add_custom_button(__('Activity Group'), function() {
                frappe.new_doc('Activity Group');
            }, __("Create"));
            
            frm.add_custom_button(__('Equipment'), function() {
                frappe.set_route('List', 'Equipment');
            }, __("View")); 
        }
    },
}); 


frappe.ui.form.on('Parameter CT', {
    values: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.parameter_type === 'List' && row.values) {
            let options = row.values.split(',').map(option => option.trim()).join('\n');
            frappe.model.set_value(cdt, cdn, 'acceptance_criteria_for_list', options);

            frm.fields_dict.parameter.grid.update_docfield_property('acceptance_criteria_for_list', 'options', options);

            frm.refresh_field('parameter');
        } else {
            frm.fields_dict.parameter.grid.update_docfield_property('acceptance_criteria_for_list', 'options', '');
            frm.refresh_field('parameter');
        }
    },
});



