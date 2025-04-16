# Copyright (c) 2025, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate
from collections import defaultdict

def execute(filters):
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
        where_conditions.append("td.old_tag_dcs= %(old_tag_dcs)s")
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
            td.parameter_type,
            td.activity,
            td.frequency,
            eq.section,
            td.location,
            td.equipment_group,
            td.work_center,
            td.minimum_value,
            td.maximum_value,
            td.standard_value,
            eq.custom_abc_indicator
        FROM
            `tabTask Detail` td
        LEFT JOIN
            `tabEquipment` eq ON td.equipment_code = eq.name
        WHERE
            {where_clause} AND td.plan_start_date > CURDATE()
        ORDER BY
            td.parameter, td.plan_start_date
    """

    raw_data = frappe.db.sql(query, filters_dict, as_dict=True)

    seen = set()
    final_data = []

    for row in raw_data:
        key = (row.parameter, row.equipment_code)
        if key not in seen:
            seen.add(key)
            final_data.append(row)

    return final_data


def get_columns():
    return [
        {
            "label": "Task ID",
            "fieldname": "task_detail",
            "fieldtype": "Link",
            "options": "Task Detail",
            "width": 200
        },
        {
            "label": "Next Plan Date",
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
            "label": "OLD TAG (DCS)",
            "fieldname": "old_tag_dcs",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "ABC Indicator",
            "fieldname": "custom_abc_indicator",
            "fieldtype": "Select",
            "options": "Equipment",
            "width": 120
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
            "label": "Frequency",
            "fieldname": "frequency",
            "fieldtype": "Select",
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
     
    ]
