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
            td.location,
			td.equipment_code,
			td.type,
			td.parameter,
			td.approver,
            td.assigned_to,
            td.send_for_approval_date,
            td.approved_date,
            td.completion_date,
            td.work_center,
            td.status,
            td.modified_by AS process_manager
           
        FROM
            `tabTask Detail` AS td
    """
    raw_data = frappe.db.sql(query, as_dict=True)

    data = []

    for row in raw_data:
        if row['plan_start_date'] and row['send_for_approval_date']:
            days_diff = max(date_diff(row['send_for_approval_date'], row['plan_start_date']), 0)
            time_taken_by_technical_team = f"{days_diff} days"
        else:
            time_taken_by_technical_team = ""  
        
        if row['send_for_approval_date'] and row['approved_date']:
            work_days_diff = max(date_diff(row['approved_date'], row['send_for_approval_date']), 0)
            time_taken_by_work_completion_team = f"{work_days_diff} days"
        else:
            time_taken_by_work_completion_team = ""

        if row['approved_date'] and row['completion_date']:
            process_days_diff = max(date_diff(row['completion_date'], row['approved_date']), 0)
            time_taken_by_process_manager = f"{process_days_diff} days"
        else:
            time_taken_by_process_manager = ""
        
        approver_name = frappe.db.get_value("User", row['approver'], "full_name") if row['approver'] else ""

        process_manager_name = (
            frappe.db.get_value("User", row['process_manager'], "full_name") 
            if row['status'] == "Completed" else ""
        )

        data.append({
            'task_detail': row['task_detail'],
            'plan_start_date': row['plan_start_date'],
            'location': row['location'],
			'equipment_code': row['equipment_code'],
			'type': row['type'],
			'parameter': row['parameter'],
			'approver': approver_name,
            'assigned_to': row['assigned_to'],
            'send_for_approval_date': row['send_for_approval_date'],
            'approved_date': row['approved_date'],
            'completion_date': row['completion_date'],
            'work_center': row['work_center'],
            'status': row['status'],
            'time_taken_by_technical_team': time_taken_by_technical_team,
            'time_taken_by_work_completion_team': time_taken_by_work_completion_team,
            'time_taken_by_process_manager': time_taken_by_process_manager,
            'process_manager_name': process_manager_name
        })

    return data



def get_columns():
    return [
        {
            "label": "Notification",
            "fieldname": "task_detail",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Notification Created Date",
            "fieldname": "plan_start_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": "Location",
            "fieldname": "location",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 150
        },
        
		{
            "label": "Equipment",
            "fieldname": "equipment_code",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 150
        },
		{
            "label": "Maintenance Type",
            "fieldname": "type",
            "fieldtype": "Select",
            "options": "Task Detail",
            "width": 200
        },
		{
            "label": "Notification Description",
            "fieldname": "parameter",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
		{
            "label": "Notification Raised by (Person)",
            "fieldname": "approver",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 250
        },
        
        {
            "label": "Technical completion by",
            "fieldname": "assigned_to",
            "fieldtype": "Small Text",
            "width": 250
        },
        {
            "label": "Technical completion Date",
            "fieldname": "send_for_approval_date",
            "fieldtype": "Date",
            "width": 200
        },
        {
            "label": "Time taken by Technical Team",
            "fieldname": "time_taken_by_technical_team",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Work completion by",
            "fieldname": "approver",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Work completion date",
            "fieldname": "approved_date",
            "fieldtype": "Date",
            "width": 200
        },
        {
            "label": "Time Taken by Work Completion Team",
            "fieldname": "time_taken_by_work_completion_team",
            "fieldtype": "Data",  
            "width": 250
        },
        {
            "label": "Process Manager Name",
            "fieldname": "process_manager_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Process Manager Date",
            "fieldname": "completion_date",
            "fieldtype": "Date",
            "width": 200
        },
        {
            "label": "Time Taken by Process Manager",
            "fieldname": "time_taken_by_process_manager",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Department from each User",
            "fieldname": "work_center",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Select",
            "width": 200
        },


    ]
