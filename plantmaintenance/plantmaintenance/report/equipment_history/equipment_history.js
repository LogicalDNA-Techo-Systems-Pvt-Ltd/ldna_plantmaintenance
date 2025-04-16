// Copyright (c) 2025, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment History"] = {
	"filters": [
        {
            "fieldname": "start_date",
            "label": __("Start Date"),
            "fieldtype": "Date",
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
        },
        {
            "fieldname": "task_detail",
            "label": __("Task ID"),
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "OLD TAG (DCS)",
            "fieldname": "old_tag_dcs",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "ABC Indicator",
            "fieldname": "custom_abc_indicator",
            "fieldtype": "Select",
            "options": "\nA\nB\nC\nD",
            "width": 120
        },
        {
            "label": "Equipment",
            "fieldname": "equipment_code",
            "fieldtype": "Link",
            "options": "Equipment",
            "width": 200
        },
        {
            "label": "Equipment Name",
            "fieldname": "equipment_name",
            "fieldtype": "Data",
            "width": 200,
           
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
        
	]
};
