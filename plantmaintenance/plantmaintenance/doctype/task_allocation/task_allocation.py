import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, add_days, add_months, add_years
from openpyxl import Workbook
from io import BytesIO
import calendar

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
            "expected_start_date": detail.date,
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
def load_tasks(work_center, plant_section):
    if not work_center or not plant_section:
        frappe.throw(_("Please select Work Center and Plant Section before loading tasks."))

    equipment_list = frappe.get_list('Equipment', filters={'work_center': work_center, 'plant_section': plant_section}, fields=['equipment_code', 'equipment_name', 'activity_group'])

    if not equipment_list:
        frappe.throw(_("No equipment found for the selected Work Center and Plant Section."))

    tasks_to_add = []

    for equipment in equipment_list:
        if not equipment.activity_group:
            continue

        activity_group = frappe.get_doc('Activity Group', equipment.activity_group)
        for activity in activity_group.activity:
            activity_doc = frappe.get_doc('Activity', activity.activity_name)
            for parameter in activity_doc.parameter:
                task_dates = get_task_dates(parameter.frequency, parameter.range)
                for task_date in task_dates:
                    tasks_to_add.append({
                        'equipment_code': equipment.equipment_code,
                        'equipment_name': equipment.equipment_name,
                        'date': task_date,
                        'frequency': parameter.frequency,
                        'task_status': 'Open',
                        'activity_name': activity.activity_name,
                        'parameter': parameter.parameter,
                        'day': calendar.day_name[task_date.weekday()]
                    })

    return tasks_to_add

def get_task_dates(frequency, range_value=None):
    start_date = getdate(nowdate())
    dates = []

    if frequency == 'Daily':
        dates = [add_days(start_date, i) for i in range(15)]
    elif frequency == 'Weekly':
        dates = [add_days(start_date, i * 7) for i in range(12)]
    elif frequency == 'Monthly':
        dates = [add_months(start_date, i) for i in range(6)]
    elif frequency == 'Yearly':
        dates = [add_years(start_date, i) for i in range(1)]
    elif frequency == 'Randomly':
        dates = [add_days(start_date, i * range_value) for i in range(5)]

    return dates

@frappe.whitelist()
def download_tasks_excel_for_task_allocation(tasks):
    tasks = frappe.parse_json(tasks)

    wb = Workbook()
    ws = wb.active
    ws.title = "Tasks"

    headers = ['Equipment Code', 'Equipment Name', 'Activity', 'Parameter', 'Parameter Type', 'Min Value', 'Max Value', 'List Text', 'Frequency', 'Assign TO', 'Date', 'Day']
    ws.append(headers)

    for task in tasks:
        task_date = getdate(task.get('date'))
        row = [
            task.get('equipment_code'),
            task.get('equipment_name'),
            task.get('activity_name'),
            task.get('parameter'),
            task.get('parameter_type'),
            task.get('min_value'),
            task.get('max_value'),
            task.get('list_text'),
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
