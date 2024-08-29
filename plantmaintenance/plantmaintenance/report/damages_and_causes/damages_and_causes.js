// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["Damages And Causes"] = {
		"filters": [
			{
				"label": "Equipment",
				"fieldname": "equipment_name",
				"fieldtype": "Link",
				"options": "Equipment",
				"width": 200
				},
				{
				"label": "Damages",
				"fieldname": "damage",
				"fieldtype": "Link",
				"options" : "Damage",
				"width": 200
				},
				{
				"label": "Causes",
				"fieldname": "causes",
				"fieldtype": "Link",
				"options" : "Cause",
				"width": 200
				}
			]
	};
	
