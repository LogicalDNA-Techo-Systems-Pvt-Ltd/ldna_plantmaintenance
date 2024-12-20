# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe

def execute(filters):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_data(filters):
    equipment_code = filters.get('equipment_code')
    activity_group = filters.get('activity_group')
    parameter_type = filters.get('parameter_type')

    query = """
        SELECT
            e.equipment_code,
            e.equipment_name,
            e.activity_group,
            act.activity,
            param.parameter,
            param.parameter_type,
            param.acceptance_criteria,
            param.number_of_readings,
            param.minimum_value,
            param.maximum_value,
            param.values,
            param_doc.frequency
        FROM
            `tabEquipment` AS e
        LEFT JOIN 
            `tabActivity CT` AS act
        ON 
            act.parent = e.activity_group
        LEFT JOIN
            `tabParameter CT` AS param
        ON
            param.parent = act.activity
        LEFT JOIN
            `tabParameter` AS param_doc
        ON
            param.parameter = param_doc.name
        AND
            param.parameter_type = param_doc.parameter_type
        AND
            param.acceptance_criteria = param_doc.acceptance_criteria
        AND 
            param.number_of_readings = param_doc.number_of_readings
        AND
            param.minimum_value = param_doc.minimum_value
        AND
            param.maximum_value = param_doc.maximum_value
        AND
            param.values = param_doc.values
        WHERE
            (%s IS NULL OR e.equipment_code = %s)
        AND
            (e.activity_group IS NOT NULL) 
        AND
            (%s IS NULL OR e.activity_group = %s)
        AND
            (%s IS NULL OR param.parameter_type = %s)
    """
    params = (equipment_code, equipment_code, activity_group, activity_group, parameter_type, parameter_type)

    raw_data = frappe.db.sql(query, params, as_dict=True)

    data = []
    for row in raw_data:  
        data.append({
            'equipment_code': row['equipment_code'],
            'equipment_name': row['equipment_name'],
            'activity_group': row['activity_group'],
            'activity': row['activity'],
            'parameter': row['parameter'],
            'parameter_type': row['parameter_type'],
            'acceptance_criteria': row['acceptance_criteria'],
            'number_of_readings': row['number_of_readings'],
            'minimum_value': row['minimum_value'],
            'maximum_value': row['maximum_value'],
            'values': row['values'],
            'frequency': row['frequency']
        })

    return data

def get_columns():
    return [
        {
            "label": "Equipment Code",
            "fieldname": "equipment_code",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Equipment Name",
            "fieldname": "equipment_name",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Activity Group",
            "fieldname": "activity_group",
            "fieldtype": "Link",
            "options": "Activity Group",
            "width": 250
        },
        {
            "label": "Activity",
            "fieldname": "activity",
            "fieldtype": "Data",
            "width": 260
        },
        {
            "label": "Parameter",
            "fieldname": "parameter",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Parameter Type",
            "fieldname": "parameter_type",
            "fieldtype": "Select",
            "options": "Parameter",
            "width": 150
        },
        {
            "label": "Acceptance Criteria",
            "fieldname": "acceptance_criteria",
            "fieldtype": "Select",
            "Options": "Parameter",
            "width": 170
        },
        {
            "label": "Number Of Readings",
            "fieldname": "number_of_readings",
            "fieldtype": "Int",
            "width": 180
        },
        {
            "label": "Minimum Value",
            "fieldname": "minimum_value",
            "fieldtype": "Float",
            "width": 150
        },
        {
            "label": "Maximum Value",
            "fieldname": "maximum_value",
            "fieldtype": "Float",
            "width": 150
        },
        {
            "label": "Acceptance Criteria for List",
            "fieldname": "values",
            "fieldtype": "Small Text",
            "width": 220
        },
        
        {
            "label": "Frequency",
            "fieldname": "frequency",
            "fieldtype": "Data",
            "width": 200
        }
    ]
