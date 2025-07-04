# Copyright (c) 2025, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime

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
        equipment_groups = filters.get('equipment_group')
        placeholders = ','.join(['%s'] * len(equipment_groups))
        conditions.append(f"eg.equipment_group IN ({placeholders})")
        params.extend(equipment_groups)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    subquery_conditions = ["type = 'Breakdown'"]
    subquery_params = []

    if filters.get('start_date'):
        subquery_conditions.append("plan_start_date >= %s")
        subquery_params.append(filters.get('start_date'))

    if filters.get('to_date'):
        subquery_conditions.append("plan_start_date <= %s")
        subquery_params.append(filters.get('to_date'))

    subquery_where = " AND " + " AND ".join(subquery_conditions)

    start_date = filters.get("start_date")
    to_date = filters.get("to_date")
    total_hours = 0

    if start_date and to_date:
        d1 = datetime.strptime(start_date, "%Y-%m-%d")
        d2 = datetime.strptime(to_date, "%Y-%m-%d")
        total_hours = (d2 - d1).days + 1 
        total_hours *= 24

    query = f"""
        SELECT
            e.equipment_code,
            e.equipment_name,
            e.old_tag_dcs,
            e.work_center,
            GROUP_CONCAT(DISTINCT eg.equipment_group) AS equipment_group,
            e.description,
            e.custom_abc_indicator,
            COALESCE(td.breakdown_count, 0) AS breakdown_count,
            COALESCE(td.total_breakdown_time, 0) AS total_breakdown_time,
            COALESCE(td.mttr, 0) AS mttr,
            COALESCE(
                CASE 
                    WHEN td.breakdown_count > 0 THEN ROUND((%s - td.total_breakdown_time) / td.breakdown_count, 2)
                    ELSE 0
                END, 0
            ) AS mtbf,
            COALESCE(
                CASE 
                    WHEN td.breakdown_count > 0 THEN ROUND(td.mttr + ((%s - td.total_breakdown_time) / td.breakdown_count), 2)
                    ELSE 0
                END, 0
            ) AS mtbr,
            td.last_pm_done_date
        FROM
            `tabEquipment` AS e
        LEFT JOIN
            `tabEquipment Group CT` AS eg ON eg.parent = e.name
        LEFT JOIN (
            SELECT 
                equipment_code,
                COUNT(*) AS breakdown_count,
                ROUND(SUM(
                    TIMESTAMPDIFF(
                        SECOND,
                        TIMESTAMP(plan_start_date, task_creation_time),
                        TIMESTAMP(completion_date, completion_time)
                    )
                ) / 3600, 2) AS total_breakdown_time,
                ROUND(SUM(
                    TIMESTAMPDIFF(
                        SECOND,
                        TIMESTAMP(plan_start_date, task_creation_time),
                        TIMESTAMP(completion_date, completion_time)
                    )
                ) / COUNT(*) / 3600, 2) AS mttr,
                MAX(completion_date) AS last_pm_done_date
            FROM `tabTask Detail`
            WHERE 1=1 {subquery_where}
            GROUP BY equipment_code
        ) AS td ON td.equipment_code = e.equipment_code
        {where_clause}
        GROUP BY e.equipment_code
    """

    raw_data = frappe.db.sql(query, tuple([total_hours, total_hours] + params + subquery_params), as_dict=True)

    return [
        {
            'equipment_code': row['equipment_code'],
            'equipment_name': row['equipment_name'],
            'old_tag_dcs': row['old_tag_dcs'],
            'work_center': row['work_center'],
            'equipment_group': row['equipment_group'],
            'description': row['description'],
            'custom_abc_indicator': row['custom_abc_indicator'],
            'breakdown_count': row['breakdown_count'],
            'total_breakdown_time': row['total_breakdown_time'],
            'mttr': row['mttr'],
            'mtbf': row['mtbf'],
            'mtbr': row['mtbr'],
            'last_pm_done_date': row['last_pm_done_date']
        }
        for row in raw_data
    ]


def get_columns():
    return [
        {"label": "Equipment Code", "fieldname": "equipment_code", "fieldtype": "Data", "width": 150},
        {"label": "Old Tag DCS", "fieldname": "old_tag_dcs", "fieldtype": "Data", "width": 250},
        {"label": "Abc Indicator", "fieldname": "custom_abc_indicator", "fieldtype": "Data", "width": 250},
        {"label": "Work Center", "fieldname": "work_center", "fieldtype": "Data", "width": 250},
        {"label": "Equipment Group", "fieldname": "equipment_group", "fieldtype": "Data", "width": 250},
        {"label": "Equipment Name", "fieldname": "equipment_name", "fieldtype": "Data", "width": 250},
        {"label": "Equipment Description", "fieldname": "description", "fieldtype": "Data", "width": 250},
        {"label": "Total Breakdown Time (Hrs)", "fieldname": "total_breakdown_time", "fieldtype": "Float", "precision": 2, "width": 250},
        {"label": "Number of Breakdowns", "fieldname": "breakdown_count", "fieldtype": "Int", "width": 250},
        {"label": "MTTR", "fieldname": "mttr", "fieldtype": "Float", "precision": 2, "width": 250},
        {"label": "MTBF", "fieldname": "mtbf", "fieldtype": "Float", "precision": 2, "width": 250},
        {"label": "MTBR", "fieldname": "mtbr", "fieldtype": "Float", "precision": 2, "width": 250},
        {"label": "Last PM done date", "fieldname": "last_pm_done_date", "fieldtype": "Date", "width": 250},
    ]
