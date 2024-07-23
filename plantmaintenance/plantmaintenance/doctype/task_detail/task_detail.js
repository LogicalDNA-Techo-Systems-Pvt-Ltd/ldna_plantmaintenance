frappe.ui.form.on('Task Detail', {
    readings: function(frm) {
        const numReadings = frm.doc.readings;
        
        if (numReadings > 10) {
            frappe.msgprint(__('Number of readings must be less than or equal to 10.'));
            return;
        }
        
        for (let i = 1; i <= 10; i++) {
            const fieldname = `reading_${i}`;
            
            if (i <= numReadings) {
                frm.set_df_property(fieldname, 'hidden', false);
            } else {
                frm.set_df_property(fieldname, 'hidden', true);
            }
        }
    },
    
    onload: function(frm) {
        frm.trigger('readings');
        
        // Fetch parameter details if parameter field is set
        if (frm.doc.parameter) {
            fetch_parameter_details(frm);
        }
    },
    
    parameter: function(frm) {
        // Fetch parameter details whenever parameter field changes
        fetch_parameter_details(frm);
    },
    
    type: function(frm) {
        if (frm.doc.type === 'Breakdown') {
            frm.set_value('parameter_type', '');
        }
    },

    validate: function(frm) {
        if (frm.doc.actual_end_date < frm.doc.actual_start_date) {
            frappe.msgprint(__('Actual End Date should be greater than or equal to Actual Start Date'));
            frappe.validated = false;
        }
    },

    before_save: function(frm) {
        const fields = ['reading_1', 'reading_2', 'reading_3', 'reading_4', 'reading_5', 
                        'reading_6', 'reading_7', 'reading_8', 'reading_9', 'reading_10'];
        
        let readingsCount = frm.doc.readings; 
        let hasValidationErrors = false; 
        
        if (frm.doc.parameter_type === 'Numeric') {
            let minRange = frm.doc.minimum_value;
            let maxRange = frm.doc.maximum_value;
            
            for (let i = 0; i < readingsCount; i++) {
                let field = fields[i];
                let numericValue = frm.doc[field];
                if (numericValue < minRange || numericValue > maxRange) {
                    hasValidationErrors = true;
                }
            }
        }
        if (hasValidationErrors) {
            frm.doc.result = 'Fail';
        } else {
            frm.doc.result = 'Pass';
        }
    },

    refresh: function(frm) {
        let material_issued = frm.fields_dict.material_issued;
        if (material_issued && !frm.inventory_button_added) {
            frm.inventory_button_added = true;

            let button = $('<button class="btn btn-primary btn-xs" style="margin-top: -40px; margin-left: 72%;">Update Quantity</button>');
            let button1 = $('<button class="btn btn-primary btn-xs" style="margin-top: -80px; margin-left: 87%;">Send for Approval</button>');
            button1.on('click', function() {
                let all_shortages_zero = true;
                if (all_shortages_zero) {
                    frappe.call({
                        method: "plantmaintenance.plantmaintenance.doctype.task_detail.task_detail.send_for_approval",
                        args: {
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            if (response.message) {
                                frappe.msgprint(response.message);
                                frm.doc.material_issued.forEach(item => {
                                    item.status = 'Pending Approval';
                                });
                                frm.refresh_field('material_issued');
                            }
                        }
                    });
                } 
            });

            material_issued.grid.wrapper.find('.grid-footer').append(button);
            material_issued.grid.wrapper.find('.grid-footer').append(button1);
        }
    }
});

frappe.ui.form.on('Material Issue', {
    available_quantity: function(frm, cdt, cdn) {
        calculate_shortage(frm, cdt, cdn);
    },
    required_quantity: function(frm, cdt, cdn) {
        calculate_shortage(frm, cdt, cdn);
    }
});

function calculate_shortage(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.available_quantity >= row.required_quantity) {
        row.shortage = 0;
    } 
    else {
        row.shortage = row.required_quantity - row.available_quantity;
    }
    frm.refresh_field('material_issued');
}


function fetch_parameter_details(frm) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Parameter",
            name: frm.doc.parameter
        },
        callback: function(r) {
            if (r.message) {
                let parameter = r.message;
                if (parameter.parameter_type === "List" && parameter.values) {
                    let options = parameter.values.split(',').map(option => option.trim());
                    frm.set_df_property('parameter_dropdown', 'options', options.join('\n'));
                    frm.refresh_field('parameter_dropdown');
                } else {
                    frm.set_df_property('parameter_dropdown', 'options', '');
                    frm.refresh_field('parameter_dropdown');
                }
            }
        }
    });
}


