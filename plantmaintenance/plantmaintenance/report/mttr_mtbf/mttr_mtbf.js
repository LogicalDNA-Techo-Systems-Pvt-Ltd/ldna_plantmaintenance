// Copyright (c) 2025, LogicalDNA and contributors
// For license information, please see license.txt

frappe.query_reports["MTTR-MTBF"] = {
	"filters": [
		{
            "fieldname": "start_date",
            "label": __("Start Date"),
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
			"label": "Equipment Code",
			"fieldname": "equipment_code",
			"fieldtype": "Link",
			"options": "Equipment",
			"width": 200
		},
		{
			"label": "Old Tag DCS",
			"fieldname": "old_tag_dcs",
			"fieldtype": "Data",
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

	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "action" && data) {
			value = `<button class="btn btn-xs btn-primary" 
				onclick="frappe.query_reports['MTTR-MTBF'].show_details('${data.equipment_code}')">
				Action
			</button>`;
		}
		
		return value;
	},
	"show_details": function(equipment_code) {
		frappe.set_route("List", "Task Detail", {
			"equipment_code": equipment_code,
			"type": "Breakdown"
		});
	}
};