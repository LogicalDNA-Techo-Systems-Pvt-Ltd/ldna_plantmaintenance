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

class Allocation(Document):
    pass

generated_unique_keys = set()


@frappe.whitelist()
def load_tasks(plant, location, plant_section, work_center, start_date=None, end_date=None, equipment=None):
    global generated_unique_keys

    today = getdate()
    if start_date and end_date and getdate(start_date) > getdate(end_date):
        frappe.throw("Start Date must be less than or equal to End Date.")

    if start_date and getdate(start_date) < today:
        frappe.throw("Start Date cannot be before today's date.")

    settings_doc = frappe.get_single('Settings')
    start_date = getdate(start_date) if start_date else max(today, getdate(settings_doc.start_date))
    end_date = getdate(end_date) if end_date else getdate(settings_doc.end_date)


    current_user = frappe.session.user
    user_work_center = frappe.get_value('User Work Center', {'user': current_user}, 'name')
    
    assigned_work_centers = frappe.get_all('Work Center CT', filters={'parent': user_work_center}, pluck='work_center')
    
    if work_center not in assigned_work_centers or not assigned_work_centers or not user_work_center:
        return frappe.msgprint(f"You are not assigned to {work_center} work center")

    filters = {
        "plant": plant,
        "location": location,
        "section": plant_section,
        "work_center": work_center,
        "on_scrap": 0, 
        "activity_group_active": 1 
    }

    if equipment:
        filters["equipment_code"] = equipment

    equipment_list = frappe.get_all('Equipment', filters=filters, fields=['equipment_code', 'equipment_name', 'activity_group'])

    if not equipment_list:
        return frappe.msgprint("No equipment found for the provided filters.")

    settings_doc = frappe.get_single('Settings')
    start_date = getdate(start_date) if start_date else getdate(settings_doc.start_date)
    end_date = getdate(end_date) if end_date else getdate(settings_doc.end_date)

    tasks = []

    for equipment_item in equipment_list:
        if not equipment_item.activity_group:
            continue

        activities = frappe.get_all('Activity CT', filters={'parent': equipment_item.activity_group}, fields=['activity'])
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
                    date_range = (end_date - start_date).days + 1
                    dates = [add_days(start_date, i) for i in range(date_range) if start_date <= add_days(start_date, i) <= end_date]

                elif frequency == 'Weekly':
                    selected_days = []
                    if parameter.monday: selected_days.append('Monday')
                    if parameter.tuesday: selected_days.append('Tuesday')
                    if parameter.wednesday: selected_days.append('Wednesday')
                    if parameter.thursday: selected_days.append('Thursday')
                    if parameter.friday: selected_days.append('Friday')
                    if parameter.saturday: selected_days.append('Saturday')
                    if parameter.sunday: selected_days.append('Sunday')

                    for day in selected_days:
                        current_date = start_date
                        while current_date.weekday() != list(calendar.day_name).index(day):
                            current_date += timedelta(days=1)
                        while current_date <= end_date:
                            dates.append(current_date)
                            current_date += timedelta(weeks=1)

                elif frequency == 'Monthly':
                    day_of_month = parameter.day_of_month or 1
                    current_date = start_date

                    if current_date.day > day_of_month:
                        current_date = (current_date + relativedelta(months=1)).replace(day=1)
                    
                    while current_date <= end_date:
                        if day_of_month <= calendar.monthrange(current_date.year, current_date.month)[1]:
                            current_date = current_date.replace(day=day_of_month)
                        else:
                            current_date = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])

                        if current_date >= start_date and current_date <= end_date:
                            dates.append(current_date)

                        current_date += relativedelta(months=1)

                elif frequency == 'Yearly':
                    date_of_year = getdate(parameter.date_of_year)
                    year_date = start_date.replace(month=date_of_year.month, day=date_of_year.day)
                    while year_date <= end_date:
                        if year_date >= start_date:
                            dates.append(year_date)
                        year_date += relativedelta(years=1)

                for date in dates:
                    date_obj = getdate(date)
                    key_context = (equipment_item.equipment_code, activity_details.activity_name, parameter.parameter, parameter.frequency, date)
                    existing_key = next((key for key, context in generated_unique_keys if context == key_context), None)

                    if existing_key is None:
                        unique_key = 'lbvrq8' + str(uuid.uuid4())[:8]
                        generated_unique_keys.add((unique_key, key_context))
                    else:
                        unique_key = existing_key

                    parameter_doc = frappe.get_doc("Parameter", parameter.parameter)
                    parameter_type = parameter_doc.parameter_type

                    task = {
                        'equipment_code': equipment_item.equipment_code,
                        'equipment_name': equipment_item.equipment_name,
                        'activity_group': equipment_item.activity_group,
                        'activity': activity_details.activity_name,
                        'parameter': parameter.parameter,
                        'frequency': frequency,
                        'date': date,
                        'day': calendar.day_name[date_obj.weekday()],
                        'unique_key': unique_key[:10]
                    }

                    tasks.append(task)

                    if not frappe.db.exists('Task Detail', {'unique_key': unique_key[:10]}):
                        task_detail = frappe.new_doc("Task Detail")
                        task_detail.update({
                            "approver": frappe.session.user,
                            "equipment_code": task['equipment_code'],
                            "equipment_name": task['equipment_name'],
                            "activity_group": task['activity_group'],
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


@frappe.whitelist()
def download_tasks_excel_for_allocation(tasks):
    doc = frappe.get_doc("Allocation")
    tasks = frappe.parse_json(tasks)

    wb = Workbook()
    ws = wb.active
    ws.title = "Tasks"


    headers = ['Unique Key','Equipment Code', 'Equipment Name', 'Activity Group','Activity', 'Parameter', 'Frequency', 'Assign To', 'Date', 'Day','Priority']
    ws.append(headers)


    for task in tasks:
        task_date = getdate(task.get('date'))
        row = [
            task.get('unique_key'),
            task.get('equipment_code'),
            task.get('equipment_name'),
            task.get('activity_group'),
            task.get('activity'),
            task.get('parameter'),
            task.get('frequency'),
            task.get('assign_to'),
            task_date.strftime('%Y-%m-%d') if task_date else None,
            task.get('day'),
            task.get('priority'),
        ]
        ws.append(row)


    virtual_workbook = BytesIO()
    wb.save(virtual_workbook)
    virtual_workbook.seek(0)
    file_data = virtual_workbook.read()


    file_name = f'Task_Allocation_{nowdate()}.xlsx'
    file_doc = frappe.get_doc({
        'doctype': 'File',
        'file_name': file_name,
        'content': file_data,
        'is_private': 0
    })
    file_name = f'Task_Detail_{nowdate()}.xlsx'
    file_doc = frappe.get_doc({
        'doctype': 'File',
        'file_name': file_name,
        'content': file_data,
        'is_private': 0
    })
    file_doc.save(ignore_permissions=True)


    return file_doc.file_url
 

@frappe.whitelist()
def upload_tasks_excel_for_allocation(file, allocation_name):
    folder_path = ''
    actual_file_name = ''

    if file.startswith("/private/files/"):
        actual_file_name = file.replace("/private/files/", '')
        folder_path = os.path.join(os.path.abspath(frappe.get_site_path()), "private", "files")
    else:
        actual_file_name = file.replace("/files/", '')
        folder_path = os.path.join(os.path.abspath(frappe.get_site_path()), "public", "files")

    source_file = os.path.join(folder_path, actual_file_name)
    wb = load_workbook(source_file)
    sheet = wb.active

    headers = [sheet.cell(row=1, column=i).value for i in range(1, sheet.max_column + 1)]
    allocation_details = []

    missing_assign_to_count = 0
    mismatch_people_count = 0

    for row in range(2, sheet.max_row + 1):
        row_data = {}
        is_blank_row = True
        for col_num in range(1, sheet.max_column + 1):
            cell_value = sheet.cell(row=row, column=col_num).value
            if cell_value is not None and cell_value != '':
                is_blank_row = False
                break

        if is_blank_row:
            continue

        for col_num in range(1, sheet.max_column + 1):
            cell_value = sheet.cell(row=row, column=col_num).value
            row_data[headers[col_num - 1]] = cell_value

        assign_to = row_data.get('Assign To')
        parameter_doc = frappe.get_doc("Parameter", row_data.get('Parameter'))

        if assign_to is None or assign_to.strip() == '':
            missing_assign_to_count += 1
        elif parameter_doc.number_of_maintenance_person != len(assign_to.split(',')):
            mismatch_people_count += 1

        allocation_details.append({
            'equipment_code': row_data.get('Equipment Code'),
            'equipment_name': row_data.get('Equipment Name'),
            'activity_group': row_data.get('Activity Group'),
            'activity': row_data.get('Activity'),
            'parameter': row_data.get('Parameter'),
            'frequency': row_data.get('Frequency'),
            'date': getdate(row_data.get('Date')),
            'assign_to': assign_to,
            'priority': row_data.get('Priority'),
            'day': row_data.get('Day')
        })

    
    for detail in allocation_details:
        filters = {
            'equipment_code': detail['equipment_code'],
            'activity': detail['activity'],
            'parameter': detail['parameter'],
            'plan_start_date': detail['date']
        }

        task_details = frappe.get_all('Task Detail', filters=filters, fields=['name'])

        if not task_details:
            frappe.log_error(f"No tasks found for filters: {filters}", "Task Update Error")
            continue

        for task in task_details:
            try:
                task_detail = frappe.get_doc('Task Detail', task.name)
                task_detail.assigned_to = detail['assign_to']
                task_detail.priority = detail['priority']
                task_detail.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Error updating task {task.name}: {str(e)}", "Task Update Error")

    error_message = ""
    if missing_assign_to_count > 0:
        error_message += f"{missing_assign_to_count} rows are missing 'Assign To' person. "
    if mismatch_people_count > 0:
        error_message += f"{mismatch_people_count} rows have a mismatch in the number of people assigned."

    if error_message:
        frappe.msgprint(error_message)

    return {"message": "Excel import successful with warnings!" if error_message else "Excel import successful!", "allocation_details": allocation_details}

