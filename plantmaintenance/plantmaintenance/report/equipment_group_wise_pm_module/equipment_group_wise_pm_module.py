# Copyright (c) 2025, LogicalDNA and contributors
# For license information, please see license.txt

# import frappe

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters):
    selected_date = filters.get("plan_start_date") if filters else None
    selected_type = filters.get("task_type") if filters else None
    equipment_group = filters.get("equipment_group") if filters else None

    def build_condition(extra_conditions):
        conditions = extra_conditions[:]
        if selected_type:
            conditions.append(f"td.type = '{selected_type}'")
        if selected_date:
            conditions.append(f"td.plan_start_date = '{selected_date}'")
        if equipment_group:
            conditions.append(f"td.equipment_group = '{equipment_group}'")
        return " AND ".join(conditions)

    open_task_case = f"""
        COUNT(CASE 
            WHEN {build_condition(["td.status = 'Open'"])}
            THEN td.name 
        END)
    """

    generated_task_case = f"""
        COUNT(CASE 
            WHEN {build_condition([]) or '1=1'}
            THEN td.name 
        END)
    """

    unassigned_task_case = f"""
        COUNT(CASE 
            WHEN {build_condition(["(td.assigned_to IS NULL OR td.assigned_to = '')"])}
            THEN td.name 
        END)
    """

    completed_by_technical_case = f"""
        COUNT(CASE 
            WHEN {build_condition(["td.status = 'Pending Approval'"])}
            THEN td.name 
        END)
    """

    open_by_process_case = f"""
        COUNT(CASE 
            WHEN {build_condition(["td.status = 'Approved'"])}
            THEN td.name 
        END)
    """

    pending_jobs_case = f"""
        COUNT(CASE 
            WHEN {build_condition([
                "td.status IN ('Hold', 'In Progress', 'Rejected', 'Cancelled', 'Overdue')"
            ])}
            THEN td.name 
        END)
    """

    query = f"""
        SELECT 
            wc.name AS work_center,
            {open_task_case} AS open_task,
            {generated_task_case} AS generated_task,
            {unassigned_task_case} AS unassigned_task,
            {completed_by_technical_case} AS completed_by_technical,
            {open_by_process_case} AS open_by_process,
            {pending_jobs_case} AS pending_jobs
        FROM `tabWork Center` wc
        LEFT JOIN `tabTask Detail` td ON td.work_center = wc.name
        GROUP BY wc.name
    """
    return frappe.db.sql(query, as_dict=True)

def get_columns():
    return [
        {"label": "Work Center", "fieldname": "work_center", "fieldtype": "Data", "width": 200},
        {"label": "Open Task", "fieldname": "open_task", "fieldtype": "Int", "width": 150},
        {"label": "Generated Task", "fieldname": "generated_task", "fieldtype": "Int", "width": 150},
        {"label": "Unassigned Task", "fieldname": "unassigned_task", "fieldtype": "Int", "width": 150},
        {"label": "Completed by Technical", "fieldname": "completed_by_technical", "fieldtype": "Int", "width": 200},
        {"label": "Open by Process", "fieldname": "open_by_process", "fieldtype": "Int", "width": 150},
        {"label": "Pending Jobs", "fieldname": "pending_jobs", "fieldtype": "Int", "width": 200},
    ]
