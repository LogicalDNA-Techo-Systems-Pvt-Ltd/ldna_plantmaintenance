(function() {
    // Function to get role-based breadcrumbs
    function getRoleBreadcrumb() {
        const roleBreadcrumbs = {
            'Maintenance Manager': '/app/manager',
            'Maintenance User': '/app/maintenance-user',
            'System Manager': '/app/system-workspace',
            'Process Manager': '/app/manager'
        };
        const role = frappe.user_roles.find(r => roleBreadcrumbs[r]);
        return role ? `<a href="${roleBreadcrumbs[role]}">${role}</a>` : 
                       `<a href="/app/activity-group">Activity Group</a>`;
    }

    // Function to update breadcrumbs
    function updateBreadcrumbs(doctype, docname, isNew) {
        $(document).ready(function() {
            let breadcrumbs = $('#navbar-breadcrumbs').empty();
            let breadcrumbString = '';

            breadcrumbString += getRoleBreadcrumb();
            breadcrumbString += `  <a href="/app/${frappe.router.slug(doctype)}">${doctype}</a>`;

            if (isNew) {
                breadcrumbString += ` > New ${doctype}`;
            } else if (docname) {
                breadcrumbString += ` > ${__(docname)}`;
            }

            breadcrumbs.append(`<li class="breadcrumb-item">${breadcrumbString}</li>`);
        });
    }

    // Calendar view settings for "Task Detail"
    frappe.views.calendar["Task Detail"] = {
        field_map: {
            "start": "plan_start_date",
            "end": "plan_end_date",
            "title": "parameter",
            "frequency": "frequency",
            "allDay": "allDay"
        }
    };

    // Initialize list view settings for all doctypes
    const doctypes = ['Equipment', 'Activity Group', 'Activity', 'Parameter', 'Task Detail'];

    doctypes.forEach(doctype => {
        frappe.ui.form.on(doctype, {
            refresh: function(frm) {
                const isNew = frm.is_new();
                updateBreadcrumbs(doctype, frm.doc.name, isNew);
            }
        });

        frappe.listview_settings[doctype] = {
            refresh: function(listview) {
                setTimeout(function() {
                    $(".list-row-container .list-row").each(function (i, obj) {
                        var row = $(this);
                        var statusField = listview.data[i] ? listview.data[i].status : '';
                        if (statusField === 'Overdue') {
                            var workflowStateElement = row.find(".indicator-pill:eq(0)");
                            if (workflowStateElement.length) {
                                workflowStateElement.css({
                                    'background-color': 'red',
                                    'color': 'white'
                                });
                            }
                        }
                    });
                }, 1);

                // Hide 'Assign To' from sidebar for all doctypes
                setTimeout(function() {
                    $('a[data-fieldname="assigned_to"]').closest('li').hide();
                }, 0);

                updateBreadcrumbs(doctype, null, false);

                function toggleAssignToButton() {
                    let selectedItems = listview.get_checked_items();
                    let openTasks = selectedItems.filter(item => item.status === "Open");

                    if (openTasks.length > 0) {
                        listview.assignToButton.show();
                    } else {
                        listview.assignToButton.hide();
                    }
                }

                toggleAssignToButton();
            },

            onload: function(listview) {
                if (listview.doctype === 'Task Detail') {
                    let today = frappe.datetime.get_today();
                    listview.filter_area.add([[listview.doctype, 'plan_start_date', '=', today]]);

                    // Hide 'Assign To' field in the list view
                    var assigned_To = listview.$page.find(`[data-label='Assign%20To']`);
                    if (assigned_To.length) {
                        assigned_To.hide();
                        assigned_To.parent().hide();
                        assigned_To.parent().parent().hide();
                    }

                    // Add the 'Assign To' button
                    let assignToButton = listview.page.add_inner_button(__('Assign To'), function() {
                        let selectedItems = listview.get_checked_items();

                        if (selectedItems.length === 0) {
                            frappe.msgprint(__('Please select at least one task.'));
                            return;
                        }

                        // Filter tasks with status 'Open'
                        let openTasks = selectedItems.filter(item => item.status === "Open");

                        if (openTasks.length === 0) {
                            frappe.msgprint(__('No tasks in "Open" status selected.'));
                            return;
                        }

                        frappe.call({
                            method: 'frappe.client.get_list',
                            args: {
                                doctype: 'User',
                                fields: ['full_name'],
                                filters: [
                                    ['User', 'enabled', '=', 1],
                                    ['Has Role', 'role', '=', 'Maintenance User']
                                ],
                                limit_page_length: 0
                            },
                            callback: function(response) {
                                let options = response.message.map(user => user.full_name).filter(Boolean);

                                const dialog = new frappe.ui.Dialog({
                                    title: __('Select Users'),
                                    fields: [
                                        {
                                            label: __("Select Users"),
                                            fieldtype: "MultiSelectList",
                                            fieldname: "users",
                                            placeholder: "Add User",
                                            options: options,
                                            reqd: 1,
                                            get_data: function() {
                                                return response.message.map(user => ({
                                                    value: user.full_name,
                                                    description: ""
                                                }));
                                            }
                                        }
                                    ],
                                    primary_action_label: __('Submit'),
                                    primary_action: function(values) {
                                        let selectedAssignees = values['users'] || [];
                                        let taskNames = openTasks.map(item => item.name);

                                        // Call server-side method for bulk assignment
                                        frappe.call({
                                            method: 'plantmaintenance.plantmaintenance.doctype.task_detail.task_detail.bulk_assign_tasks',
                                            args: {
                                                task_names: taskNames,
                                                assigned_users: selectedAssignees
                                            },
                                            error: function(err) {
                                                frappe.msgprint(__('An error occurred while assigning tasks.'));
                                                console.error(err);
                                            },
                                            callback: function() {
                                                // Refresh the list to reflect changes
                                                listview.refresh();
                                            }
                                        });

                                        dialog.hide();
                                        $('body').removeClass('modal-open');
                                    }
                                });

                                dialog.show();
                                $('body').addClass('modal-open');

                                dialog.$wrapper.find('.modal-body').css({
                                    "overflow-y": "auto",
                                    "height": "16vh"
                                });
                            }
                        });
                    }).addClass("btn-primary").hide();

                    listview.assignToButton = assignToButton;

                    listview.$page.on('change', '.list-row-checkbox', function() {
                        toggleAssignToButton(); 
                    
                    });
                    listview.$page.on('change', 'input.list-check-all', function() {
                        toggleAssignToButton();
                    });

                    function toggleAssignToButton() {
                        let selectedItems = listview.get_checked_items();
                        let openTasks = selectedItems.filter(item => item.status === "Open");

                        if (openTasks.length > 0) {
                            assignToButton.show();
                        } else {
                            assignToButton.hide();
                        }
                    }

                    toggleAssignToButton();
                }
            }
        };
    });
})();

