// // Copyright (c) 2024, LogicalDNA and contributors
// // For license information, please see license.txt

frappe.ui.form.on('Task Detail', {
    after_save: function(frm){
        frappe.call({
            method: "plantmaintenance.plantmaintenance.doctype.equipment.equipment.equipment_task_details",
            args:{
                task_detail: frm.doc
            }
        })
    },
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
        if (frm.doc.actual_end_date && frm.doc.actual_start_date && frm.doc.actual_end_date < frm.doc.actual_start_date) {
            frappe.msgprint(__('Actual End Date should be greater than or equal to Actual Start Date'));
            frappe.validated = false;
        }
    },

    before_save: function(frm) {
        const fields = ['reading_1', 'reading_2', 'reading_3', 'reading_4', 'reading_5', 
                        'reading_6', 'reading_7', 'reading_8', 'reading_9', 'reading_10'];
        
        let validationMessages = []; // Array to store validation messages
        let readingsCount = parseInt(frm.doc.readings); // Number of readings
        
        if (frm.doc.parameter_type !== 'Binary' && frm.doc.parameter_type !== 'List' && (isNaN(readingsCount) || readingsCount < 1 || readingsCount > 10)) {
            frappe.msgprint("Please specify a valid number of readings between 1 and 10.");
            frappe.validated = false; // Prevent form submission
            return;
        }
        
        let hasValidationErrors = false; // Flag to indicate if there are validation errors
        
        // Loop through only the specified number of readings
        for (let i = 0; i < readingsCount; i++) {
            let field = fields[i];
            
            if (frm.doc[field] !== undefined && frm.doc[field] !== null) {
                let value = parseFloat(frm.doc[field]).toFixed(2);
                let numericValue = parseFloat(value);
                let parameterType = frm.doc.parameter_type;
                
                if (parameterType === 'Numeric') {
                    // Check if value falls within specified range
                    let minRange = parseFloat(frm.doc.minimum_value);
                    let maxRange = parseFloat(frm.doc.maximum_value);
                    
                    if (isNaN(minRange) || isNaN(maxRange)) {
                        validationMessages.push("Please specify valid minimum and maximum values for numeric parameters.");
                        hasValidationErrors = true;
                        break;
                    }
                    
                    if (numericValue < minRange || numericValue > maxRange) {
                        validationMessages.push(
                            `The value for ${frm.fields_dict[field].df.label} must be between ${minRange} and ${maxRange}.`
                        );
                        hasValidationErrors = true;
                    }
                } else if (parameterType === 'Binary') {
                    if (frm.doc.acceptance_criteria === 'Yes' && numericValue === 0) {
                        validationMessages.push(
                            `The value for ${frm.fields_dict[field].df.label} must be 1 as per the acceptance criteria.`
                        );
                        hasValidationErrors = true;
                    } else if (frm.doc.acceptance_criteria === 'No' && numericValue === 1) {
                        validationMessages.push(
                            `The value for ${frm.fields_dict[field].df.label} must be 0 as per the acceptance criteria.`
                        );
                        hasValidationErrors = true;
                    }
                }
            }
        }
        
        if (hasValidationErrors) {
            // Set the result to 'Fail'
            frm.doc.result = 'Fail';
            
            // Show validation messages
            frappe.confirm(
                validationMessages.join("<br>"),
                function() {
                    // Continue with form submission
                    frappe.validated = true;
                },
                function() {
                    // Cancel save action
                    frappe.validated = false;
                }
                
            );
        }
        else{
            frm.doc.result = 'Pass';
        }
    },
    parameter_dropdown: function(frm) {
        let parameterDropdownValue = frm.doc.parameter_dropdown;
        let acceptanceCriteriaForList = frm.doc.acceptance_criteria_for_list;

        if (acceptanceCriteriaForList && parameterDropdownValue !== acceptanceCriteriaForList) {
            frm.doc.result = 'Fail';
        }
        else if (acceptanceCriteriaForList && parameterDropdownValue == acceptanceCriteriaForList) {
            frm.doc.result = 'Pass';
        }
    },

    refresh: function(frm) {
        // Locate the 'Material Issued' child table in the 'Inventory' tab
        let material_issued = frm.fields_dict.material_issued;

        if (material_issued && !frm.inventory_button_added) {
            // Ensure the button is added only once
            frm.inventory_button_added = true;

            // Create the button with adjusted top margin
            let button = $('<button class="btn btn-primary btn-xs" style="background-color: #eceff1; color: black; margin-top: -40px; margin-left: 90px;">Update Stock</button>')
            
            // Append the button after the 'Add Row' button
            material_issued.grid.wrapper.find('.grid-footer').append(button);
        }
    }
});


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



