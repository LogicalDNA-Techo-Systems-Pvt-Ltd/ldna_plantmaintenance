// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["Notification Report"] = {
	"filters": [
		{
            "fieldname":"from_date",
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
            "label": "Maintenance Type",
            "fieldname": "type",
            "fieldtype": "Select",
            "options": "\nPreventive\nBreakdown\nShutdown\nGeneral\nPredictive",
            "width": 200
        },
        {
            "label": "Equipment Group",
            "fieldname": "equipment_group",
            "fieldtype": "Link",
            "options": "Equipment  Group",
            "width": 150
        },
        {
            "label": __("Work Center"),
            "fieldname": "work_center",
            "fieldtype": "Link",
            "options": "Work Center",
            "width": 200
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Select",
            "options":"\nOpen\nIn Progress\nPending Approval\nRejected\nApproved\nCompleted\nCancelled\nOverdue",
            "width": 200,
           
        },
	]
};
