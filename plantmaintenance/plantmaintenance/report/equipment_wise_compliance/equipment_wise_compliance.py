# Copyright (c) 2025, LogicalDNA and contributors
# For license information, please see license.txt


# import frappe

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters or {})
#     return columns, data

# def get_data(filters):
#     conditions = []
#     params = []

#     if filters.get('equipment_code'):
#         conditions.append("e.equipment_code = %s")
#         params.append(filters.get('equipment_code'))

#     if filters.get('old_tag_dcs'):
#         conditions.append("e.old_tag_dcs = %s")
#         params.append(filters.get('old_tag_dcs'))

#     if filters.get('custom_abc_indicator'):
#         conditions.append("e.custom_abc_indicator = %s")
#         params.append(filters.get('custom_abc_indicator'))

#     if filters.get('work_center'):
#         conditions.append("e.work_center = %s")
#         params.append(filters.get('work_center'))

#     if filters.get('equipment_group'):
#         conditions.append("e.equipment_group = %s")
#         params.append(filters.get('equipment_group'))

#     if filters.get('start_date'):
#         conditions.append("e.creation >= %s")
#         params.append(filters.get('start_date'))

#     if filters.get('to_date'):
#         conditions.append("e.creation <= %s")
#         params.append(filters.get('to_date'))

#     where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

#     query = f"""
#         SELECT
#             e.equipment_code,
#             e.equipment_name,
#             e.old_tag_dcs,
#             e.work_center,
#             e.equipment_group,
#             e.description,
#             e.custom_abc_indicator,
#             COUNT(td.name) AS task_count,
# 			SUM(CASE WHEN td.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
# 			ROUND(
# 				CASE 
# 					WHEN COUNT(td.name) = 0 THEN 0
# 					ELSE SUM(CASE WHEN td.status = 'Completed' THEN 1 ELSE 0 END) / COUNT(td.name)
# 				END, 4
# 			) AS compliance_ratio,
# 			SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END) AS breakdown_count,
#             (
#                 SELECT MAX(td2.completion_date)
#                 FROM `tabTask Detail` AS td2
#                 WHERE td2.equipment_code = e.equipment_code
#                 AND td2.type = 'Breakdown'
#                 AND td2.status = 'Completed'
#             ) AS last_pm_done_date,
#             ROUND(SUM(
#                 CASE 
#                     WHEN td.type = 'Breakdown' AND td.status = 'Completed'
#                     THEN TIMESTAMPDIFF(SECOND, td.creation, td.modified) / 3600
#                     ELSE 0
#                 END
#             ), 2) AS total_breakdown_time,
#             ROUND(
#                 CASE 
#                     WHEN SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END) = 0 THEN 0
#                     ELSE SUM(
#                         CASE 
#                             WHEN td.type = 'Breakdown' AND td.status = 'Completed'
#                             THEN TIMESTAMPDIFF(SECOND, td.creation, td.modified) / 3600
#                             ELSE 0
#                         END
#                     ) / SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END)
#                 END, 2
#             ) AS mttr,
#             (
#                 SELECT 
#                     SEC_TO_TIME(TIMESTAMPDIFF(SECOND, td2.creation, td2.modified))
#                 FROM `tabTask Detail` td2
#                 WHERE 
#                     td2.equipment_code = e.equipment_code
#                     AND td2.type = 'Breakdown'
#                     AND td2.status = 'Completed'
#                 ORDER BY td2.modified DESC
#                 LIMIT 1
#             ) AS total_operating_time,
#             (
#                 SELECT 
#                     td2.name
#                 FROM `tabTask Detail` td2
#                 WHERE 
#                     td2.equipment_code = e.equipment_code
#                     AND td2.type = 'Breakdown'
#                     AND td2.status = 'Completed'
#                 ORDER BY td2.modified DESC
#                 LIMIT 1
#             ) AS latest_breakdown_task_id,
#             ROUND(
#                 CASE 
#                     WHEN SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END) = 0 THEN 0
#                     ELSE (
#                         SELECT 
#                             TIMESTAMPDIFF(SECOND, td2.creation, td2.modified) / 3600
#                         FROM `tabTask Detail` td2
#                         WHERE 
#                             td2.equipment_code = e.equipment_code
#                             AND td2.type = 'Breakdown'
#                             AND td2.status = 'Completed'
#                         ORDER BY td2.modified DESC
#                         LIMIT 1
#                     ) / SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END)
#                 END, 2
#             ) AS mtbf
#         FROM
#             `tabEquipment` AS e
#         LEFT JOIN
#             `tabTask Detail` AS td ON td.equipment_code = e.equipment_code
#         {where_clause}
#         GROUP BY
#             e.equipment_code
#     """

#     raw_data = frappe.db.sql(query, tuple(params), as_dict=True)

#     return [
#         {
#             'equipment_code': row['equipment_code'],
#             'equipment_name': row['equipment_name'],
#             'old_tag_dcs': row['old_tag_dcs'],
#             'work_center': row['work_center'],
#             'equipment_group': row['equipment_group'],
#             'description': row['description'],
#             'custom_abc_indicator': row['custom_abc_indicator'],
#             'task_count': row['task_count'],
# 			'completed_count': row['completed_count'],
# 			'compliance_ratio': row['compliance_ratio'],
# 			'breakdown_count': row['breakdown_count'],
#             'last_pm_done_date': row['last_pm_done_date'],
#             'total_breakdown_time': row['total_breakdown_time'],
#             'mttr': row['mttr'],
#             'total_operating_time': row['total_operating_time'],
#             'latest_breakdown_task_id': row['latest_breakdown_task_id'],
#             'mtbf': row['mtbf']
#         }
#         for row in raw_data
#     ]


# def get_columns():
#     return [
#         {
#             "label": "Equipment Code",
#             "fieldname": "equipment_code",
#             "fieldtype": "Data",
#             "width": 150
#         },
#         {
#             "label": "Old Tag DCS",
#             "fieldname": "old_tag_dcs",
#             "fieldtype": "Data",
#             "width": 250
#         },
# 		{
#             "label": "Abc Indicator",
#             "fieldname": "custom_abc_indicator",
#             "fieldtype": "Data",
#             "width": 250
#         },
# 		{
#             "label": "Work Center",
#             "fieldname": "work_center",
#             "fieldtype": "Data",
#             "width": 250
#         },  
# 		 {
#             "label": "Equipment Group",
#             "fieldname": "equipment_group",
#             "fieldtype": "Data",
#             "width": 250
#         },
# 		{
#             "label": "Equipment Name",
#             "fieldname": "equipment_name",
#             "fieldtype": "Data",
#             "width": 250
#         },
#         {
#             "label": "Equipment Description",
#             "fieldname": "description",
#             "fieldtype": "Data",
#             "width": 250
#         },
# 		{
# 			"label": "Number of PM Task Generated",
# 			"fieldname": "task_count",
# 			"fieldtype": "Int",
# 			"width": 250
# 		},
# 		{
# 			"label": "Number of PM Task Completed",
# 			"fieldname": "completed_count",
# 			"fieldtype": "Int",
# 			"width": 250
# 		},
# 		{
# 			"label": "Equipment wise PM Compliance",
# 			"fieldname": "compliance_ratio",
# 			"fieldtype": "Float",
# 			"width": 250
# 		},
# 		{
#             "label": "Last PM done date",
#             "fieldname": "last_pm_done_date",
#             "fieldtype": "Date",
#             "width": 250
#         },
# 		{
# 			"label": "Number of Breakdowns",
# 			"fieldname": "breakdown_count",
# 			"fieldtype": "Int",
# 			"width": 250
# 		},
#         # {
#         #     "label": "Total Breakdown Time (Hrs)",
#         #     "fieldname": "total_breakdown_time",
#         #     "fieldtype": "Float",
#         #     "precision": 2,
#         #     "width": 250
#         # },
#         {
#             "label": "MTTR",
#             "fieldname": "mttr",
#             "fieldtype": "Float",
#             "precision": 2,
#             "width": 250
#         },
#         # {
#         #     "label": "Total Operating Time",
#         #     "fieldname": "total_operating_time",
#         #     "fieldtype": "Data", 
#         #     "width": 250
#         # },
#         # {
#         #     "label": "Latest Breakdown Task ID",
#         #     "fieldname": "latest_breakdown_task_id",
#         #     "fieldtype": "Link",
#         #     "options": "Task Detail",
#         #     "width": 250
#         # },
#         {
#             "label": "MTBF",
#             "fieldname": "mtbf",
#             "fieldtype": "Float",
#             "precision": 2,
#             "width": 250
#         },
#         {
#             "label": "MTBR",
#             "fieldname": "mtbf",
#             "fieldtype": "Float",
#             "precision": 2,
#             "width": 250
#         },
           
#     ]



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
        conditions.append("""
            EXISTS (
                SELECT 1 FROM `tabEquipment Group CT` eg
                WHERE eg.parent = e.name AND eg.equipment_group = %s
            )
        """)
        params.append(filters.get('equipment_group'))
    # if filters.get('equipment_group'):
    #     conditions.append("e.equipment_group = %s")
    #     params.append(filters.get('equipment_group'))

    # if filters.get('start_date'):
    #     conditions.append("e.creation >= %s")
    #     params.append(filters.get('start_date'))

    # if filters.get('to_date'):
    #     conditions.append("e.creation <= %s")
    #     params.append(filters.get('to_date'))
    if filters.get('start_date'):
        conditions.append("td.plan_start_date >= %s")
        params.append(filters.get('start_date'))

    if filters.get('to_date'):
        conditions.append("td.plan_start_date <= %s")
        params.append(filters.get('to_date'))


    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            e.equipment_code,
            e.equipment_name,
            e.old_tag_dcs,
            e.work_center,
            (
                SELECT GROUP_CONCAT(eg.equipment_group)
                FROM `tabEquipment Group CT` eg
                WHERE eg.parent = e.name
            ) AS equipment_group,
            e.description,
            e.custom_abc_indicator,
            COUNT(td.name) AS task_count,
			SUM(CASE WHEN td.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
			ROUND(
				CASE 
					WHEN COUNT(td.name) = 0 THEN 0
					ELSE SUM(CASE WHEN td.status = 'Completed' THEN 1 ELSE 0 END) / COUNT(td.name)
				END, 4
			) AS compliance_ratio,
			SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END) AS breakdown_count,
            (
                SELECT MAX(td2.completion_date)
                FROM `tabTask Detail` AS td2
                WHERE td2.equipment_code = e.equipment_code
                AND td2.type = 'Breakdown'
                AND td2.status = 'Completed'
            ) AS last_pm_done_date,
            ROUND(SUM(
                CASE 
                    WHEN td.type = 'Breakdown' AND td.status = 'Completed'
                    THEN TIMESTAMPDIFF(SECOND, td.creation, td.modified) / 3600
                    ELSE 0
                END
            ), 2) AS total_breakdown_time,
            ROUND(
                CASE 
                    WHEN SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END) = 0 THEN 0
                    ELSE SUM(
                        CASE 
                            WHEN td.type = 'Breakdown' AND td.status = 'Completed'
                            THEN TIMESTAMPDIFF(SECOND, td.creation, td.modified) / 3600
                            ELSE 0
                        END
                    ) / SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END)
                END, 2
            ) AS mttr,
            (
                SELECT 
                    SEC_TO_TIME(TIMESTAMPDIFF(SECOND, td2.creation, td2.modified))
                FROM `tabTask Detail` td2
                WHERE 
                    td2.equipment_code = e.equipment_code
                    AND td2.type = 'Breakdown'
                    AND td2.status = 'Completed'
                ORDER BY td2.modified DESC
                LIMIT 1
            ) AS total_operating_time,
            (
                SELECT 
                    td2.name
                FROM `tabTask Detail` td2
                WHERE 
                    td2.equipment_code = e.equipment_code
                    AND td2.type = 'Breakdown'
                    AND td2.status = 'Completed'
                ORDER BY td2.modified DESC
                LIMIT 1
            ) AS latest_breakdown_task_id,
            ROUND(
                CASE 
                    WHEN SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END) = 0 THEN 0
                    ELSE (
                        SELECT 
                            TIMESTAMPDIFF(SECOND, td2.creation, td2.modified) / 3600
                        FROM `tabTask Detail` td2
                        WHERE 
                            td2.equipment_code = e.equipment_code
                            AND td2.type = 'Breakdown'
                            AND td2.status = 'Completed'
                        ORDER BY td2.modified DESC
                        LIMIT 1
                    ) / SUM(CASE WHEN td.type = 'Breakdown' THEN 1 ELSE 0 END)
                END, 2
            ) AS mtbf
        FROM
            `tabEquipment` AS e
        INNER JOIN
            `tabTask Detail` AS td ON td.equipment_code = e.equipment_code
        {where_clause}
        GROUP BY
            e.equipment_code
    """

    raw_data = frappe.db.sql(query, tuple(params), as_dict=True)

    return [
        {
            'equipment_code': row['equipment_code'],
            'equipment_name': row['equipment_name'],
            'old_tag_dcs': row['old_tag_dcs'],
            'work_center': row['work_center'],
            'equipment_group': row['equipment_group'],
            'description': row['description'],
            'custom_abc_indicator': row['custom_abc_indicator'],
            'task_count': row['task_count'],
			'completed_count': row['completed_count'],
			'compliance_ratio': row['compliance_ratio'],
			'breakdown_count': row['breakdown_count'],
            'last_pm_done_date': row['last_pm_done_date'],
            'total_breakdown_time': row['total_breakdown_time'],
            'mttr': row['mttr'],
            'total_operating_time': row['total_operating_time'],
            'latest_breakdown_task_id': row['latest_breakdown_task_id'],
            'mtbf': row['mtbf']
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
        },
		{
			"label": "Number of PM Task Generated",
			"fieldname": "task_count",
			"fieldtype": "Int",
			"width": 250
		},
		{
			"label": "Number of PM Task Completed",
			"fieldname": "completed_count",
			"fieldtype": "Int",
			"width": 250
		},
		{
			"label": "Equipment wise PM Compliance",
			"fieldname": "compliance_ratio",
			"fieldtype": "Float",
			"width": 250
		},
		{
            "label": "Last PM done date",
            "fieldname": "last_pm_done_date",
            "fieldtype": "Date",
            "width": 250
        },
		{
			"label": "Number of Breakdowns",
			"fieldname": "breakdown_count",
			"fieldtype": "Int",
			"width": 250
		},
        # {
        #     "label": "Total Breakdown Time (Hrs)",
        #     "fieldname": "total_breakdown_time",
        #     "fieldtype": "Float",
        #     "precision": 2,
        #     "width": 250
        # },
        {
            "label": "MTTR",
            "fieldname": "mttr",
            "fieldtype": "Float",
            "precision": 2,
            "width": 250
        },
        # {
        #     "label": "Total Operating Time",
        #     "fieldname": "total_operating_time",
        #     "fieldtype": "Data", 
        #     "width": 250
        # },
        # {
        #     "label": "Latest Breakdown Task ID",
        #     "fieldname": "latest_breakdown_task_id",
        #     "fieldtype": "Link",
        #     "options": "Task Detail",
        #     "width": 250
        # },
        {
            "label": "MTBF",
            "fieldname": "mtbf",
            "fieldtype": "Float",
            "precision": 2,
            "width": 250
        },
        {
            "label": "MTBR",
            "fieldname": "mtbf",
            "fieldtype": "Float",
            "precision": 2,
            "width": 250
        },
           
    ]