# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt
# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import date_diff, today

def execute(filters):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters):
    query = """
        SELECT
            td.name AS task_detail,
            td.plan_start_date,
            td.send_for_approval_date,
            td.approved_date,
            td.completion_date
        FROM
            `tabTask Detail` AS td
    """
    raw_data = frappe.db.sql(query, as_dict=True)

    data = []

    for row in raw_data:
        
        send_for_approval_aging = date_diff(row['send_for_approval_date'], row['plan_start_date']) if row['plan_start_date'] and row['send_for_approval_date'] else None
        approval_aging = date_diff(row['approved_date'], row['send_for_approval_date']) if row['send_for_approval_date'] and row['approved_date'] else None
        completion_aging = date_diff(row['completion_date'], row['approved_date']) if row['approved_date'] and row['completion_date'] else None

        send_for_approval_aging = send_for_approval_aging if send_for_approval_aging is not None and send_for_approval_aging >= 0 else None
        approval_aging = approval_aging if approval_aging is not None and approval_aging >= 0 else None
        completion_aging = completion_aging if completion_aging is not None and completion_aging >= 0 else None

        data.append({
            'task_detail': row['task_detail'],
            'plan_start_date': row['plan_start_date'],
            'send_for_approval_date': row['send_for_approval_date'],
            'send_for_approval_aging': send_for_approval_aging,
            'approved_date': row['approved_date'],
            'approval_aging': approval_aging,
            'completion_date': row['completion_date'],
            'completion_aging': completion_aging
        })

    return data



def get_columns():
    return [
        {
            "label": "Task Detail",
            "fieldname": "task_detail",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Plan Start Date",
            "fieldname": "plan_start_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": "Send For Approval Date",
            "fieldname": "send_for_approval_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": "Send For Approval Ageing (Days)",
            "fieldname": "send_for_approval_aging",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": "Approved Date",
            "fieldname": "approved_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": "Approval Ageing (Days)",
            "fieldname": "approval_aging",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": "Completion Date",
            "fieldname": "completion_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": "Completion Ageing (Days)",
            "fieldname": "completion_aging",
            "fieldtype": "Int",
            "width": 190
        }
    ]
