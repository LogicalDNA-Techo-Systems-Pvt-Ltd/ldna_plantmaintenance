// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["Activity Grp , Activity and Parameter"] = {
	"filters": [
		{
			"label": "Equipment Code",
			"fieldname": "equipment_code",
			"fieldtype": "Link",
			"options": "Equipment",
			"width": 200
		},
		{
			"label": "Activity Group",
			"fieldname": "activity_group",
			"fieldtype": "Link",
			"options": "Activity Group",
			"width": 200
		},
		{
			"label": "Parameter Type",
			"fieldname": "parameter_type",
			"fieldtype": "Select",
			"options": [
				" ",
				"Binary",
				"Numeric",
				"List"],
			"width": 200
		}
	]
};
