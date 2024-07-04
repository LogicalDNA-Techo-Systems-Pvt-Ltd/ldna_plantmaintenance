
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, add_days, add_months, add_years
from openpyxl import Workbook
from io import BytesIO
import calendar
import os
import openpyxl
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class TaskAllocation(Document):
    def on_update(self):
        if self.docstatus == 0:
            if not self.check_tasks_generated():
                self.create_task_details()

    def check_tasks_generated(self):
        return frappe.db.exists("Task Detail", {
            "work_center": self.work_center,
            "plant_section": self.plant_section,
        })

    def create_task_details(self):
        for detail in self.get('task_allocation_details'):
            self.create_task_detail(detail)

    def create_task_detail(self, detail):
        parameter_info = self.get_parameter_info(detail.parameter)
        task_detail = frappe.new_doc("Task Detail")
        task_detail.update({
            "task_allocation_id": self.name,
            "approver": frappe.session.user,
            "equipment_code": detail.equipment_code,
            "equipment_name": detail.equipment_name,
            "work_center": self.work_center,
            "plant_section": self.plant_section,
            "plan_start_date": detail.date,
            "assigned_to": detail.assign_to,
            "activity": detail.activity,
            "parameter": detail.parameter,
            "parameter_type": parameter_info.get('parameter_type'),
            "minimum_value": parameter_info.get('minimum_value'),
            "maximum_value": parameter_info.get('maximum_value'), 
            "text": ",".join(parameter_info.get('text', [])) if parameter_info.get('text') else None,
            "priority": detail.priority,
        })
        task_detail.insert(ignore_permissions=True)

    def get_parameter_info(self, parameter):
        parameter_doc = frappe.get_doc("Parameter", {"parameter": parameter})
        parameter_info = {
            "parameter_type": parameter_doc.parameter_type,
            "minimum_value": parameter_doc.minimum_value if parameter_doc.parameter_type == "Numeric" else None,
            "maximum_value": parameter_doc.maximum_value if parameter_doc.parameter_type == "Numeric" else None,
            "text": parameter_doc.text.split(',') if parameter_doc.parameter_type == "List" else None
        }
        return parameter_info


@frappe.whitelist()
def upload_tasks_excel_for_task_allocation(file,task_allocation_name):
    task_allocation_doc = frappe.get_doc("Task Allocation",task_allocation_name)    
   
    folder_path = ''
    actual_file_name = ''

    if file.startswith("/private/files/"):
        actual_file_name = file.replace("/private/files/", '')
        folder_path = os.path.join(os.path.abspath(frappe.get_site_path()), "private", "files")
    else:
        actual_file_name = file.replace("/files/", '')
        folder_path = os.path.join(os.path.abspath(frappe.get_site_path()), "public", "files")

    source_file = os.path.join(folder_path, actual_file_name)
 

    wb = openpyxl.load_workbook(source_file)
    sheet = wb.active

    headers = [sheet.cell(row=1, column=i).value for i in range(1, sheet.max_column + 1)]
    
    task_allocation_doc.set("task_allocation_details", [])

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
            
        print(task_allocation_doc.as_dict())
        task_allocation_doc.append("task_allocation_details", {
            'equipment_code': row_data.get('Equipment Code'),
            'equipment_name': row_data.get('Equipment Name'),
            'activity': row_data.get('Activity'),
            'parameter': row_data.get('Parameter'),
            'frequency': row_data.get('Frequency'),
            'assign_to': row_data.get('Assign TO'),
            'date': row_data.get('Date'),
            'day': row_data.get('Day')
        })

        task_allocation_doc.save()
        
   
        # equipment_code = row_data.get('Equipment Code')
        # equipment_name = row_data.get('Equipment Name')
        # activity = row_data.get('Activity')
        # parameter = row_data.get('Parameter')
        # frequency = row_data.get('Frequency')
        # assign_to = row_data.get('Assign TO')
        # date = row_data.get('Date')
        # day = row_data.get('Day')

    return True



@frappe.whitelist()
def check_tasks_generated(docname):
    if frappe.db.exists("Task Detail", {"task_allocation_id": docname}):
        return True
    return False

@frappe.whitelist()
def generate_tasks(docname):
    doc = frappe.get_doc("Task Allocation", docname)
    if doc:
        doc.create_task_details()
        return "Tasks have been generated successfully."
    else:
        return "Task Allocation document not found."





@frappe.whitelist()
def load_tasks(plant, location, functional_location, plant_section, work_center, end_date=None):
    filters = {
        "plant": plant,
        "location": location,
        "functional_location": functional_location,
        "section": plant_section,
        "work_center": work_center
    }

    equipment_list = frappe.get_all('Equipment', filters=filters, fields=['equipment_code', 'equipment_name', 'activity_group'])
    setting_doc = frappe.get_single('Setting')
    start_date = getdate(setting_doc.start_date)
    today_date = getdate(nowdate())
    end_date = getdate(end_date) if end_date else start_date + timedelta(days=120)

    tasks = []
    for equipment in equipment_list:
        activities = frappe.get_all('Activity CT', filters={'parent': equipment.activity_group}, fields=['activity'])
        
        for activity in activities:
            activity_details = frappe.get_doc('Activity', activity.activity)
            
            parameters = frappe.get_all('Parameter CT', filters={'parent': activity.activity}, fields=[
                'parameter', 'frequency', 'day_of_month', 'monday', 'tuesday', 'wednesday', 
                'thursday', 'friday', 'saturday', 'sunday'
            ])
            
            for parameter in parameters:
                frequency = parameter.frequency
                dates = []

                if frequency == 'Daily':
                    dates = [add_days(start_date, i) for i in range(15) if start_date <= add_days(start_date, i) <= end_date]

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
                        
                        while current_date <= (start_date + timedelta(days=90)) and (start_date <= current_date <= end_date):
                            current_date += timedelta(weeks=1)
                            if start_date <= current_date <= end_date:
                                dates.append(current_date)

                elif frequency == 'Monthly':
                    day_of_month = parameter.day_of_month or 1
                    current_date = start_date.replace(day=day_of_month)
                    if current_date < start_date:
                        current_date += relativedelta(months=1)
                    dates = [current_date + relativedelta(months=i) for i in range(6) if start_date <= current_date + relativedelta(months=i) <= end_date]

                elif frequency == 'Yearly':
                    dates = [add_years(start_date, i) for i in range(1) if start_date <= add_years(start_date, i) <= end_date]
                
                for date in dates:
                    date_obj = getdate(date)
                    task = {
                        'equipment_code': equipment.equipment_code,
                        'equipment_name': equipment.equipment_name,
                        'activity': activity_details.activity_name,
                        'parameter': parameter.parameter,
                        'frequency': frequency,
                        'date': date,
                        'day': calendar.day_name[date_obj.weekday()]
                    }
                    tasks.append(task)
                        
    return tasks



@frappe.whitelist()
def download_tasks_excel_for_task_allocation(tasks):
    tasks = frappe.parse_json(tasks)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Tasks"

    headers = ['Equipment Code', 'Equipment Name', 'Activity', 'Parameter', 'Frequency', 'Assign TO', 'Date','Day']
    ws.append(headers)

    for task in tasks:
        task_date = getdate(task.get('date'))
        row = [
            task.get('equipment_code'),
            task.get('equipment_name'),
            task.get('activity'), 
            task.get('parameter'),
            task.get('frequency'),
            task.get('assign_to'), 
            task_date.strftime('%Y-%m-%d') if task_date else None,
            task.get('day')

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
    file_doc.save(ignore_permissions=True)
    
    return file_doc.file_url

