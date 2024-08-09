# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt
import frappe
import json
from frappe.model.document import Document
from frappe.utils import nowdate, getdate
from datetime import datetime, timedelta
from frappe.utils import nowdate, getdate

class TaskDetail(Document):
    def validate(self):
        if self.parameter_type == 'Binary':
            if not self.actual_value:
                self.result = ''
            elif self.actual_value != self.acceptance_criteria:
                self.result = 'Fail'
            else:
                self.result = 'Pass'

        elif self.parameter_type == 'List':
            if not self.parameter_dropdown:
                self.result = ''
            elif self.acceptance_criteria_for_list and self.parameter_dropdown != self.acceptance_criteria_for_list:
                self.result = 'Fail'
            else:
                self.result = 'Pass'

        self.material_issued_to_returned()

    def before_save(self):
        if self.plan_start_date:
            today = getdate(nowdate())
            start_date = getdate(self.plan_start_date) 
            if today > start_date:
                self.status = 'Overdue'

    def material_issued_to_returned(self):
        self.material_returned = []  

        for item in self.material_issued:
            if item.status == 'Material Issued':
                self.append("material_returned", {
                    "material_code": item.material_code,
                    "material_name": item.material_name,
                    "issue_quantity": item.required_quantity,
                    "approval_date": item.approval_date,
                    "issued_date": item.issued_date
                })

@frappe.whitelist()
def send_for_approval(docname):
    task_detail = frappe.get_doc('Task Detail', docname)
    send_approval_email(task_detail)
    return {"message": "Email sent to Manager for Material Approval."}
    
def send_approval_email(task_detail):
    url = frappe.utils.get_url_to_form('Task Detail', task_detail.name)
    subject = "Approval Request for Material required for {}".format(task_detail.name)
    message = """Please review and approve the material with ID: {}.<br> <a href="{}"> Click here to view the task</a>""".format(task_detail.name, url)    
    recipient = task_detail.approver  

    if recipient:
        frappe.sendmail(
            recipients=recipient,
            subject=subject,
            message=message,
            now=True
        )


@frappe.whitelist()
def mark_as_issued(docname):
    doc = frappe.get_doc("Task Detail", docname)
    for item in doc.material_issued:
        if item.status == "Pending Approval":
            item.status = "Material Issued"
            item.issued_date = getdate(nowdate()) 

    doc.save()
    
@frappe.whitelist()
def update_task_detail(equipment_code, activity,parameter, assign_to, date):

    task_details = frappe.get_all('Task Detail', filters={
        'equipment_code': equipment_code,
        'activity': activity,
        'parameter':parameter,
        'plan_start_date': date 
    })

    for task in task_details:
        doc = frappe.get_doc('Task Detail', task.name)
        doc.assigned_to = assign_to 
        doc.save()
        
    return True
