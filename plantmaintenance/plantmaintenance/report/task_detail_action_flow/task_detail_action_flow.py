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
			td.old_tag_dcs,
            td.equipment_name,
            td.equipment_group,
			td.type,
            td.activity,
			td.parameter,
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
        `tabEquipment` AS eq ON td.old_tag_dcs = eq.name
        WHERE {where_clause}
    """
    raw_data = frappe.db.sql(query, filters_dict, as_dict=True)

    data = []

    for row in raw_data:
        assigned_to_name = frappe.db.get_value("User", {"name": row['assigned_to']}, "first_name") or row['assigned_to']

        data.append({
            'task_detail': row['task_detail'],
            'plan_start_date': row['plan_start_date'],
			'old_tag_dcs': row['old_tag_dcs'],
            'equipment_name': row['equipment_name'],
            'equipment_group': row['equipment_group'],
			'type': row['type'],
            'activity': row['activity'],
			'parameter': row['parameter'],
            'assigned_to': assigned_to_name,
            'work_center': row['work_center'],
            'status': row['status'],
        })

    return data



def get_columns():
    return [
		{
            "label": "",
            "fieldname": "select_task",
            "fieldtype": "Checkbox",
            "width": 50
        },
        {
            "label": "Task Id",
            "fieldname": "task_detail",
            "fieldtype": "Link",
            "options": "Task Detail",
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
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Select",
            "width": 200
        },
        {
            "label": "Plan Start Date",
            "fieldname": "plan_start_date",
            "fieldtype": "Date",
            "width": 150
        },
		{
            "label": "OLD TAG (DCS)",
            "fieldname": "old_tag_dcs",
            "fieldtype": "Data",
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
            "label": "Assigned To",
            "fieldname": "assigned_to",
            "fieldtype": "Small Text",
            "width": 250
        },
       
    ]

@frappe.whitelist()
def update_task_status(task_ids, status):
    if isinstance(task_ids, str):
        task_ids = frappe.parse_json(task_ids)

    if not task_ids:
        return "No tasks selected"

    workflow_states = {
        "Approved": "Approved",
        "Rejected": "Rejected",
        "Completed": "Completed",
        "Cancelled": "Cancelled"
    }

    workflow_state = workflow_states.get(status)

    for task_id in task_ids:
        task_doc = frappe.get_doc("Task Detail", task_id)
        task_doc.status = status 
        if workflow_state:
            task_doc.workflow_state = workflow_state  
        task_doc.save(ignore_permissions=True)
        frappe.db.commit()

    return "success"
