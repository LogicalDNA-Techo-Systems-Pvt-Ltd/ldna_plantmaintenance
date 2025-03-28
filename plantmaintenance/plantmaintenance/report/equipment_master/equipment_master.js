// Copyright (c) 2025, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment Master"] = {
	"filters": [
		{
			"label": "Equipment Code",
			"fieldname": "equipment_code",
			"fieldtype": "Link",
			"options": "Equipment",
			"width": 200
		},
		{
			"label": "Old Tag DCS",
			"fieldname": "old_tag_dcs",
			"fieldtype": "Link",
			"options": "Equipment",
			"width": 200
		},
		{
			"label": "ABC Indicator",
			"fieldname": "custom_abc_indicator",
			"fieldtype": "Select",
			"options": "\nA\nB\nC\nD",
			"width": 200
		},
		{
			"label": "Work Center",
			"fieldname": "work_center",
			"fieldtype": "Link",
			"options": "Work Center",
			"width": 200
		},
		{
			"label": "Equipement Group",
			"fieldname": "equipment_group",
			"fieldtype": "Link",
			"options": "Equipment  Group",
			"width": 200
		},

	]
};
