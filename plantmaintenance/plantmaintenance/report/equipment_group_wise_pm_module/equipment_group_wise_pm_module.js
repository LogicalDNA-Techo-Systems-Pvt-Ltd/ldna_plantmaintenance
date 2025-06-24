// Copyright (c) 2025, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment Group Wise PM Module"] = {
	"filters": [
        {
            "label": "Date",
            "fieldname": "plan_start_date",
            "fieldtype": "Date"
        },
        {
            "label": "Task Type",
            "fieldname": "task_type",
            "fieldtype": "Select",
            "options": "\nPreventive\nBreakdown"
        },
        {
            "label": "Equipment Group",
            "fieldname": "equipment_group",
            "fieldtype": "Link",
            "options": "Equipment  Group"
        }
    ]
};
