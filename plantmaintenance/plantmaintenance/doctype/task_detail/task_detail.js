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


// frappe.ui.form.on('Task Detail', {
//     onload: function(frm) {
//         // Fetch parameter details if parameter field is set
//         if (frm.doc.parameter) {
//             fetch_parameter_details(frm);
//         }
//     },
//     parameter: function(frm) {
//         // Fetch parameter details whenever parameter field changes
//         fetch_parameter_details(frm);
//     }
// });

// function fetch_parameter_details(frm) {
//     frappe.call({
//         method: "frappe.client.get",
//         args: {
//             doctype: "Parameter",
//             name: frm.doc.parameter
//         },
//         callback: function(r) {
//             if (r.message) {
//                 let parameter = r.message;
//                 if (parameter.parameter_type === "List" && parameter.text) {
//                     let options = parameter.text.split(',').map(option => option.trim());
//                     frm.set_df_property('parameter_dropdown', 'options', options.join('\n'));
//                     frm.refresh_field('parameter_dropdown');
//                 } else {
//                     frm.set_df_property('parameter_dropdown', 'options', '');
//                     frm.refresh_field('parameter_dropdown');
//                 }
//             }
//         }
//     });
// }


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


