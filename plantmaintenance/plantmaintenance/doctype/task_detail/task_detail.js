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
    },
    
    type: function(frm) {
        if (frm.doc.type === 'Breakdown') {
          
            frm.set_value('parameter_type', '');
        }
    }
});
