# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt


import frappe

def execute(filters):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_data(filters):
    
    
    damage_type = filters.get('damage')
    cause_type = filters.get('causes')
    equipment = filters.get('equipment_name')
    
    if not (filters.get('damage') or filters.get('causes') or filters.get('equipment_name')):
        return []

    if damage_type and cause_type:
        # Query for when both damage and cause filters are used
        query = """
            SELECT
                e.equipment_code,
                d.damage_type AS damage_type,
                c.cause AS cause,
                COUNT(td.name) AS occurrence_count,
                GROUP_CONCAT(td.name ORDER BY td.name) AS task_details,
                GROUP_CONCAT(td.parameter ORDER BY td.name) AS parameters,
                GROUP_CONCAT(td.status ORDER BY td.name) AS statuses,
                GROUP_CONCAT(td.plan_start_date ORDER BY td.name) AS plan_start_dates,
                GROUP_CONCAT(td.type ORDER BY td.name) AS types,
                GROUP_CONCAT(wc.name ORDER BY wc.name) AS work_centers,
                GROUP_CONCAT(a.name ORDER BY a.name) AS activities
            FROM
                `tabTask Detail` AS td
            JOIN
                `tabEquipment` AS e
            ON
                td.equipment_code = e.equipment_code
            JOIN
                `tabDamage CT` AS d
            ON
                td.name = d.parent
            JOIN
                `tabCause CT` AS c
            ON
                td.name = c.parent
            JOIN
                `tabWork Center` AS wc
            ON
                td.work_center = wc.name
            JOIN
                `tabActivity` AS a
            ON
                td.activity = a.name
            WHERE
                (%s IS NULL OR d.damage_type = %s)
                AND
                (%s IS NULL OR c.cause = %s)
                AND
                (%s IS NULL OR e.equipment_code = %s)
            GROUP BY
                e.equipment_code, d.damage_type, c.cause
            ORDER BY
                e.equipment_code, d.damage_type, c.cause
        """
        params = (damage_type, damage_type, cause_type, cause_type, equipment, equipment)

    elif cause_type:
        # Query for when only cause filter is used
        query = """
            SELECT
                e.equipment_code,
                c.cause AS cause,
                COUNT(c.name) AS occurrence_count,
                GROUP_CONCAT(td.name ORDER BY td.name) AS task_details,
                GROUP_CONCAT(td.parameter ORDER BY td.name) AS parameters,
                GROUP_CONCAT(td.status ORDER BY td.name) AS statuses,
                GROUP_CONCAT(td.plan_start_date ORDER BY td.name) AS plan_start_dates,
                GROUP_CONCAT(td.type ORDER BY td.name) AS types,
                GROUP_CONCAT(wc.name ORDER BY wc.name) AS work_centers,
                GROUP_CONCAT(a.name ORDER BY a.name) AS activities
            FROM
                `tabTask Detail` AS td
            JOIN
                `tabEquipment` AS e
            ON
                td.equipment_code = e.equipment_code
            JOIN
                `tabCause CT` AS c
            ON
                td.name = c.parent
            JOIN
                `tabWork Center` AS wc
            ON
                td.work_center = wc.name
            JOIN
                `tabActivity` AS a
            ON
                td.activity = a.name
            WHERE
                (%s IS NULL OR c.cause = %s)
                AND
                (%s IS NULL OR e.equipment_code = %s)
            GROUP BY
                e.equipment_code, c.cause
            ORDER BY
                e.equipment_code, c.cause
        """
        params = (cause_type, cause_type, equipment, equipment)

    elif damage_type:
        # Query for when only damage filter is used
        query = """
            SELECT
                e.equipment_code,
                d.damage_type AS damage_type,
                COUNT(d.name) AS occurrence_count,
                GROUP_CONCAT(td.name ORDER BY td.name) AS task_details,
                GROUP_CONCAT(td.parameter ORDER BY td.name) AS parameters,
                GROUP_CONCAT(td.status ORDER BY td.name) AS statuses,
                GROUP_CONCAT(td.plan_start_date ORDER BY td.name) AS plan_start_dates,
                GROUP_CONCAT(td.type ORDER BY td.name) AS types,
                GROUP_CONCAT(wc.name ORDER BY wc.name) AS work_centers,
                GROUP_CONCAT(a.name ORDER BY a.name) AS activities
            FROM
                `tabTask Detail` AS td
            JOIN
                `tabEquipment` AS e
            ON
                td.equipment_code = e.equipment_code
            JOIN
                `tabDamage CT` AS d
            ON
                td.name = d.parent
            JOIN
                `tabWork Center` AS wc
            ON
                td.work_center = wc.name
            JOIN
                `tabActivity` AS a
            ON
                td.activity = a.name
            WHERE
                (%s IS NULL OR d.damage_type = %s)
                AND
                (%s IS NULL OR e.equipment_code = %s)
            GROUP BY
                e.equipment_code, d.damage_type
            ORDER BY
                e.equipment_code, d.damage_type
        """
        params = (damage_type, damage_type, equipment, equipment)

    else:
        # Query when neither damage nor cause filters are applied
        query = """
            SELECT
                e.equipment_code
            FROM
                `tabEquipment` AS e
            WHERE
                (%s IS NULL OR e.equipment_code = %s)
            GROUP BY
                e.equipment_code
            ORDER BY
                e.equipment_code
        """
        params = (equipment, equipment)

    raw_data = frappe.db.sql(query, tuple(params), as_dict=True)

    data = []

    for row in raw_data:
        row_data = {
            'equipment_code': row.get('equipment_code'),
            'damage_type': row.get('damage_type'),
            'cause': row.get('cause'),
            'occurrence_count': row.get('occurrence_count'),
            'indent': 0, 
            'parent_account': None,
            'has_value': True
        }
        data.append(row_data)

        if damage_type or cause_type:
            task_details = row.get('task_details', '').split(',')
            parameters = row.get('parameters', '').split(',')
            statuses = row.get('statuses', '').split(',')
            plan_start_dates = row.get('plan_start_dates', '').split(',')
            types = row.get('types', '').split(',')
            work_centers = row.get('work_centers', '').split(',')
            activities = row.get('activities', '').split(',')

            for i in range(len(task_details)):
                data.append({
                    'equipment_code': '', 
                    'task_details': task_details[i] if i < len(task_details) else '',
                    'parameters': parameters[i] if i < len(parameters) else '',
                    'statuses': statuses[i] if i < len(statuses) else '',
                    'plan_start_dates': plan_start_dates[i] if i < len(plan_start_dates) else '',
                    'types': types[i] if i < len(types) else '',
                    'work_centers': work_centers[i] if i < len(work_centers) else '',
                    'activities': activities[i] if i < len(activities) else '',
                    'indent': 1,  
                    'parent_account': row['equipment_code'],
                    'has_value': True
                })

    return data

def get_columns(filters):
    columns = []
    damage_type = filters.get('damage')
    cause_type = filters.get('causes')
    equipment = filters.get('equipment_name')
    

    if damage_type or cause_type or equipment:
        
        columns.append({
            "label": "Equipment Code",
            "fieldname": "equipment_code",
            "fieldtype": "Link",
            "options": "Equipment",
            "width": 150
        })
        if damage_type and cause_type:
            columns.extend([
                {
                    "label": "Damage Type",
                    "fieldname": "damage_type",
                    "fieldtype": "Data",
                    "width": 150
                },
                {
                    "label": "Cause Type",
                    "fieldname": "cause",
                    "fieldtype": "Data",
                    "width": 150
                },
                {
                    "label": "Occurrence Count",
                    "fieldname": "occurrence_count",
                    "fieldtype": "Int",
                    "width": 150
                },
                {
                    "label": "Task Detail",
                    "fieldname": "task_details",
                    "fieldtype": "Link",
                    "options": "Task Detail",
                    "width": 200
                },
                {
                    "label": "Status",
                    "fieldname": "statuses",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Activity",
                    "fieldname": "activities",
                    "fieldtype": "Link",
                    "options": "Activity",
                    "width": 200
                },
                {
                    "label": "Parameter",
                    "fieldname": "parameters",
                    "fieldtype": "Link",
                    "options": "Parameter",
                    "width": 200
                },
                {
                    "label": "Plan Start Date",
                    "fieldname": "plan_start_dates",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Type",
                    "fieldname": "types",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Work Center",
                    "fieldname": "work_centers",
                    "fieldtype": "Data",
                    "width": 200
                }
            ])

        elif damage_type:
            columns.extend([
                {
                    "label": "Damage Type",
                    "fieldname": "damage_type",
                    "fieldtype": "Data",
                    "width": 150
                },
                {
                    "label": "Occurrence Count",
                    "fieldname": "occurrence_count",
                    "fieldtype": "Int",
                    "width": 150
                },
                {
                    "label": "Task Detail",
                    "fieldname": "task_details",
                    "fieldtype": "Link",
                    "options": "Task Detail",
                    "width": 200
                },
                {
                    "label": "Status",
                    "fieldname": "statuses",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Activity",
                    "fieldname": "activities",
                    "fieldtype": "Link",
                    "options": "Activity",
                    "width": 200
                },
                {
                    "label": "Parameter",
                    "fieldname": "parameters",
                    "fieldtype": "Link",
                    "options": "Parameter",
                    "width": 200
                },
                {
                    "label": "Plan Start Date",
                    "fieldname": "plan_start_dates",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Type",
                    "fieldname": "types",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Work Center",
                    "fieldname": "work_centers",
                    "fieldtype": "Data",
                    "width": 200
                }
            ])

        elif cause_type:
            columns.extend([
                {
                    "label": "Cause Type",
                    "fieldname": "cause",
                    "fieldtype": "Data",
                    "width": 150
                },
                {
                    "label": "Occurrence Count",
                    "fieldname": "occurrence_count",
                    "fieldtype": "Int",
                    "width": 150
                },
                {
                    "label": "Task Detail",
                    "fieldname": "task_details",
                    "fieldtype": "Link",
                    "options": "Task Detail",
                    "width": 200
                },
                {
                    "label": "Status",
                    "fieldname": "statuses",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Activity",
                    "fieldname": "activities",
                    "fieldtype": "Link",
                    "options": "Activity",
                    "width": 200
                },
                {
                    "label": "Parameter",
                    "fieldname": "parameters",
                    "fieldtype": "Link",
                    "options": "Parameter",
                    "width": 200
                },
                {
                    "label": "Plan Start Date",
                    "fieldname": "plan_start_dates",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Type",
                    "fieldname": "types",
                    "fieldtype": "Data",
                    "width": 200
                },
                {
                    "label": "Work Center",
                    "fieldname": "work_centers",
                    "fieldtype": "Data",
                    "width": 200
                }
            ])

    return columns
