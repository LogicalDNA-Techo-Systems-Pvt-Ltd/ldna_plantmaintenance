# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt
import frappe
import json
from frappe.model.document import Document
from frappe.utils import nowdate, getdate
from datetime import datetime, timedelta
from frappe.utils import nowdate, getdate
from frappe import _
from frappe.utils.background_jobs import enqueue
import time

class TaskDetail(Document):
    
    website = frappe._dict(
        condition_field="published" 
    )

    def validate(self):
        if self.parameter:
            parameter_doc = frappe.get_doc('Parameter', self.parameter)
            self.acceptance_criteria = parameter_doc.acceptance_criteria
            self.acceptance_criteria_for_list = parameter_doc.acceptance_criteria_for_list

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
    
@frappe.whitelist()
def send_for_approval(docname):
    task_detail = frappe.get_doc('Task Detail', docname)
    
    for item in task_detail.material_issued:
        if item.status != 'Material Issued' and item.shortage == 0 and item.spare:
            frappe.db.set_value('Material Issue', item.name, 'status', 'Pending Approval')
            frappe.db.set_value('Material Issue', item.name, 'approval_date', frappe.utils.nowdate())

    send_approval_email(task_detail)
    return {"message": "Email sent to Manager for material approval."}


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
            
            doc.append("material_returned", {
                "material_code": item.material_code,
                "material_name": item.material_name,
                "issue_quantity": item.required_quantity,
                "approval_date": item.approval_date,
                "issued_date": item.issued_date
            })
    
    doc.save()

    
@frappe.whitelist()
def update_task_detail(equipment_code, parameter, activity, assign_to, date):
    retries = 3
    for _ in range(retries):
        try:
            task_details = frappe.get_all('Task Detail', filters={
                'equipment_code': equipment_code,
                'parameter': parameter,
                'activity': activity,
                'plan_start_date': date 
            })
            for task in task_details:
                frappe.db.set_value('Task Detail', task.name, 'assigned_to', assign_to)
            return True
        except frappe.exceptions.TimestampMismatchError:
            time.sleep(1)  # Introduce a small delay before retrying
        except Exception as e:
            frappe.log_error(str(e), "Task Update Error")
            frappe.throw(f"Error updating tasks: {str(e)}")





@frappe.whitelist()
def validate_before_workflow_action(doc,method):
    if doc.material_issued:
        pending_approval_exists = any(row.status == "Pending Approval" for row in doc.material_issued)
        if pending_approval_exists and (doc.workflow_state == "Approval Pending"):
            frappe.throw(_("The Material Issued status is Pending Approval, so you cannot continue."))


def update_overdue_status():
    try:
        today = nowdate()

        overdue_tasks = frappe.get_all('Task Detail', filters={
            'plan_start_date': ['<', today],
            'status': ['in', ['Open', 'In Progress']]
        })

        # Update status in smaller batches  
        batch_size = 50
        for i in range(0, len(overdue_tasks), batch_size):
            tasks_batch = overdue_tasks[i:i + batch_size]
            for task in tasks_batch:
                try:
                    doc = frappe.get_doc('Task Detail', task.name)
                    doc.status = 'Overdue' 
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
                except Exception as e:
                    frappe.log_error(f"Error updating task {task.name}: {str(e)}", "Update Overdue Status")
                    continue  

    except Exception as e:
        frappe.log_error(f"Scheduler event failed: {str(e)}", "Update Overdue Status")
        
        
        

def get_material_issued_data():
    # Fetch Material Issue records with status 'Pending Approval'
    material_issues = frappe.get_all('Material Issue', filters={
        'status': 'Pending Approval'
    }, fields=['parent', 'parenttype', 'material_code', 'material_name', 'available_quantity', 'required_quantity', 'shortage', 'status', 'approval_date', 'issued_date'])
    
    # Group by parent Task Detail
    task_material_data = {}
    for issue in material_issues:
        parent_task = issue.parent
        if parent_task not in task_material_data:
            task_material_data[parent_task] = []
        task_material_data[parent_task].append(issue)
    
    # Prepare list for frontend
    tasks_data = []
    for parent_task, issues in task_material_data.items():
        task_doc = frappe.get_doc('Task Detail', parent_task)
        for issue in issues:
            tasks_data.append({
                'task_name': task_doc.name,
                'material_code': issue.material_code,
                'material_name': issue.material_name,
                'available_quantity': issue.available_quantity,
                'required_quantity': issue.required_quantity,
                'shortage': issue.shortage,
                'status': issue.status,
                'approval_date': issue.approval_date,
                'issued_date': issue.issued_date,
            })
    
    return tasks_data

@frappe.whitelist(allow_guest=True)
def get_material_issued_records():
    return get_material_issued_data()

