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
            `tabEquipment` AS e ON td.equipment_code = e.equipment_code
        LEFT JOIN
            `tabDamage CT` AS d ON td.name = d.parent
        LEFT JOIN
            `tabCause CT` AS c ON td.name = c.parent
        LEFT JOIN
            `tabWork Center` AS wc ON td.work_center = wc.name
        LEFT JOIN
            `tabActivity` AS a ON td.activity = a.name
        WHERE
            (%s IS NULL OR e.equipment_code = %s)
            AND
            (d.damage_type IS NOT NULL) 
            AND
            (c.cause IS NOT NULL) 
            AND
            (%s IS NULL OR d.damage_type = %s)
            AND
            (%s IS NULL OR c.cause = %s)
        GROUP BY
            e.equipment_code, d.damage_type, c.cause
        ORDER BY
            e.equipment_code, d.damage_type, c.cause
    """
    
  
    params = (equipment, equipment, damage_type, damage_type, cause_type, cause_type)

   
    raw_data = frappe.db.sql(query, params, as_dict=True)

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

        task_details = row.get('task_details', '')
        parameters = row.get('parameters', '')
        statuses = row.get('statuses', '')
        plan_start_dates = row.get('plan_start_dates', '')
        types = row.get('types', '')
        work_centers = row.get('work_centers', '')
        activities = row.get('activities', '')

        task_details_list = task_details.split(',') if task_details else []
        parameters_list = parameters.split(',') if parameters else []
        statuses_list = statuses.split(',') if statuses else []
        plan_start_dates_list = plan_start_dates.split(',') if plan_start_dates else []
        types_list = types.split(',') if types else []
        work_centers_list = work_centers.split(',') if work_centers else []
        activities_list = activities.split(',') if activities else []

        for i in range(len(task_details_list)):
            data.append({
                'equipment_code': '', 
                'task_details': task_details_list[i] if i < len(task_details_list) else '',
                'parameters': parameters_list[i] if i < len(parameters_list) else '',
                'statuses': statuses_list[i] if i < len(statuses_list) else '',
                'plan_start_dates': plan_start_dates_list[i] if i < len(plan_start_dates_list) else '',
                'types': types_list[i] if i < len(types_list) else '',
                'work_centers': work_centers_list[i] if i < len(work_centers_list) else '',
                'activities': activities_list[i] if i < len(activities_list) else '',
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

    columns.append({
        "label": "Equipment Code",
        "fieldname": "equipment_code",
        "fieldtype": "Link",
        "options": "Equipment",
        "width": 150
    })
    
    if damage_type or cause_type or equipment:
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
                }
            ])
        elif equipment:
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
                }
            ])
        
       
        columns.extend([
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

    else:
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

    return columns
