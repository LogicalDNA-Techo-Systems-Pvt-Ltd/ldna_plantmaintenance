frappe.ui.form.on('Task Allocation', {
    refresh: function(frm) {
        if (!frm.custom_buttons_created) {
            const buttonContainer = $('<div class="custom-button-container"></div>').appendTo(frm.fields_dict['button_container'].wrapper);

            $('<button class="btn btn-primary" style="margin-right: 10px;">Load Tasks</button>').appendTo(buttonContainer).click(function() {
                load_tasks(frm);
            });

            $('<button class="btn btn-primary" style="margin-right: 10px;">Download Tasks Excel</button>').appendTo(buttonContainer).click(function() {
                download_tasks_excel(frm.doc.task_allocation_details);
            });

            $('<button class="btn btn-primary" style="margin-right: 10px;">Upload Assignment Excel</button>').appendTo(buttonContainer).click(function() {
                upload_assignment_excel(frm);
            });

            frm.custom_buttons_created = true;
        }

        if (!frm.is_new()) {
            add_generate_task_button(frm);
        }
    },
    after_save: function(frm) {
        add_generate_task_button(frm);
        if (!frm.custom_buttons_created) {
            const buttonContainer = $('<div class="custom-button-container"></div>').appendTo(frm.fields_dict['button_container'].wrapper);

            $('<button class="btn btn-primary" style="margin-right: 10px;">Load Tasks</button>').appendTo(buttonContainer).click(function() {
                load_tasks(frm);
            });

            $('<button class="btn btn-primary" style="margin-right: 10px;">Download Tasks Excel</button>').appendTo(buttonContainer).click(function() {
                download_tasks_excel(frm.doc.task_allocation_details);
            });

            $('<button class="btn btn-primary" style="margin-right: 10px;">Upload Assignment Excel</button>').appendTo(buttonContainer).click(function() {
                upload_assignment_excel(frm);
            });

            frm.custom_buttons_created = true;
        }
    }
});

function load_tasks(frm) {
    if (!frm.doc.work_center || !frm.doc.plant_section) {
        frappe.msgprint(__('Please select Work Center and Plant Section before loading tasks.'));
        return;
    }

    frappe.call({
        method: 'plantmaintenance.plantmaintenance.doctype.task_allocation.task_allocation.load_tasks',
        args: {
            work_center: frm.doc.work_center,
            plant_section: frm.doc.plant_section
        },
        callback: function(response) {
            let tasks_to_add = response.message;
            if (tasks_to_add && tasks_to_add.length > 0) {
                let existing_tasks = frm.doc.task_allocation_details.map(d => {
                    return {
                        parameter: d.parameter,
                        date: d.date
                    };
                });

                tasks_to_add.forEach(task => {
                    let exists = existing_tasks.some(existing_task =>
                        existing_task.parameter === task.parameter &&
                        existing_task.date === task.date
                    );

                    if (!exists) {
                        let child = frm.add_child('task_allocation_details');
                        frappe.model.set_value(child.doctype, child.name, 'equipment_code', task.equipment_code);
                        frappe.model.set_value(child.doctype, child.name, 'equipment_name', task.equipment_name);
                        frappe.model.set_value(child.doctype, child.name, 'date', task.date);
                        frappe.model.set_value(child.doctype, child.name, 'frequency', task.frequency);
                        frappe.model.set_value(child.doctype, child.name, 'task_status', task.task_status);
                        frappe.model.set_value(child.doctype, child.name, 'activity', task.activity_name);
                        frappe.model.set_value(child.doctype, child.name, 'parameter', task.parameter);
                        frappe.model.set_value(child.doctype, child.name, 'day', task.day);
                    }
                });

                frm.refresh_field('task_allocation_details');
                frappe.msgprint(__('Tasks have been loaded successfully.'));
            } else {
                frappe.msgprint(__('No tasks found for the selected criteria.'));
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
        callback: function(response) {
            const file_url = response.message;
            if (file_url) {
                window.open(file_url);
            } else {
                frappe.msgprint(__('Failed to generate download link.'));
            }
        },
        error: function(xhr, textStatus, error) {
            frappe.msgprint(__('Failed to download tasks: {0}', [error]));
        }
    });
}
function add_generate_task_button(frm) {
    frm.remove_custom_button(__('Generate Task'));

    frm.add_custom_button(__('Generate Task'), function() {
        frappe.call({
            method: "plantmaintenance.plantmaintenance.doctype.task_allocation.task_allocation.check_tasks_generated",
            args: {
                docname: frm.doc.name
            },
            callback: function(response) {
                if (response.message) {
                    frappe.msgprint(__('Tasks have been generated successfully.'));
                } else {
                    generate_tasks(frm);
                }
            },
            error: function(err) {
                console.log(err);
                frappe.msgprint(__('An error occurred while checking tasks.'));
            }
        });
    }).css({
        'background-color': 'black',
        'color': 'white'
    });
}

function generate_tasks(frm) {
    frappe.call({
        method: "plantmaintenance.plantmaintenance.doctype.task_allocation.task_allocation.generate_tasks",
        args: {
            docname: frm.doc.name
        },
        callback: function(response) {
            if (response.message) {
                frappe.msgprint(response.message);
                frm.reload_doc();
            }
        },
        error: function(err) {
            console.log(err);
            frappe.msgprint(__('An error occurred while generating tasks.'));
        }
    });
}