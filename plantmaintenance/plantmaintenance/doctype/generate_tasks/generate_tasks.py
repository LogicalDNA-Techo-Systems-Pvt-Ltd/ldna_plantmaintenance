# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt
# class GenerateTasks(Document):
# 	pass

import frappe
import uuid
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, add_days
import calendar
from openpyxl import Workbook, load_workbook
from io import BytesIO
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import os
import openpyxl
import base64
import io
from frappe.exceptions import TimestampMismatchError

class GenerateTasks(Document):
    pass

generated_unique_keys = set()

@frappe.whitelist()
def load_tasks(plant, location, functional_location, plant_section, work_center, start_date=None, end_date=None):
    global generated_unique_keys
    if not start_date or not end_date:
        return frappe.msgprint("Please provide both start date and end date.")

    current_user = frappe.session.user

    user_work_center = frappe.get_value('User Work Center', {'user': current_user}, 'name')
    
    assigned_work_centers = frappe.get_all('Work Center CT', filters={'parent': user_work_center}, pluck='work_center')
    
    if work_center not in assigned_work_centers  or not user_work_center:
        return frappe.msgprint(f"You are not assigned to {work_center} work center")

    filters = {
        "plant": plant,
        "location": location,
        "functional_location": functional_location,
        "section": plant_section,
        "work_center": work_center,
    }

    equipment_list = frappe.get_all('Equipment', filters={**filters, 'on_scrap': 0,'activity_group_active':1}, fields=['equipment_code', 'equipment_name', 'activity_group'])
    on_scrap_equipment = frappe.get_all('Equipment', filters={**filters, 'on_scrap': 1}, fields=['equipment_code'])
    
    start_date = getdate(start_date)
    today_date = getdate(nowdate())
    end_date = getdate(end_date)

    if not (today_date <= start_date <= end_date):
        return frappe.msgprint("Previous dates are not allowed.")

    tasks = []
    if not equipment_list:
        return frappe.msgprint("Equipment not found for the provided filters.")

    for equipment in equipment_list:

        if not equipment.activity_group:
            continue
        
        activities = frappe.get_all('Activity CT', filters={'parent': equipment.activity_group}, fields=['activity'])

        if not activities:
            continue

        for activity in activities:
            activity_details = frappe.get_doc('Activity', activity.activity)

            parameters = frappe.get_all('Parameter CT', filters={'parent': activity.activity}, fields=[
                'parameter', 'frequency', 'day_of_month', 'monday', 'tuesday', 'wednesday',
                'thursday', 'friday', 'saturday', 'sunday', 'date_of_year'
            ])

            if not parameters:
                continue

            for parameter in parameters:
                frequency = parameter.frequency
                dates = []

                if frequency == 'Daily':
                    dates = [add_days(start_date, i) for i in range((end_date - start_date).days + 1)]

                elif frequency == 'Weekly':
                    selected_days = []
                    if parameter.monday:
                        selected_days.append('Monday')
                    if parameter.tuesday:
                        selected_days.append('Tuesday')
                    if parameter.wednesday:
                        selected_days.append('Wednesday')
                    if parameter.thursday:
                        selected_days.append('Thursday')
                    if parameter.friday:
                        selected_days.append('Friday')
                    if parameter.saturday:
                        selected_days.append('Saturday')
                    if parameter.sunday:
                        selected_days.append('Sunday')

                    for day in selected_days:
                        current_date = start_date
                        while current_date.weekday() != list(calendar.day_name).index(day):
                            current_date += timedelta(days=1)
                        if start_date <= current_date <= end_date:
                            dates.append(current_date)

                        while current_date <= end_date:
                            current_date += timedelta(weeks=1)
                            if start_date <= current_date <= end_date:
                                dates.append(current_date)

                elif frequency == 'Monthly':
                    day_of_month = parameter.day_of_month or 1
                    current_date = start_date

                    while current_date <= end_date:
                        last_day_of_month = calendar.monthrange(current_date.year, current_date.month)[1]

                        if day_of_month > last_day_of_month:
                            task_date = current_date.replace(day=last_day_of_month)
                        else:
                            task_date = current_date.replace(day=day_of_month)

                        if start_date <= task_date <= end_date:
                            dates.append(task_date)

                        current_date += relativedelta(months=1)

                    next_month_first_day = end_date.replace(day=day_of_month) if day_of_month <= calendar.monthrange(end_date.year, end_date.month)[1] else end_date.replace(day=calendar.monthrange(end_date.year, end_date.month)[1])
                    if start_date <= next_month_first_day <= end_date:
                        dates.append(next_month_first_day)
                                            

                elif frequency == 'Yearly':
                    date_of_year = getdate(parameter.date_of_year)
                    year_start_date = start_date.replace(month=date_of_year.month, day=date_of_year.day)
                    
                    dates = []

                    if start_date <= year_start_date <= end_date:
                        dates.append(year_start_date)
                    
                    current_year = start_date.year
                    while year_start_date <= end_date:
                        if start_date <= year_start_date <= end_date:
                            if year_start_date.year != datetime.now().year:
                                dates.append(year_start_date)
                            elif year_start_date.year == datetime.now().year:
                                if not any(date.year == datetime.now().year for date in dates):
                                    dates.append(year_start_date)
                        
                        current_year += 1
                        year_start_date = year_start_date.replace(year=current_year)
                    
                    dates = [date for date in dates if start_date <= date <= end_date]

                

                for date in dates:
                    date_obj = getdate(date)
                    key_context = (equipment.equipment_code, activity_details.activity_name, parameter.parameter, parameter.frequency, date)
                    existing_key = next((key for key, context in generated_unique_keys if context == key_context), None)
                    if existing_key is None:
                        unique_key = 'lbvrq8' + str(uuid.uuid4())[:8]
                        generated_unique_keys.add((unique_key, key_context))
                    else:
                        unique_key = existing_key

                    parameter_doc = frappe.get_doc("Parameter", parameter.parameter)
                    parameter_type = parameter_doc.parameter_type

                    task = {
                        'equipment_code': equipment.equipment_code,
                        'equipment_name': equipment.equipment_name,
                        'activity_group':equipment.activity_group,
                        'activity': activity_details.activity_name,
                        'parameter': parameter.parameter,
                        'frequency': frequency,
                        'date': date,
                        'day': calendar.day_name[date_obj.weekday()],
                        'unique_key': unique_key[:10]
                    }

                    tasks.append(task)

                    task_exists = frappe.db.exists(
                        'Task Detail',
                        {
                            'equipment_code': task['equipment_code'],
                            'activity': task['activity'],
                            'parameter': task['parameter'],
                            'frequency': task['frequency'],
                            'plan_start_date': task['date']
                        }
                    )

                    if not task_exists:
                        if not frappe.db.exists('Task Detail', {'unique_key': unique_key[:10]}):
                            task_detail = frappe.new_doc("Task Detail")
                            task_detail.update({
                                "approver": frappe.session.user,
                                "equipment_code": task['equipment_code'],
                                "equipment_name": task['equipment_name'],
                                "activity_group":task['activity_group'],
                                "work_center": work_center,
                                "plant_section": plant_section,
                                "plan_start_date": task['date'],
                                "activity": task['activity'],
                                "parameter": task['parameter'],
                                "frequency": task['frequency'],
                                "day": task['day'],
                                "date": task['date'],
                                "unique_key": task['unique_key'],
                                "parameter_type": parameter_type 
                            })
                            task_detail.insert(ignore_permissions=True)

    if not tasks:
        return frappe.msgprint("No tasks found for the provided filters.")
                            
    return tasks

