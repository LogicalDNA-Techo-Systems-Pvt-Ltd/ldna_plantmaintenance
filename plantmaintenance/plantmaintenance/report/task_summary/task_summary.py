
import frappe
from datetime import datetime, timedelta
def execute(filters=None):
    filters = filters or {}
    date_filter = filters.get('date_filter', 'daily').lower()  

    today = datetime.today().date()
    if date_filter == 'daily':
        date_range = [today - timedelta(days=i) for i in range(7)]
    elif date_filter == 'weekly':
        date_range = [today - timedelta(weeks=i, days=today.weekday()) for i in range(4)]
    elif date_filter == 'monthly':
        date_range = [datetime(today.year, month, 1) for month in range(1, 13)]
    elif date_filter == 'yearly':
        date_range = [today.replace(month=1, day=1) - timedelta(days=365*i) for i in range(5)]
    else:
        frappe.throw(f"Unsupported date filter: {date_filter}")

    data = []
    for date in date_range:
        if date_filter == 'daily':
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())
            label = date.strftime('%Y-%m-%d')
        elif date_filter == 'weekly':
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = start_datetime + timedelta(days=6, hours=23, minutes=59, seconds=59)
            label = f"{start_datetime.strftime('%Y-%m-%d')} - {end_datetime.strftime('%Y-%m-%d')}"
        elif date_filter == 'monthly':
            start_datetime = datetime.combine(date, datetime.min.time())
            next_month = (start_datetime.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_datetime = next_month - timedelta(seconds=1)
            label = start_datetime.strftime('%B')  
        elif date_filter == 'yearly':
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = start_datetime.replace(year=start_datetime.year + 1) - timedelta(seconds=1)
            label = date.strftime('%Y')

        # Count tasks within the calculated date range
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

        data.append([label, open_count, completed_count, created_count])

    # Sorting based on filter type
    if date_filter == 'daily':
        data.sort(key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
    elif date_filter == 'monthly':
        data.sort(key=lambda x: datetime.strptime(x[0], '%B').month)
    elif date_filter == 'weekly':
        data.sort(key=lambda x: datetime.strptime(x[0].split(' - ')[0], '%Y-%m-%d'))
    elif date_filter == 'yearly':
        data.sort(key=lambda x: int(x[0]))

    columns = ["Date", "Open", "Completed", "Created"]
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
        "colors": ["#fc4f51", "#78d6ff", "#7575ff"],
        "barOptions": {"stacked": True},
    }
    return columns, data, None, chart_data
