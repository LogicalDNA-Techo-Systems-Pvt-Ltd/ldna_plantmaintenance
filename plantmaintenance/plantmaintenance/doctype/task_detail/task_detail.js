// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Task Detail', {
    refresh: function (frm) {
        frappe.db.get_single_value('Settings', 'back_days_entry').then(back_days_entry => {
            if (back_days_entry) {
                let start_date = frm.doc.plan_start_date;

                if (start_date) {
                    let critical_date = frappe.datetime.add_days(start_date, back_days_entry);
                    let today = frappe.datetime.now_date();

                    if (critical_date < today) {
                        frm.disable_save();
                        let fields = [
                            'type', 'work_permit_number', 'work_center', 'equipment_code',
                            'status', 'equipment_name', 'approver', 'assigned_to',
                            'add_assignee', 'activity', 'parameter', 'parameter_type',
                            'actual_value', 'parameter_dropdown', 'reading_1', 'reading_2',
                            'reading_3', 'reading_4', 'reading_5', 'reading_6',
                            'reading_7', 'reading_8', 'reading_9', 'reading_10',
                            'damage', 'cause', 'remark', 'breakdown_reason',
                            'service_call', 'material_issued', 'material_returned', 'attachment'
                        ];

                        fields.forEach(fieldname => {
                            frm.fields_dict[fieldname].df.read_only = 1;
                            frm.refresh_field(fieldname);
                        });
                    }
                }
            }
        });

        let material_issued = frm.fields_dict.material_issued;
        let user = frappe.session.user;
        let manager_email = frm.doc.approver;

        if (user === manager_email) {
            $('.update-qty-btn').hide();
            $('.send-for-approval-btn').hide();
            if (!frm.approved_button_added) {
    
                frm.approved_button_added = true;
                let approvedButton = $('<button class="btn btn-primary btn-xs approved-btn" style="margin-top: -10px; margin-left: 92%;">Approve</button>');
                approvedButton.on('click', function () {
                    frappe.call({
                        method: "plantmaintenance.plantmaintenance.doctype.task_detail.task_detail.mark_as_issued",
                        args: { docname: frm.doc.name },
                        callback: function (response) {
                            if (response.message) {
                                frm.doc.material_issued.forEach(item => {
                                    if (item.status === 'Pending Approval') {
                                        item.status = 'Material Issued';
                                    }
                                });
                                frm.refresh_field('material_issued');
                            }
                        }
                    });
                });
                material_issued.grid.wrapper.find('.grid-footer').append(approvedButton);
            }
            material_issued.grid.data.forEach((row, idx) => {
                if (row.shortage > 0 || row.consumable || !row.spare) {
                    frm.fields_dict.material_issued.grid.grid_rows[idx].wrapper.hide();
                }
            });
            material_issued.grid.wrapper.find('.grid-add-row').hide();
            $(".form-assignments").hide(); // for hiding assign to in sidebar
        } else {
            if (!frm.inventory_button_added) {
                frm.inventory_button_added = true;

                let button = $('<button class="btn btn-primary btn-xs update-qty-btn" style="margin-top: -40px; margin-left: 72%;">Update Quantity</button>');
                let button1 = $('<button class="btn btn-primary btn-xs send-for-approval-btn" style="margin-top: -80px; margin-left: 87%;">Send for Approval</button>');

                button1.on('click', function () {
                    let new_rows_for_approval = [];
                    let message = '';

                    frm.doc.material_issued.forEach((item, index) => {
                        if (item.status === 'Material Issued') {
                            // Skip materials that are already issued
                            return;
                        } else if (item.shortage > 0) {
                            message = `Cannot send for approval due to existing shortage`;
                        } else if (!item.spare) {
                            message = __('Cannot send for approval.');
                        } else if (item.shortage != 0) {
                            message = __('Cannot send for approval.');
                        } else {
                            if (item.spare && item.shortage === 0) {
                                new_rows_for_approval.push(item);
                            }
                        }
                    });

                    if (new_rows_for_approval.length > 0) {
                        frappe.call({
                            method: "plantmaintenance.plantmaintenance.doctype.task_detail.task_detail.send_for_approval",
                            args: { docname: frm.doc.name },
                            callback: function (response) {
                                if (response.message) {
                                    new_rows_for_approval.forEach(item => {
                                        frappe.msgprint('Email sent to Manager for material approval.');
                                        item.status = 'Pending Approval';
                                        item.approval_date = frappe.datetime.nowdate();
                                    });

                                    frm.refresh_field('material_issued');
                                }
                            }
                        });
                    } else if (message) {
                        frappe.msgprint(message);
                    }
                });

                material_issued.grid.wrapper.find('.grid-footer').append(button);
                material_issued.grid.wrapper.find('.grid-footer').append(button1);
            }
        }

        set_existing_rows_read_only(frm);
        toggle_result_field(frm);
        toggle_add_assignee_button(frm);

    },

    readings: function (frm) {
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

    onload: function (frm) {
        frm.trigger('readings');

        // Fetch parameter details if parameter field is set
        if (frm.doc.parameter) {
            fetch_parameter_details(frm);
        };
        set_existing_rows_read_only(frm);
    },

    parameter: function (frm) {
        // Fetch parameter details whenever parameter field changes
        fetch_parameter_details(frm);
    },

    type: function (frm) {
        if (frm.doc.type === 'Breakdown') {
            frm.set_value('parameter_type', '');
        }
    },

    validate: function (frm) {
        if (frm.doc.actual_end_date < frm.doc.actual_start_date) {
            frappe.msgprint(__('Actual End Date should be greater than or equal to Actual Start Date'));
            frappe.validated = false;
        };
        set_existing_rows_read_only(frm);
    },

    before_save: function (frm) {
        const fields = ['reading_1', 'reading_2', 'reading_3', 'reading_4', 'reading_5',
            'reading_6', 'reading_7', 'reading_8', 'reading_9', 'reading_10'];

        let readingsCount = frm.doc.readings;
        let hasValidationErrors = false;

        if (frm.doc.parameter_type === 'Numeric') {
            let minRange = frm.doc.minimum_value;
            let maxRange = frm.doc.maximum_value;

            for (let i = 0; i < readingsCount; i++) {
                let field = fields[i];
                let numericValue = frm.doc[field];
                if (numericValue < minRange || numericValue > maxRange) {
                    hasValidationErrors = true;
                }
            }
        }
        if (hasValidationErrors) {
            frm.doc.result = 'Fail';
        } else {
            frm.doc.result = 'Pass';
        };
        frm.fields_dict.material_issued.grid.data.forEach(row => {
            consumable_fields(frm, row.doctype, row.name, row.consumable);
        });
    },

    attachment: function (frm) {
        toggle_result_field(frm);
    },

    add_assignee: function (frm) {
        toggle_add_assignee_button(frm);
    }
});

frappe.ui.form.on('Material Issue', {
    available_quantity: function (frm, cdt, cdn) {
        calculate_shortage(frm, cdt, cdn);
    },
    required_quantity: function (frm, cdt, cdn) {
        calculate_shortage(frm, cdt, cdn);
    },
    consumable: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        consumable_fields(frm, cdt, cdn, row.consumable);
    },
    material_issued_add: function (frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'is_new_entry', 1);
        set_new_row_editable(frm, cdt, cdn);
    }
});

function calculate_shortage(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.available_quantity >= row.required_quantity) {
        row.shortage = 0;
    } else {
        row.shortage = row.required_quantity - row.available_quantity;
    }
    if (isNaN(row.shortage)) {
        row.shortage = '';
    }
    if (row.shortage > 0 && row.status === 'Pending Approval' || row.shortage > 0 && row.status === 'Material Issued' || row.shortage === 0 && row.status == "Material Issued") {
        row.status = '';
    }

    frm.refresh_field('material_issued');

}


function fetch_parameter_details(frm) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Parameter",
            name: frm.doc.parameter
        },
        callback: function (r) {
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

function consumable_fields(frm, cdt, cdn, is_consumable) {
    let row = locals[cdt][cdn];
    if (is_consumable) {
        frappe.model.set_value(cdt, cdn, 'status', 'Material Issued');
        if (row.is_new_entry) {
            frm.fields_dict['material_issued'].grid.toggle_enable('required_quantity', true, cdn);
        }
        else {
            frm.fields_dict['material_issued'].grid.toggle_enable('available_quantity', false, cdn);
        }
        frm.fields_dict['material_issued'].grid.toggle_enable('available_quantity', false, cdn);
    }
    else {
        frm.fields_dict['material_issued'].grid.toggle_enable('available_quantity', true, cdn);
        frm.fields_dict['material_issued'].grid.toggle_enable('required_quantity', true, cdn);
    }
    frm.refresh_field('material_issued');
}

function set_existing_rows_read_only(frm) {
    frm.fields_dict['material_issued'].grid.get_data().forEach(row => {
        if (!row.is_new_entry && (row.status === 'Material Issued' || row.status === 'Pending Approval' || row.status === '')) {
            console.log(row.name);
            frm.fields_dict['material_issued'].grid.toggle_enable('material_code', false, row.name);
            frm.fields_dict['material_issued'].grid.toggle_enable('material_name', false, row.name);
            frm.fields_dict['material_issued'].grid.toggle_enable('available_quantity', false, row.name);
            frm.fields_dict['material_issued'].grid.toggle_enable('required_quantity', false, row.name);
            frm.fields_dict['material_issued'].grid.toggle_enable('approval_date', false, row.name);
            frm.fields_dict['material_issued'].grid.toggle_enable('issued_date', false, row.name);
        }
    });
    frm.refresh_field('material_issued');
}

function set_new_row_editable(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    frm.fields_dict['material_issued'].grid.toggle_enable('material_code', true, row.name);
}

function toggle_result_field(frm) {
    if (frm.doc.attachment && frm.doc.attachment.length > 0) {
        frm.set_df_property('result', 'hidden', 0);
    } else {
        frm.set_df_property('result', 'hidden', 1);
    }
}

function toggle_add_assignee_button(frm) {
  
    if (!frm.doc.assigned_to) {
        frm.set_df_property('add_assignee', 'hidden', 0);
    } else {
        frm.set_df_property('add_assignee', 'hidden', 1);
    }
}




frappe.ui.form.on('Task Detail', {
    add_assignee: function (frm) {
        let selectedAssignees = frm.doc.assigned_to ? frm.doc.assigned_to.split(',').map(a => a.trim()).filter(Boolean) : [];

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
            callback: function (response) {
                let options = response.message.map(user => user.full_name).filter(Boolean); // Ensure no empty values

                frappe.prompt(
                    [
                        {
                            label: __("Select Users"),
                            fieldname: "users",
                            fieldtype: "MultiSelectList",
                            options: options,
                            reqd: 1,
                            get_data: function () {
                                return response.message.map(user => {
                                    return { value: user.full_name, description: "" };
                                });
                            }
                        }
                    ],
                    function (values) {
                        let newAssignees = values['users'] || [];
                        let duplicates = newAssignees.filter(user => selectedAssignees.includes(user));

                        if (duplicates.length > 0) {
                            frappe.msgprint(__("The following users are already selected: {0}.", [duplicates.join(', ')]));
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
            frm.set_value("assigned_to", userList);
            frm.refresh_field('assigned_to');
        }
    }
});
