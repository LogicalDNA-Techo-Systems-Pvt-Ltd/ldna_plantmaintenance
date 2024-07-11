// // Copyright (c) 2024, LogicalDNA and contributors
// // For license information, please see license.txt

// frappe.ui.form.on('Task Detail', {
//     readings: function(frm) {
//         const numReadings = frm.doc.readings;
        
//         if (numReadings > 10) {
//             frappe.msgprint(__('Number of readings must be less than 10.'));
//             return;
//         }
        
//         for (let i = 1; i <= 10; i++) {
//             const fieldname = `reading_${i}`;
            
//             if (i <= numReadings) {
//                 frm.set_df_property(fieldname, 'hidden', false);
//             } else {
//                 frm.set_df_property(fieldname, 'hidden', true);
//             }
//         }
//     },
    
//     onload: function(frm) {
//         frm.trigger('readings');
//     }
    
// })
// frappe.ui.form.on('Task Detail', {
//     refresh: function(frm) {
//         console.log('After save triggered');
        
//         if (frm.doc.equipment_code) {
//             frappe.call({
//                 method: 'frappe.client.get',
//                 args: {
//                     doctype: 'Equipment',
//                     name: frm.doc.equipment_code 
//                 },
//                 callback: function(r) {
//                     console.log(r.message);
//                     if (r.message && !$.isEmptyObject(r.message)) {
                      
//                         let damage_list = [];
//                         let cause_list = [];

                        
//                         if (r.message.damage && Array.isArray(r.message.damage)) {
//                             r.message.damage.forEach(d => {
//                                 damage_list.push(d.damage);
//                             });
//                         }

                       
//                         r.message.cause.forEach(c => {
//                             cause_list.push(c.cause);
//                         });

                       
//                         frm.set_query("damage", function() {
//                             return {
//                                 "filters": {
//                                     "equipment_code": frm.doc.equipment_code,
//                                     "damage": ["in", damage_list]
//                                 }
//                             };
//                         });

                        
//                         frm.set_query("cause", function() {
//                             return {
//                                 "filters": {
//                                     "equipment_code": frm.doc.equipment_code,
//                                     "cause": ["in", cause_list]
//                                 }
//                             };
//                         });

//                     } else {
//                         frappe.msgprint(__('No equipment found with this name.'));
//                     }
//                 }
//             });
//         }
//     }
// });


// frappe.ui.form.on('Task Detail', {
//     readings: function(frm) {
//         const numReadings = frm.doc.readings;
        
//         if (numReadings > 10) {
//             frappe.msgprint(__('Number of readings must be less than or equal to 10.'));
//             return;
//         }
        
//         for (let i = 1; i <= 10; i++) {
//             const fieldname = `reading_${i}`;
            
//             if (i <= numReadings) {
//                 frm.set_df_property(fieldname, 'hidden', false);
//             } else {
//                 frm.set_df_property(fieldname, 'hidden', true);
//             }
//         }
//     },
    
//     onload: function(frm) {
//         frm.trigger('readings');
//     },
    
//     type: function(frm) {
//         if (frm.doc.type === 'Breakdown') {
          
//             frm.set_value('parameter_type', '');
//         }
//     }
// });

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
        if (frm.doc.actual_end_date && frm.doc.actual_start_date && frm.doc.actual_end_date < frm.doc.actual_start_date) {
            frappe.msgprint(__('Actual End Date should be greater than or equal to Actual Start Date'));
            frappe.validated = false;
        }
    },

    before_save: function(frm) {
        const fields = ['reading_1', 'reading_2', 'reading_3', 'reading_4', 'reading_5', 'reading_6', 'reading_7', 'reading_8', 'reading_9', 'reading_10'];
    
        fields.forEach(field => {
            if (frm.doc[field] !== undefined && frm.doc[field] !== null) {
                let value = parseFloat(frm.doc[field]).toFixed(2);
                let parts = value.split('.'); // Split the number into integer and decimal parts
                if (parts[0].length > 4) {
                    let field_label = frm.fields_dict[field].df.label; // Get the field label 
                    frappe.msgprint(__("The value for {0} exceeds the maximum allowed digits before the decimal point.", [field_label]));
                    frappe.validated = false; // Prevent form submission
                } else {
                    frm.doc[field] = value;
                }
            }
        });
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


