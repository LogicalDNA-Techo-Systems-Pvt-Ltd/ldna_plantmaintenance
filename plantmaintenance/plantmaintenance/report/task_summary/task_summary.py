# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

# import frappe


import frappe
from datetime import datetime, timedelta

def execute(filters=None):
    filters = filters or {}

    today = datetime.today().date()
    date_range = [today - timedelta(days=i) for i in range(7)]

    data = []
    for date in date_range:
    
        start_datetime = datetime.combine(date, datetime.min.time())
        
        end_datetime = datetime.combine(date, datetime.max.time())
        
        open_count = frappe.db.count("Task Detail", filters={
            "status": "Open",
            "creation": ["between", [start_datetime, end_datetime]]
        })
        completed_count = frappe.db.count("Task Detail", filters={
            "status": "Completed",
            "creation": ["between", [start_datetime, end_datetime]]
        })
        created_count = frappe.db.count("Task Detail", filters={
            "creation": ["between", [start_datetime, end_datetime]]
        })
        
        data.append([date.strftime('%Y-%m-%d'), open_count, completed_count, created_count])

    columns = ["Date", "Open", "Completed", "Created"]

    print("\n\n\n\n dataaa",data)

    chart_data = {
        'data': {
            'labels': [row[0] for row in data], 
            'datasets': [
                {
                    'name': 'Open',
                    'values': [row[1] for row in data]
                },
                {
                    'name': 'Completed',
                    'values': [row[2] for row in data]
                },
                {
                    'name': 'Created',
                    'values': [row[3] for row in data]
                }
            ]
        },
        'type': 'bar',
        
    }
    # open_total = sum(row[1] for row in data)
    # completed_total = sum(row[2] for row in data)
    # created_total = sum(row[3] for row in data)
    # report_summary = [
    #     {"label": "Open Tasks", "value": open_total, 'indicator': 'Blue'},
    #     {"label": "Completed Tasks", "value": completed_total, 'indicator': 'Green'},
    #     {"label": "Total Tasks Created", "value": created_total, 'indicator': 'Orange'}
    # ]

    return columns, data, None, chart_data
