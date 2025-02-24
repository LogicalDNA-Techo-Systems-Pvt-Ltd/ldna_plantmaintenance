// Copyright (c) 2025, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["Task Detail Action Flow"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "task_detail",
            "label": __("Task ID"),
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Select",
            "options":"\nOpen\nIn Progress\nPending Approval\nRejected\nApproved\nCompleted\nCancelled\nOverdue",
            "width": 200,
        },
    ],
    "onload": function(report) {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "User",
                filters: { "name": frappe.session.user },
                fieldname: ["roles"]
            },
            callback: function(response) {
                if (response.message) {
                    let user_roles = frappe.user_roles;
                    
                    let is_maintenance_manager = user_roles.includes("Maintenance Manager");
                    let is_process_manager = user_roles.includes("Process Manager");
    
                    console.log("User Roles:", user_roles);
    
                    let dropdown_html = `
                        <div class="btn-group">
                            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                                Workflow Action
                            </button>
                            <div class="dropdown-menu">
                                ${is_maintenance_manager ? `<a class="dropdown-item approve-action" href="#"> Approve</a>
                                <a class="dropdown-item reject-action" href="#"> Reject</a>` : ""}
                                
                                ${is_process_manager ? `<a class="dropdown-item complete-action" href="#"> Complete</a>
                                <a class="dropdown-item cancel-action" href="#"> Cancel</a>` : ""}
                            </div>
                        </div>
                    `;
    
                    if (is_maintenance_manager || is_process_manager) {
                        $(report.page.wrapper).find(".page-actions").prepend(dropdown_html);
                    }
                }
            }
        });
        $(document).on("click", ".approve-action", function() {
            update_task_status("Approved");
        });
    
        $(document).on("click", ".reject-action", function() {
            update_task_status("Rejected");
        });
    
        $(document).on("click", ".complete-action", function() {
            update_task_status("Completed");
        });
    
        $(document).on("click", ".cancel-action", function() {
            update_task_status("Cancelled");
        });
    },    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.fieldname === "select_task") {
            let checked = data.select_task ? "checked" : "";
            value = `
                <div class="checkbox-container" data-task="${data.task_detail}" style="cursor: pointer; text-align: center;">
                    <input type="checkbox" class="select-task-checkbox hidden-checkbox" ${checked} style="display: none;">
                    <span class="custom-checkbox" style="display: inline-block; width: 20px; height: 20px; border: 2px solid #000; text-align: center; line-height: 18px; font-size: 16px;">
                        ${checked ? "✔" : ""}
                    </span>
                </div>
            `;
        }
        return value;
    }
};

$(document).on("click", ".checkbox-container", function() {
    let checkbox = $(this).find(".select-task-checkbox");
    let checkboxIcon = $(this).find(".custom-checkbox");

    let isChecked = !checkbox.prop("checked");
    checkbox.prop("checked", isChecked);
    checkboxIcon.html(isChecked ? "✔" : "");

    console.log("Checkbox clicked: ", checkbox.prop("checked"));
});

function update_task_status(status) {
    let selected_tasks = [];

    $(".select-task-checkbox:checked").each(function() {
        let task_id = $(this).closest(".checkbox-container").data("task");
        selected_tasks.push(task_id);
    });

    if (selected_tasks.length === 0) {
        frappe.msgprint(__("Please select at least one task."));
        return;
    }

    frappe.call({
        method: "plantmaintenance.plantmaintenance.report.task_detail_action_flow.task_detail_action_flow.update_task_status",
        args: {
            task_ids: selected_tasks,
            status: status
        },
        callback: function(response) {
            if (response.message === "success") {
                frappe.msgprint(__("Task status updated successfully."));
                frappe.query_report.refresh();
            } else {
                frappe.msgprint(__("Failed to update task status."));
            }
        }
    });
}
