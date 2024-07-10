frappe.ui.form.on('Task Allocation', {
    refresh: function (frm) {
        if (!frm.custom_buttons_created) {
            const buttonContainer = $('<div class="custom-button-container"></div>').appendTo(frm.fields_dict['button_container'].wrapper);

            $('<button class="btn btn-primary" style="margin-right: 10px;">Load Tasks</button>').appendTo(buttonContainer).click(function () {
                load_tasks(frm);
            });

            $('<button class="btn btn-primary" style="margin-right: 10px;">Download Tasks Excel</button>').appendTo(buttonContainer).click(function () {
                download_tasks_excel(frm.doc.task_allocation_details);
            });

            $('<button class="btn btn-primary" style="margin-right: 10px;">Upload Assignment Excel</button>').appendTo(buttonContainer).click(function () {
                upload_assignment_excel(frm);
            });

            frm.custom_buttons_created = true;
        }
    },

    plant: function (frm) {
        if (frm.doc.plant) {
            frm.set_value('location', '');
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
        }
    },
    location: function (frm) {
        if (frm.doc.location) {
            frm.set_value('functional_location', '');
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
        }
    },
    functional_location: function (frm) {
        if (frm.doc.functional_location) {
            frm.set_value('plant_section', '');
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
        }
    }

});


function load_tasks(frm) {
    frappe.call({
        method: 'plantmaintenance.plantmaintenance.doctype.task_allocation.task_allocation.load_tasks',
        args: {
            plant: frm.doc.plant,
            location: frm.doc.location,
            functional_location: frm.doc.functional_location,
            plant_section: frm.doc.plant_section,
            work_center: frm.doc.work_center,
            end_date: frm.doc.end_date
        },
        callback: function (r) {
            if (r.message) {
                frm.clear_table('task_allocation_details');

                r.message.sort(function (a, b) {
                    return new Date(a.date) - new Date(b.date);
                });
                r.message.forEach(function (task) {
                    var row = frm.add_child('task_allocation_details');
                    row.equipment_code = task.equipment_code;
                    row.equipment_name = task.equipment_name;
                    row.activity = task.activity;
                    row.parameter = task.parameter;
                    row.frequency = task.frequency;
                    row.date = task.date;
                    row.day = task.day;
                    row.unique_key = task.unique_key;
                });
                frm.refresh_field('task_allocation_details');
            }
        }
    });
}

function download_tasks_excel(tasks) {
    frappe.call({
        method: 'plantmaintenance.plantmaintenance.doctype.task_allocation.task_allocation.download_tasks_excel_for_task_allocation',
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
            method: 'plantmaintenance.plantmaintenance.doctype.task_allocation.task_allocation.upload_tasks_excel_for_task_allocation',
            args: {
                file: values.xlsx_file,
                task_allocation_name: frm.doc.name
            },
            callback: (response) => {
                if (response.message) {
                    frappe.show_alert({
                        message: 'Excel import successful!',
                        indicator: 'green'
                    });
                    frm.reload_doc();
                }
                // else {
                //     frappe.msgprint(__('Failed to import Excel.'));
                // }
            }
        });
    }, __('Upload XLSX File'));

}





//Pragati Dike//
frappe.ui.form.on("Task Allocation Details", {
    add_assignee: function (frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        let selectedAssigne = child.assign_to ? child.assign_to.split(', ') : [];
        frappe.prompt(
            [
                {
                    label: __("First Name"),
                    fieldname: "first_name",
                    fieldtype: "Link",
                    options: "User",
                    get_query: function () {
                        return {
                            filters: [
                            ]
                        };
                    }
                }
            ],
            function (values) {
                let newassigne = values['first_name'];
                if (selectedAssigne.includes(newassigne)) {
                    frappe.msgprint(__("User already selected."));
                } else {
                    selectedAssigne.push(newassigne);
                    updateUser();
                }
            },
            __("Select User")
        );
        function updateUser() {
            let userList = selectedAssigne.join(', ');
            frappe.model.set_value(child.doctype, child.name, "assign_to", userList);
        }
    }
});





