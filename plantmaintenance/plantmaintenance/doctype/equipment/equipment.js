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
    if (!frm.is_new()) {
        frm.add_custom_button(__('Activity Group'), function() {
            frappe.new_doc('Activity Group');
        }, __("Create"));
    }
},
});





