// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt
frappe.query_reports["Task Summary"] = {
    "filters": [
        {
            "fieldname": "date_filter",
            "label": __("Date Filter"),
            "fieldtype": "Select",
            "options": ["Daily", "Weekly", "Monthly", "Yearly"],
            "default": "Monthly",
            "reqd": 1,
            
        }
    ]

};
