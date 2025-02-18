# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff, today

def execute(filters):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters):
    where_conditions = []
    filters_dict = {}

    if filters.get("from_date"):
        where_conditions.append("td.plan_start_date >= %(from_date)s")
        filters_dict["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        where_conditions.append("td.plan_start_date <= %(to_date)s")
        filters_dict["to_date"] = filters.get("to_date")

    if filters.get("task_detail"):
        where_conditions.append("td.name = %(task_detail)s")
        filters_dict["task_detail"] = filters.get("task_detail")

    if filters.get("type"):
        where_conditions.append("td.type = %(type)s")
        filters_dict["type"] = filters.get("type")

    if filters.get("work_center"):
        where_conditions.append("td.work_center = %(work_center)s")
        filters_dict["work_center"] = filters.get("work_center")

    if filters.get("equipment_group"):
        where_conditions.append("td.equipment_group = %(equipment_group)s")
        filters_dict["equipment_group"] = filters.get("equipment_group")

    if filters.get("status"):
        where_conditions.append("td.status = %(status)s")
        filters_dict["status"] = filters.get("status")

    # Join conditions properly
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    query = f"""
        SELECT
            td.name AS task_detail,
            td.plan_start_date,
            td.location,
			td.equipment_code,
            td.equipment_group,
            eq.section,
            eq.sub_section,
			td.type,
			td.parameter,
            td.parameter_type,
            td.minimum_value,
            td.maximum_value,
            td.standard_value,
            td.actual_value,
            td.acceptance_criteria_for_list,
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
        LEFT JOIN
        `tabEquipment` AS eq ON td.equipment_code = eq.name
        WHERE {where_clause}
    """
    raw_data = frappe.db.sql(query, filters_dict, as_dict=True)

    data = []

    for row in raw_data:
        if row['plan_start_date'] and row['completion_date']:
            overdue_days = max(date_diff(row['completion_date'], row['plan_start_date']), 0)
        elif row['plan_start_date']:
            overdue_days = max(date_diff(today(), row['plan_start_date']), 0)
        else:
            overdue_days = 0
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
        
        approver_name = frappe.db.get_value("User", row['approver'], "first_name") if row['approver'] else ""
        assigned_to_name = frappe.db.get_value("User", {"name": row['assigned_to']}, "first_name") or row['assigned_to']

        process_manager_name = (
            frappe.db.get_value("User", row['process_manager'], "first_name") 
            if row['status'] == "Completed" else ""
        )

        data.append({
            'task_detail': row['task_detail'],
            'plan_start_date': row['plan_start_date'],
            'location': row['location'],
			'equipment_code': row['equipment_code'],
            'equipment_group': row['equipment_group'],
            'section': row['section'],
            'sub_section': row['sub_section'],
			'type': row['type'],
			'parameter': row['parameter'],
            'parameter_type': row['parameter_type'],
            'minimum_value': row['minimum_value'],
            'maximum_value': row['maximum_value'],
            'standard_value': row['standard_value'],
            'actual_value': row['actual_value'],
            'acceptance_criteria_for_list': row['acceptance_criteria_for_list'],
			'approver': approver_name,
            'assigned_to': assigned_to_name,
            'send_for_approval_date': row['send_for_approval_date'],
            'approved_date': row['approved_date'],
            'completion_date': row['completion_date'],
            'work_center': row['work_center'],
            'status': row['status'],
            'overdue_days': overdue_days,
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
            "label": "Equipment",
            "fieldname": "equipment_code",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 150
        },
        {
            "label": "Equipment Group",
            "fieldname": "equipment_group",
            "fieldtype": "Link",
            "options": "Task Detail",
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
            "label": "Section",
            "fieldname": "section",
            "fieldtype": "Link",
            "options": "Section",
            "width": 150
        },
        {
            "label": "Sub-Section",
            "fieldname": "sub_section",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Work Center",
            "fieldname": "work_center",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Parameter",
            "fieldname": "parameter",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Parameter Type",
            "fieldname": "parameter_type",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        
        {
            "label": "Actual Value",
            "fieldname": "actual_value",
            "fieldtype": "Select",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Minimum Value",
            "fieldname": "minimum_value",
            "fieldtype": "Float",
            "width": 200
        },
        {
            "label": "Maximum Value",
            "fieldname": "maximum_value",
            "fieldtype": "Float",
            "width": 200
        },
        {
            "label": "Standard Value",
            "fieldname": "standard_value",
            "fieldtype": "Float",
            "width": 200
        },
        {
            "label": "Acceptance Criteria For List",
            "fieldname": "acceptance_criteria_for_list",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Select",
            "width": 200
        },
		{
            "label": "Maintenance Type",
            "fieldname": "type",
            "fieldtype": "Select",
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
            "label": "Completion by Maintenance Manager",
            "fieldname": "approver",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Maintenance Manager completion date",
            "fieldname": "approved_date",
            "fieldtype": "Date",
            "width": 200
        },
        {
            "label": "Time Taken by Maintenance Manager Team",
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
            "label": "Overdue Days",
            "fieldname": "overdue_days",
            "fieldtype": "Data",
            "width": 200
        },
    ]
