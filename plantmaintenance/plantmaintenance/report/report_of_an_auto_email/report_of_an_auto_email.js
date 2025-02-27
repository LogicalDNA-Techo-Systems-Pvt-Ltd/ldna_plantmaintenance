// Copyright (c) 2025, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["Report of an Auto Email"] = {
	"filters": [
        {
            "fieldname": "future_date",
            "label": __("Future Date"),
            "fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), 1),
            "reqd": 1,
			"read_only": 1
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
