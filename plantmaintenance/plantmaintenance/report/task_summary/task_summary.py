# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    
    columns = [
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 150},
        {"fieldname": "count", "label": _("Count"), "fieldtype": "Int", "width": 150},
    ]
    
    
    statuses = ["Open", "Completed"]
    status_data = []
    for status in statuses:
        count = frappe.db.count("Task Detail", filters={"status": status})
        status_data.append({"status": status, "count": count})
    
    
    all_tasks_count = frappe.db.count("Task Detail")
    status_data.append({"status": "Task Created", "count": all_tasks_count})
    
    data = status_data
    
    return columns, data
