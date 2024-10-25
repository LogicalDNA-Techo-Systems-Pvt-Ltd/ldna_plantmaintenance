frappe.ui.form.on('Allocation', {
    refresh: function (frm) {
        if (!frm.custom_buttons_created) {
            const buttonContainer = $('<div class="custom-button-container"></div>').appendTo(frm.fields_dict['button_container'].wrapper);

            $('<button id="load-tasks-btn" class="btn btn-primary" style="margin-right: 10px;">Load Tasks</button>').appendTo(buttonContainer).click(function () {
                load_tasks(frm);
            });

            $('<button id="download-tasks-excel-btn" class="btn btn-primary" style="margin-right: 10px;">Download Tasks Excel</button>').appendTo(buttonContainer).click(function () {
                download_tasks_excel(frm.doc.task_allocation_details);
            });

            $('<button id="upload-assignment-excel-btn" class="btn btn-primary" style="margin-right: 10px;">Upload Assignment Excel</button>').appendTo(buttonContainer).click(function () {
                upload_assignment_excel(frm);
            });

            document.getElementById('download-tasks-excel-btn').style.display = 'none';
            document.getElementById('upload-assignment-excel-btn').style.display = 'none';

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
        method: 'plantmaintenance.plantmaintenance.doctype.allocation.allocation.load_tasks',
        args: {
            plant: frm.doc.plant,
            location: frm.doc.location,
            functional_location: frm.doc.functional_location,
            plant_section: frm.doc.plant_section,
            work_center: frm.doc.work_center,
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

                document.getElementById('download-tasks-excel-btn').style.display = 'inline-block';
                document.getElementById('upload-assignment-excel-btn').style.display = 'inline-block';
            }
        }
    });
}

function download_tasks_excel(tasks) {
    frappe.call({
        method: 'plantmaintenance.plantmaintenance.doctype.allocation.allocation.download_tasks_excel_for_allocation',
        args: {
            tasks: JSON.stringify(tasks)
        },
        callback: function (response) {
            const file_url = response.message;
            if (file_url) {
                window.open(file_url);
            } else {
                frappe.msgprint(__('Failed to generate download link.'));
            }
        },
        error: function (xhr, textStatus, error) {
            frappe.msgprint(__('Failed to download tasks: {0}', [error]));
        }
    });
}


frappe.ui.form.on("Task Allocation Details", {
    assign_to: function (frm, cdt, cdn) {
        const child = locals[cdt][cdn];

        if (child.assign_to) {
            frappe.call({
                method: "plantmaintenance.plantmaintenance.doctype.task_detail.task_detail.update_task_detail",
                args: {
                    equipment_code: child.equipment_code,
                    activity: child.activity,
                    assign_to: child.assign_to,
                    parameter:child.parameter,
                    date: child.date 
                },
                
                callback: function (r) {
                    if (r.message) {
                        // frappe.msgprint(__('Task Detail updated successfully'));
                        console.log("successfully uploaded excel")
                    } else {
                        frappe.msgprint(__('Error updating Task Detail'));
                    }
                }
            });
        }
    }
});


function upload_assignment_excel(frm) {
    frappe.prompt([
        {
            label: __('Select XLSX File'),
            fieldname: 'xlsx_file',
            fieldtype: 'Attach',
            reqd: 1
        }
    ], (values) => {
        frappe.call({
            method: 'plantmaintenance.plantmaintenance.doctype.allocation.allocation.upload_tasks_excel_for_allocation',
            args: {
                file: values.xlsx_file,
                allocation_name: frm.doc.name
            },
            callback: (response) => {
                if (response.message) {
                    frappe.show_alert({
                        message: 'Excel import successful!',
                        indicator: 'green'
                    });

                    frm.clear_table('task_allocation_details');

                    response.message.allocation_details.forEach(detail => {
                        let child = frm.add_child('task_allocation_details');
                        frappe.model.set_value(child.doctype, child.name, 'equipment_code', detail.equipment_code);
                        frappe.model.set_value(child.doctype, child.name, 'equipment_name', detail.equipment_name);
                        frappe.model.set_value(child.doctype, child.name, 'activity_group', detail.activity_group);
                        frappe.model.set_value(child.doctype, child.name, 'activity', detail.activity);
                        frappe.model.set_value(child.doctype, child.name, 'parameter', detail.parameter);
                        frappe.model.set_value(child.doctype, child.name, 'frequency', detail.frequency);
                        frappe.model.set_value(child.doctype, child.name, 'date', detail.date);
                        frappe.model.set_value(child.doctype, child.name, 'assign_to', detail.assign_to);
                        frappe.model.set_value(child.doctype, child.name, 'priority', detail.priority);
                        frappe.model.set_value(child.doctype, child.name, 'day', detail.day);
                        frappe.model.set_value(child.doctype, child.name, 'unique_key', detail.unique_key);
                    });

                    frm.refresh_field('task_allocation_details');
                    frm.toggle_display('task_allocation_details', true);
                } else {
                    frappe.msgprint(__('Failed to import Excel.'));
                }
            }
        });
    }, __('Upload XLSX File'));
}



frappe.ui.form.on('Task Allocation Details', {
    add_assignee: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        let selectedAssignees = child.assign_to ? child.assign_to.split(',').map(a => a.trim()).filter(Boolean) : [];

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'User',
                fields: ['full_name'],
                filters: [
                    ['User', 'enabled', '=', 1],
                    ['Has Role', 'role', '=', 'Maintenance User']
                ],
                limit_page_length: 0,
            },
            callback: function(response) {
                let options = response.message.map(user => user.full_name).filter(Boolean);
                const userCount = options.length;

                const dialog = new frappe.ui.Dialog({
                    title: __('Select Users'),
                    fields: [
                        {
                            label: __("Select Users"),
                            fieldtype: "MultiSelectList",
                            fieldname: "users",
                            options: options,
                            reqd: 1,
                            get_data: function () {
                                return response.message.map(user => ({
                                    value: user.full_name,
                                    description: ""
                                }));
                            }
                        }
                    ],
                    primary_action_label: __('Submit'),
                    primary_action: function(values) {
                        let newAssignees = values['users'] || [];
                        let duplicates = newAssignees.filter(user => selectedAssignees.includes(user));

                        if (duplicates.length > 0) {
                            frappe.msgprint(__("The following users are already selected: {0}.", [duplicates.join(', ')]));
                        } else {
                            selectedAssignees = [...new Set([...selectedAssignees, ...newAssignees])];
                            updateAssignees();
                        }

                        dialog.hide();
                        $('body').removeClass('modal-open');  
                    }
                });

                dialog.show();

                $('body').addClass('modal-open');

                let dynamicHeight = userCount * 100;
                if (userCount > 10) {
                    dynamicHeight = 300; 
                }
                dialog.$wrapper.find('.modal-body').css({
                    "overflow-y": "auto",
                    "height": dynamicHeight + "px", 
                    "max-height": "90vh"  
                });

                function updateAssignees() {
                    let userList = selectedAssignees.join(', ');
                    frappe.model.set_value(child.doctype, child.name, "assign_to", userList);
                    frm.refresh_field('task_allocation_details');
                }
            }
        });
    }
});

