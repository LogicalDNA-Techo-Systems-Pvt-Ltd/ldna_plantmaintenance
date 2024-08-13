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
            frm.set_value('functional_location', '');
            frm.set_value('section', '');
            frm.set_value('work_center', '');
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_functional_location_list_based_on_location',
                args: {
                    location: frm.doc.location,
                },
                callback: function(response){
                    if (response.message){
                        console.log(response.message)
                        var FunctionalLocation = response.message
                        frm.set_query('functional_location', () => {
                            return {
                                filters: {
                                    functional_location: ['in', FunctionalLocation]
                                }
                            }
                        })
                    }
                }
            })
        } else {
            frm.set_value('functional_location', '');
            frm.set_value('section', '');
            frm.set_value('work_center', '');
        }
    },
    functional_location: function(frm){
        if (frm.doc.functional_location){
            frm.set_value('section', '')
            frm.set_value('work_center', '')
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_section_based_on_func_location',
                args: {
                    func_loc: frm.doc.functional_location,
                },
                callback: function(response){
                    if (response.message){
                        var Section = response.message
                        console.log(Section)
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
            frm.set_value('section', '')
            frm.set_value('work_center', '')
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
    name: function(frm){
        if (!frm.doc.name1) {
            frm.set_value('location', '');
            frm.set_value('functional_location', '');
            frm.set_value('section', '');
            frm.set_value('work_center', '');
        }
    }, 
    onload: function(frm) { 

        frm.get_field('task_detail_ct').grid.cannot_add_rows = true;
        frm.get_field('material_moment_ct').grid.cannot_add_rows = true;
},
refresh: function(frm) {
    if (!frm.is_new() && frappe.user.has_role('System Manager')) {
        frm.add_custom_button(__('Activity Group'), function() {
            frappe.new_doc('Activity Group');
        }, __("Create"));
    }
    frm.set_query("activity_group", function() {
        return {
            filters: [
                ["is_active", "=", "1"]
            ]
        };
    });
},
 
//for deleting task in task detail when equipment is on scrap. 
 
validate: function(frm) {
            if (frm.doc.on_scrap) {
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Task Detail',
                        filters: {
                            'equipment_name': frm.doc.equipment_name,
                            'status': 'Open'
                        },
                        fields: ['name']
                    },
                    callback: function(response) {
                        var tasks = response.message;
                        if (tasks && tasks.length > 0) {
                            var task_names = tasks.map(task => task.name);
                            task_names.forEach(task_name => {
                                frappe.call({
                                    method: 'frappe.client.delete',
                                    args: {
                                        doctype: 'Task Detail',
                                        name: task_name
                                    },
                                    callback: function(delete_response) {
                                        if (delete_response.exc) {
                                            console.error(`Error deleting Task: ${task_name}`, delete_response.exc);
                                        } else {
                                            console.log(`Deleted Task: ${task_name}`);
                                        }
                                    }
                                });
                            });
                        }
                    }
                });
            }
        },

});

