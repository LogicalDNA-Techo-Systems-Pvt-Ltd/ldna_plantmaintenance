// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Generate Tasks", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Generate Tasks', {
    refresh: function (frm) {
        if (!frm.custom_buttons_created) {
            const buttonContainer = $('<div class="custom-button-container"></div>').appendTo(frm.fields_dict['button_container'].wrapper);

            $('<button id="load-tasks-btn" class="btn btn-primary" style="margin-right: 10px;">Load Tasks</button>').appendTo(buttonContainer).click(function () {
                load_tasks(frm);
            });

            frm.custom_buttons_created = true;
            frm.disable_save(); 

            $(".grid-add-row").hide();
            frm.fields_dict['task_allocation_details'].grid.wrapper.find('.grid-add-row').hide();
        }

        $(frm.page.sidebar).hide();
        $(frm.page.wrapper).find('.page-title .sidebar-toggle-btn').css('display', 'none');

        frm.page.wrapper.find('.page-actions .btn-primary.primary-action[data-label="Save"]').hide(); 

        // Hide the "Not Saved" indicator 
        frm.page.wrapper.find('.indicator-pill:contains("Not Saved")').hide(); 
        frm.page.wrapper.find('span:contains("Not Saved")').hide(); 

        frm.page.wrapper.find('.indicator-pill:contains("Not Saved")').hide(); 
        frm.page.wrapper.find('span:contains("Not Saved")').hide(); 

        // Additional selectors to target the exact elements
        frm.page.wrapper.find('.indicator-pill.orange:contains("Not Saved")').hide();
        frm.page.wrapper.find('.form-message').hide();

        frm.disable_save();
	    frm.saving = false;

    },
    
    plant: function (frm) {
        if (frm.doc.plant) {
            frm.set_value('location', '');
            frm.set_value('functional_location', '');
            frm.set_value('plant_section', '');
            frm.set_value('work_center', '');
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_location_list_based_on_plant',
                args: {
                    plant: frm.doc.plant
                },
                callback: function (response) {
                    if (response.message) {
                        console.log(response.message);
                        var Location = response.message;
                        frm.set_query('location', () => {
                            return {
                                filters: {
                                    name: ['in', Location]
                                }
                            };
                        });
                    }
                }
            });
        } else {
            frm.set_value('location', '');
            frm.set_value('functional_location', '');
            frm.set_value('plant_section', '');
            frm.set_value('work_center', '');
        }
    },
    location: function (frm) {
        if (frm.doc.location) {
            frm.set_value('functional_location', '');
            frm.set_value('plant_section', '');
            frm.set_value('work_center', '');
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_functional_location_list_based_on_location',
                args: {
                    location: frm.doc.location
                },
                callback: function (response) {
                    if (response.message) {
                        console.log(response.message);
                        var FunctionalLocation = response.message;
                        frm.set_query('functional_location', () => {
                            return {
                                filters: {
                                    name: ['in', FunctionalLocation]
                                }
                            };
                        });
                    }
                }
            });
        } else {
            frm.set_value('functional_location', '');
            frm.set_value('plant_section', '');
            frm.set_value('work_center', '');
        }
    },
    functional_location: function (frm) {
        if (frm.doc.functional_location) {
            frm.set_value('plant_section', '');
            frm.set_value('work_center', '');
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_section_based_on_func_location',
                args: {
                    func_loc: frm.doc.functional_location
                },
                callback: function (response) {
                    if (response.message) {
                        var Section = response.message;
                        console.log(Section);
                        frm.set_query('plant_section', () => {
                            return {
                                filters: {
                                    name: ['in', Section]
                                }
                            };
                        });
                    }
                }
            });
        } else {
            frm.set_value('plant_section', '');
            frm.set_value('work_center', '');
        }
    },
    plant_section: function (frm) {
        if (frm.doc.plant_section) {
            frm.set_value('work_center', '');
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_work_center_based_on_section',
                args: {
                    section: frm.doc.plant_section
                },
                callback: function (response) {
                    if (response.message) {
                        console.log(response.message);
                        var WorkCenter = response.message;
                        frm.set_query('work_center', () => {
                            return {
                                filters: {
                                    name: ['in', WorkCenter]
                                }
                            };
                        });
                    }
                }
            });
        } else {
            frm.set_value('work_center', '');
        }
    }
});

function load_tasks(frm) {
    if (!frm.doc.plant || !frm.doc.location || !frm.doc.functional_location || 
        !frm.doc.plant_section || !frm.doc.work_center) {
        frappe.msgprint(__('Please fill all the required fields (Plant, Location, Functional Location, Plant Section, Work Center) before loading tasks.'));
        return;
    }

    frappe.call({
        method: 'plantmaintenance.plantmaintenance.doctype.generate_tasks.generate_tasks.load_tasks',
        args: {
            plant: frm.doc.plant,
            location: frm.doc.location,
            functional_location: frm.doc.functional_location,
            plant_section: frm.doc.plant_section,
            work_center: frm.doc.work_center,
            start_date: frm.doc.start_date,
            end_date: frm.doc.end_date
        },
        callback: function (response) {
            if (response.message) {
                var tasks = response.message;
                frm.clear_table('task_allocation_details');
                response.message.sort(function (a, b) {
                    return new Date(a.date) - new Date(b.date);
                });
                $.each(tasks, function (index, task) {
                    var child = frm.add_child('task_allocation_details');
                    frappe.model.set_value(child.doctype, child.name, 'equipment_code', task.equipment_code);
                    frappe.model.set_value(child.doctype, child.name, 'equipment_name', task.equipment_name);
                    frappe.model.set_value(child.doctype, child.name, 'activity_group', task.activity_group);
                    frappe.model.set_value(child.doctype, child.name, 'activity', task.activity);
                    frappe.model.set_value(child.doctype, child.name, 'parameter', task.parameter);
                    frappe.model.set_value(child.doctype, child.name, 'frequency', task.frequency);
                    frappe.model.set_value(child.doctype, child.name, 'date', task.date);
                    frappe.model.set_value(child.doctype, child.name, 'day', task.day);
                    frappe.model.set_value(child.doctype, child.name, 'unique_key', task.unique_key);
                });
                frm.refresh_field('task_allocation_details');
                frm.toggle_display('task_allocation_details', true);

            }
        }
    });
}
