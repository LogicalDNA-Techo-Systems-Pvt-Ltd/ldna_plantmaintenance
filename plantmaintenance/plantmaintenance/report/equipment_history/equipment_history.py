# Copyright (c) 2025, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters):
    where_conditions = []
    filters_dict = {}

    if filters.get("task_detail"):
        where_conditions.append("td.name = %(task_detail)s")
        filters_dict["task_detail"] = filters.get("task_detail")

    if filters.get("equipment_code"):
        where_conditions.append("td.equipment_code = %(equipment_code)s")
        filters_dict["equipment_code"] = filters.get("equipment_code")

    if filters.get("work_center"):
        where_conditions.append("td.work_center = %(work_center)s")
        filters_dict["work_center"] = filters.get("work_center")

    if filters.get("equipment_group"):
        where_conditions.append("td.equipment_group = %(equipment_group)s")
        filters_dict["equipment_group"] = filters.get("equipment_group")

    if filters.get("equipment_name"):
        where_conditions.append("td.equipment_name = %(equipment_name)s")
        filters_dict["equipment_name"] = filters.get("equipment_name")
    
    if filters.get("old_tag_dcs"):
        where_conditions.append("td.old_tag_dcs = %(old_tag_dcs)s")
        filters_dict["old_tag_dcs"] = filters.get("old_tag_dcs")
    
    if filters.get("start_date"):
        where_conditions.append("td.plan_start_date >= %(start_date)s")
        filters_dict["start_date"] = filters.get("start_date")

    if filters.get("to_date"):
        where_conditions.append("td.plan_start_date <= %(to_date)s")
        filters_dict["to_date"] = filters.get("to_date")
    
    if filters.get("custom_abc_indicator"):
        where_conditions.append("eq.custom_abc_indicator = %(custom_abc_indicator)s")
        filters_dict["custom_abc_indicator"] = filters.get("custom_abc_indicator")

    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

    query = f"""
        SELECT
            td.name AS task_detail,
            td.plan_start_date,
            td.parameter,
            td.equipment_code,
            td.old_tag_dcs,
            td.equipment_name,
            td.description,
            td.frequency,
            td.equipment_group,
            td.work_center,
            eq.custom_abc_indicator,
            TIME(td.creation) AS creation_time,
            TIME(td.modified) AS completion_time,
            td.modified_by AS process_manager,
            td.status,
            td.completion_date
        FROM
            `tabTask Detail` td
        LEFT JOIN
            `tabEquipment` eq ON td.equipment_code = eq.name
        WHERE
            {where_clause}
        ORDER BY
            td.parameter, td.plan_start_date
    """

    results = frappe.db.sql(query, filters_dict, as_dict=True)

    for row in results:
        if row.get("status") == "Completed" and row.get("process_manager"):
            full_name = (
                frappe.db.get_value("User", row["process_manager"], "full_name") or
                "{} {}".format(
                    frappe.db.get_value("User", row["process_manager"], "first_name") or "",
                    frappe.db.get_value("User", row["process_manager"], "last_name") or ""
                ).strip()
            )
            row["completion_by"] = full_name if full_name else row["process_manager"]
        else:
            row["completion_by"] = ""


    return results

def get_columns():
    return [
        {
            "label": "Equipment Code",
            "fieldname": "equipment_code",
            "fieldtype": "Link",
            "options": "Equipment",
            "width": 150
        },
        {
            "label": "OLD TAG (DCS)",
            "fieldname": "old_tag_dcs",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "ABC Indicator",
            "fieldname": "custom_abc_indicator",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Work Center",
            "fieldname": "work_center",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Equipment Category",
            "fieldname": "equipment_group",
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
            "label": "Equipment Description",
            "fieldname": "description",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Task ID",
            "fieldname": "task_detail",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Task Date",
            "fieldname": "plan_start_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": "Parameter",
            "fieldname": "parameter",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Frequency",
            "fieldname": "frequency",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Task Opening Date",
            "fieldname": "plan_start_date",
            "fieldtype": "Date",
            "width": 200
        },
        {
            "label": "Task Opening Time",
            "fieldname": "creation_time",
            "fieldtype": "Time",
            "width": 200
        },
        {
            "label": "Task Completion Date",
            "fieldname": "completion_date",
            "fieldtype": "Date",
            "width": 200
        },
        {
            "label": "Task Completion Time",
            "fieldname": "completion_time",
            "fieldtype": "Time",
            "width": 200
        },
        {
            "label": "Task Completed By",
            "fieldname": "completion_by",
            "fieldtype": "Data",
            "width": 200
        },
    ]
