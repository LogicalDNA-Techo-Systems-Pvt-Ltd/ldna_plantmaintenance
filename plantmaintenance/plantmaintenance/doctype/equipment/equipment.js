// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment', {
     
    plant: function(frm){
        if (frm.doc.plant){
            frm.set_value('location', ''); 
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_location_list_based_on_plant',
                args: {
                    plant: frm.doc.plant,
                },
                callback: function(response){
                    if (response.message){
                        console.log(response.message)
                        var Location = response.message
                        frm.set_query('location', () => {
                            return {
                                filters: {
                                    location: ['in', Location]
                                }
                            }
                        })
                    }
                }
            })
        }
    },
    location: function(frm){
        if (frm.doc.location){
            frm.set_value('section', '');
            frm.set_value('work_center', '');
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_section_based_on_location',
                args: {
                    location: frm.doc.location,
                },
                callback: function(response){
                    if (response.message){
                        console.log(response.message)
                        var Section = response.message
                        frm.set_query('section', () => {
                            return {
                                filters: {
                                    section: ['in', Section]
                                }
                            }
                        })
                    }
                }
            })
        } else {
            frm.set_value('section', '');
            frm.set_value('work_center', '');
        }
    },
    section: function(frm){
        if (frm.doc.section){
            frm.set_value('work_center','')
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_work_center_based_on_section',
                args: {
                    section: frm.doc.section,
                },
                callback: function(response){
                    if (response.message){
                        console.log(response.message)
                        var WorkCenter = response.message
                        frm.set_query('work_center', () => {
                            return {
                                filters: {
                                    work_center: ['in', WorkCenter]
                                }
                            }
                        })
                    }
                }
            })
        } else {
            frm.set_value('work_center','')
        }
    },
    onload: function(frm) { 

        frm.get_field('equipment_task_details').grid.cannot_add_rows = true;
        frm.get_field('equipment_material_moment').grid.cannot_add_rows = true;
},
refresh: function(frm) {
    if (!frm.is_new() && frappe.user.has_role('System Manager')) {
        frm.add_custom_button(__('Activity Group'), function() {
            frappe.new_doc('Activity Group');
        }, __("Create"));
    }
}, 
activity_group_active: function(frm) {
    if (!frm.doc.activity_group_active) {  // Check if activity_group_active is unchecked (false)
        frm.set_value('activity_group', '');  // Clear activity_group field
        }
    },
//task will delete when equipment is on scrap
on_scrap:function(frm) {
    if(frm.doc.on_scrap){
        frm.set_value('activity_group_active',0);
        frm.set_df_property('activity_group', 'read_only', 1)
    }
}
    
});

// frappe.ui.form.on('Equipment', {
//     validate(frm) {
//         let error_rows = [];

//         (frm.doc.equipment_barcode || []).forEach(row => {
//             if (row.barcode_type === 'EAN') {
//                 let barcode_value = row.barcode ? row.barcode.trim() : "";
//                 if (!/^\d{13}$/.test(barcode_value)) {
//                     error_rows.push(`Row ${row.idx}: Invalid barcode ➝ "${row.barcode}"`);
//                 }
//             }
//         });

//         if (error_rows.length > 0) {
//             frappe.throw(`
//                 ${error_rows.join("<br>")}
//                 <br><br>Please enter 13-digit numeric barcode(s).
//             `);
//         }
//     }
// });


frappe.ui.form.on('Equipment', {
    refresh: function(frm) {
        setTimeout(() => {
            set_field_visibility(frm);
        }, 500);
    },
    
    onload: function(frm) {
        setTimeout(() => {
            set_field_visibility(frm);
        }, 500);
    }
});

function set_field_visibility(frm) {
    let is_maintenance_manager = frappe.user_roles.includes('Maintenance Manager');
    let is_process_manager = frappe.user_roles.includes('Process Manager');
    let is_maintenance_user = frappe.user_roles.includes('Maintenance User');
    
    console.log('User Roles:', frappe.user_roles);
    console.log('Is Maintenance Manager:', is_maintenance_manager);
    console.log('Is Process Manager:', is_process_manager);
    console.log('Is Maintenance User:', is_maintenance_user);
    
    if (is_maintenance_user && !is_maintenance_manager && !is_process_manager) {
        let visible_fields = [
            'equipment_group',
            'plant',
            'location',
            'section',
            'sub_section',
            'work_center',
            'equipment_name',
            'description'
        ];
        
        let tabs_to_hide = [
            'damage_and_causes_tab',
            'guarantee_tab',
            'warranty_tab',
            'history_tab'
        ];
        
        Object.keys(frm.fields_dict).forEach(function(fieldname) {
            let field = frm.fields_dict[fieldname];
            
            if (field && field.df) {
                let should_show = visible_fields.includes(fieldname);
                let is_tab_to_hide = tabs_to_hide.includes(fieldname);
                
                if (should_show) {
                    frm.set_df_property(fieldname, 'hidden', 0);
                } else if (is_tab_to_hide) {
                    frm.set_df_property(fieldname, 'hidden', 1);
                } else if (field.df.fieldtype !== 'Tab Break' && 
                           field.df.fieldtype !== 'Section Break' && 
                           field.df.fieldtype !== 'Column Break') {
                    frm.set_df_property(fieldname, 'hidden', 1);
                }
            }
        });
        
        let sections_to_show = ['plant_tab', 'plant_details_section', 'item_details_section'];
        sections_to_show.forEach(function(sec) {
            if (frm.fields_dict[sec]) {
                frm.set_df_property(sec, 'hidden', 0);
            }
        });
        
        tabs_to_hide.forEach(function(tab) {
            if (frm.fields_dict[tab]) {
                frm.set_df_property(tab, 'hidden', 1);
            }
        });
        
        frm.refresh_fields();
        
    } else if (is_maintenance_manager || is_process_manager) {
        Object.keys(frm.fields_dict).forEach(function(fieldname) {
            if (frm.fields_dict[fieldname]) {
                frm.set_df_property(fieldname, 'hidden', 0);
            }
        });
        
        frm.refresh_fields();
    }
}