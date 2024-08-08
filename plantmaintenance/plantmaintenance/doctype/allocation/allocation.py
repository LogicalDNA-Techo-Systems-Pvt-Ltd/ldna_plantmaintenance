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


class Allocation(Document):
    pass

generated_unique_keys = set()

@frappe.whitelist()
def load_tasks(plant, location, functional_location, plant_section, work_center, end_date=None):
    global generated_unique_keys
    filters = {
        "plant": plant,
        "location": location,
        "functional_location": functional_location,
        "section": plant_section,
        "work_center": work_center
    }

    equipment_list = frappe.get_all('Equipment', filters={**filters, 'on_scrap': 0}, fields=['equipment_code', 'equipment_name', 'activity_group'])
    on_scrap_equipment = frappe.get_all('Equipment', filters={**filters, 'on_scrap': 1}, fields=['equipment_code'])
    
    #equipment_list = frappe.get_all('Equipment', filters=filters, fields=['equipment_code', 'equipment_name', 'activity_group'])
    setting_doc = frappe.get_single('Setting')
    start_date = getdate(setting_doc.start_date)
    today_date = getdate(nowdate())
    end_date = getdate(end_date) if end_date else getdate(setting_doc.end_date)

    if not (start_date <= today_date <= end_date):
        return frappe.msgprint("Please ensure today's date is between the start date and end date.")

    tasks = []
    for equipment in equipment_list:
        activities = frappe.get_all('Activity CT', filters={'parent': equipment.activity_group}, fields=['activity'])

        for activity in activities:
            activity_details = frappe.get_doc('Activity', activity.activity)

            parameters = frappe.get_all('Parameter CT', filters={'parent': activity.activity}, fields=[
                'parameter', 'frequency', 'day_of_month', 'monday', 'tuesday', 'wednesday',
                'thursday', 'friday', 'saturday', 'sunday', 'date_of_year'
            ])

            for parameter in parameters:
                frequency = parameter.frequency
                dates = []

                if frequency == 'Daily':
                    dates = [add_days(today_date, i) for i in range(15) if today_date <= add_days(today_date, i) <= end_date]

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
                        current_date = today_date
                        while current_date.weekday() != list(calendar.day_name).index(day):
                            current_date += timedelta(days=1)
                        if today_date <= current_date <= end_date:
                            dates.append(current_date)

                        while current_date <= (today_date + timedelta(days=90)) and (today_date <= current_date <= end_date):
                            current_date += timedelta(weeks=1)
                            if today_date <= current_date <= end_date:
                                dates.append(current_date)

                elif frequency == 'Monthly':
                    day_of_month = parameter.day_of_month or 1
                    current_date = today_date.replace(day=day_of_month)
                    if current_date < today_date:
                        current_date += relativedelta(months=1)
                    dates = [current_date + relativedelta(months=i) for i in range(6) if today_date <= current_date + relativedelta(months=i) <= end_date]

                elif frequency == 'Yearly':
                    date_of_year = getdate(parameter.date_of_year)
                    if start_date <= date_of_year <= end_date:
                        years_range = range(today_date.year, end_date.year + 1)
                        dates = [date_of_year.replace(year=year) for year in years_range]

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
                        'activity': activity_details.activity_name,
                        'parameter': parameter.parameter,
                        'frequency': frequency,
                        'date': date,
                        'day': calendar.day_name[date_obj.weekday()],
                        'unique_key': unique_key[:10]
                    }
                    tasks.append(task)
                    # Check if the task exists before appending it to the tasks list
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
                        # tasks.append(task)

                        if not frappe.db.exists('Task Detail', {'unique_key': unique_key[:10]}):
                            task_detail = frappe.new_doc("Task Detail")
                            task_detail.update({
                                "approver": frappe.session.user,
                                "equipment_code": task['equipment_code'],
                                "equipment_name": task['equipment_name'],
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
                            
    return tasks

@frappe.whitelist()
def download_tasks_excel_for_allocation(tasks):
   tasks = frappe.parse_json(tasks)


   wb = Workbook()
   ws = wb.active
   ws.title = "Tasks"


   headers = ['Unique Key','Equipment Code', 'Equipment Name', 'Activity', 'Parameter', 'Frequency', 'Assign To', 'Date', 'Day','Priority']
   ws.append(headers)


   for task in tasks:
       task_date = getdate(task.get('date'))
       row = [
           task.get('unique_key'),
           task.get('equipment_code'),
           task.get('equipment_name'),
           task.get('activity'),
           task.get('parameter'),
           task.get('frequency'),
           task.get('assign_to'),
           task_date.strftime('%Y-%m-%d') if task_date else None,
           task.get('day'),
            task.get('priority')
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
            'activity': row_data.get('Activity'),
            'parameter': row_data.get('Parameter'),
            'frequency': row_data.get('Frequency'),
            'date': getdate(row_data.get('Date')),
            'assign_to': assign_to,
            'priority': row_data.get('Priority'),
            'day': row_data.get('Day'),
            'unique_key': row_data.get('Unique Key')
        })

    for detail in allocation_details:
        unique_key = detail['unique_key']
        task_exists = frappe.db.exists('Task Detail', {'unique_key': unique_key})

        if task_exists:
            task_detail = frappe.get_doc('Task Detail', task_exists)
            task_detail.assign_to = detail['assign_to']
            task_detail.priority = detail['priority']
            task_detail.save(ignore_permissions=True)

    error_message = ""
    if missing_assign_to_count > 0:
        error_message += f"{missing_assign_to_count} rows are missing 'Assign To' person. "
    if mismatch_people_count > 0:
        error_message += f"{mismatch_people_count} rows have a mismatch in the number of people assigned."

    if error_message:
        frappe.msgprint(error_message)

    return {"message": "Excel import successful with warnings!" if error_message else "Excel import successful!", "allocation_details": allocation_details}


@frappe.whitelist()
def clear_task_allocation_details(equipment_code):
    task_allocations = frappe.get_all('Task Allocation', filters={'equipment_code': equipment_code}, fields=['name'])
    for allocation in task_allocations:
        allocation_doc = frappe.get_doc('Task Allocation', allocation.name)
        allocation_doc.task_allocation_details = []
        allocation_doc.save(ignore_permissions=True)
        