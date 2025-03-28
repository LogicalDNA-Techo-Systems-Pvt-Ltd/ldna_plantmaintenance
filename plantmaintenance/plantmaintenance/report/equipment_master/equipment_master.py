# Copyright (c) 2025, LogicalDNA and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data

def get_data(filters):
    conditions = []
    params = []

    if filters.get('equipment_code'):
        conditions.append("e.equipment_code = %s")
        params.append(filters.get('equipment_code'))

    if filters.get('old_tag_dcs'):
        conditions.append("e.old_tag_dcs = %s")
        params.append(filters.get('old_tag_dcs'))

    if filters.get('custom_abc_indicator'):
        conditions.append("e.custom_abc_indicator = %s")
        params.append(filters.get('custom_abc_indicator'))

    if filters.get('work_center'):
        conditions.append("e.work_center = %s")
        params.append(filters.get('work_center'))

    if filters.get('equipment_group'):
        conditions.append("e.equipment_group = %s")
        params.append(filters.get('equipment_group'))

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            e.equipment_code,
            e.equipment_name,
            e.old_tag_dcs,
            e.location,
            e.section,
            e.sub_section,
            e.work_center,
            e.equipment_group,
            e.description,
			e.custom_abc_indicator
        FROM
            `tabEquipment` AS e
        {where_clause}
    """

    raw_data = frappe.db.sql(query, tuple(params), as_dict=True)

    return [
        {
            'equipment_code': row['equipment_code'],
            'equipment_name': row['equipment_name'],
            'old_tag_dcs': row['old_tag_dcs'],
            'location': row['location'],
            'section': row['section'],
            'sub_section': row['sub_section'],
            'work_center': row['work_center'],
            'equipment_group': row['equipment_group'],
            'description': row['description'],
			'custom_abc_indicator': row['custom_abc_indicator'],
        }
        for row in raw_data
    ]

def get_columns():
    return [
        {
            "label": "Equipment Code",
            "fieldname": "equipment_code",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Old Tag DCS",
            "fieldname": "old_tag_dcs",
            "fieldtype": "Data",
            "width": 250
        },
		{
            "label": "Abc Indicator",
            "fieldname": "custom_abc_indicator",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Location",
            "fieldname": "location",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Section",
            "fieldname": "section",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Sub Section",
            "fieldname": "sub_section",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Work Center",
            "fieldname": "work_center",
            "fieldtype": "Data",
            "width": 250
        },  
        {
            "label": "Equipment Group",
            "fieldname": "equipment_group",
            "fieldtype": "Data",
            "width": 250
        },
		{
            "label": "Equipment Name",
            "fieldname": "equipment_name",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Equipment Description",
            "fieldname": "description",
            "fieldtype": "Data",
            "width": 250
        }
    ]
