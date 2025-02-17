# Copyright (c) 2025, LogicalDNA and contributors
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

    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    query = f"""
        SELECT
            td.name AS task_detail,
            td.plan_start_date,
            td.location,
			td.equipment_code,
            td.equipment_name,
            td.equipment_group,
            eq.section,
			td.type,
            td.activity,
			td.parameter,
            td.parameter_type,
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
        approver_name = frappe.db.get_value("User", row['approver'], "first_name") if row['approver'] else ""

        data.append({
            'task_detail': row['task_detail'],
            'plan_start_date': row['plan_start_date'],
            'location': row['location'],
			'equipment_code': row['equipment_code'],
            'equipment_name': row['equipment_name'],
            'equipment_group': row['equipment_group'],
            'section': row['section'],
			'type': row['type'],
            'activity': row['activity'],
			'parameter': row['parameter'],
            'parameter_type': row['parameter_type'],
			'approver':  approver_name,
            'assigned_to': row['assigned_to'],
            'work_center': row['work_center'],
            'status': row['status'],
        })

    return data



def get_columns():
    return [
        {
            "label": "Task Id",
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
            "label": "Equipment Code",
            "fieldname": "equipment_code",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 150
        },
        {
            "label": "Equipment Name",
            "fieldname": "equipment_name",
            "fieldtype": "Data",
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
            "label": "Work Center",
            "fieldname": "work_center",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Activity",
            "fieldname": "activity",
            "fieldtype": "Link",
            "options": "Activity",
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
            "label": "Approver",
            "fieldname": "approver",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 250
        },
        
        {
            "label": "Assigned To",
            "fieldname": "assigned_to",
            "fieldtype": "Small Text",
            "width": 250
        },
       
    ]
