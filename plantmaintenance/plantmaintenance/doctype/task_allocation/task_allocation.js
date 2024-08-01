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
            $(".grid-add-row").hide();

        }
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
                    frappe.model.set_value(child.doctype, child.name, 'activity', task.activity);
                    frappe.model.set_value(child.doctype, child.name, 'parameter', task.parameter);
                    frappe.model.set_value(child.doctype, child.name, 'frequency', task.frequency);
                    frappe.model.set_value(child.doctype, child.name, 'date', task.date);
                    frappe.model.set_value(child.doctype, child.name, 'day', task.day);
                    frappe.model.set_value(child.doctype, child.name, 'unique_key', task.unique_key);
                });
                frm.refresh_field('task_allocation_details');
            }
        }
    });
}


function download_tasks_excel(tasks) { // This code is to download the excel file of task allocation detail ct for bulk assignment of task. PD
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
 
 
 
 
 function upload_assignment_excel(frm) { // This code is to upload the excel file in task allocation doctype for bulk assignment of task. PD
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
                } else {
                    frappe.msgprint(__('Failed to import Excel.'));
                }
            }
        });
    }, __('Upload XLSX File'));
    $(".grid-add-row").hide();
 
 }
 
 
 
 
 


// frappe.ui.form.on("Task Allocation Details", {
//     add_assignee: function (frm, cdt, cdn) {
//         var child = locals[cdt][cdn];
//         let selectedAssigne = child.assign_to ? child.assign_to.split(', ') : [];
//         frappe.prompt(
//             [
//                 {
//                     label: __("User Name"),
//                     fieldname: "user_name",
//                     fieldtype: "Link",
//                     options: "User",
//                     get_query: function () {
//                         return {
//                             filters: [
//                             ]
//                         };
//                     }
//                 }
//             ],
//             function (values) {
//                 let newassigne = values['first_name'];
//                 if (selectedAssigne.includes(newassigne)) {
//                     frappe.msgprint(__("User already selected."));
//                 } else {
//                     selectedAssigne.push(newassigne);
//                     updateUser();
//                 }
//             },
//             __("Select User")
//         );
//         function updateUser() {
//             let userList = selectedAssigne.join(', ');
//             frappe.model.set_value(child.doctype, child.name, "assign_to", userList);
//         }
//     }
// });


frappe.ui.form.on('Task Allocation Details', {  // this code is for mutiple assignee select user dialogue box which will allow to select multiple assignee at one time. PD
    add_assignee: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        let selectedAssignees = child.assign_to ? child.assign_to.split(',').map(a => a.trim()) : [];

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'User',
                fields: ['full_name'],
            },
            callback: function(response) {
                let options = response.message.map(user => user.full_name);

                frappe.prompt(
                    [
                        {
                            label: __("Select Users"),
                            fieldname: "users",
                            fieldtype: "MultiSelectList",
                            options: options,
                            reqd: 1
                        }
                    ],

                    function(values) {
                        let newAssignees = values['users'] || [];
                        let duplicates = newAssignees.filter(user => selectedAssignees.includes(user));
                        
                        if (duplicates.length > 0) {
                            frappe.msgprint(__("The following users are already selected: {0}", [duplicates.join(', ')]));
                        } else {
                            selectedAssignees = [...new Set([...selectedAssignees, ...newAssignees])];
                            updateAssignees();
                        }
                    },
                    __("Select Users")
                );
            }
        });

        function updateAssignees() {
            let userList = selectedAssignees.join(', ');
            // console.log(userList);
            frappe.model.set_value(child.doctype, child.name, "assign_to", userList);
            frm.refresh_field('task_allocation_details');
        }
    }
});


 