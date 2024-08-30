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
        
        if self.status == "Pending Approval":
            self.send_for_approval_date = nowdate()
        elif self.status == "Approved":
            self.approved_date = nowdate()
        elif self.status == "Completed":
            self.completion_date = nowdate()
        

    
@frappe.whitelist()
def send_for_approval(docname):
    task_detail = frappe.get_doc('Task Detail', docname)
    
    for item in task_detail.material_issued:
        if item.status != 'Material Issued' and item.shortage == 0 and item.spare:
            frappe.db.set_value('Material Issue', item.name, 'status', 'Pending Approval')
            if not item.approval_date:  
                frappe.db.set_value('Material Issue', item.name, 'approval_date', frappe.utils.nowdate())
            if item.status == 'Material Rejected':
                frappe.db.set_value('Material Issue', item.name, 'status', 'Material Rejected')

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
def mark_as_issued(docname, selected_rows=None):
    doc = frappe.get_doc("Task Detail", docname)
    selected_rows = frappe.parse_json(selected_rows) if selected_rows else []

    for item in doc.material_issued:
        if item.status == "Pending Approval" and (not selected_rows or item.name in selected_rows):
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
    return True

@frappe.whitelist()
def mark_as_rejected(docname, selected_rows=None):
    doc = frappe.get_doc('Task Detail', docname)
    selected_rows = frappe.parse_json(selected_rows) if selected_rows else []

    for item in doc.material_issued:
        if item.status == "Pending Approval" and (not selected_rows or item.name in selected_rows):
            item.status = "Material Rejected"

    doc.save()
    return True


    
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
def validate_before_workflow_action(doc, method):
    if doc.material_issued:
        pending_approval_exists = any(row.status == "Pending Approval" for row in doc.material_issued)
        if pending_approval_exists and (doc.workflow_state == "Approval Pending"):
            frappe.throw(_("The Material Issued status is Pending Approval, so you cannot continue."))

    if doc.workflow_state != "Open" and not doc.assigned_to:
        frappe.throw(_("The task cannot proceed without an assigned user. Please ensure the task is assigned before continuing."))
    
    if doc.workflow_state == "Approval Pending":
        mandatory_fields = {
            'actual_value': doc.parameter_type == "Binary",
            'parameter_dropdown': doc.parameter_type == "List",
            'remark': doc.type != "Preventive",
            'breakdown_reason': doc.type == "Breakdown",
            'service_call': doc.type == "Breakdown"
        }

        for fieldname, condition in mandatory_fields.items():
            if condition and not getattr(doc, fieldname, None):
               field_label = frappe.get_meta(doc.doctype).get_field(fieldname).label
               error_message = _("{0} is a mandatory field.").format(field_label)
               frappe.throw(error_message)

def update_overdue_status():
    try:
        today = nowdate()

        overdue_tasks = frappe.get_all('Task Detail', filters={
            'plan_start_date': ['<', today],
            'status': ['in', ['Open', 'In Progress']]
        })

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
        
        

#Fetch the task detail in equipment's history tab if task is completed or rejected PD.
@frappe.whitelist()
def equipment_task_details(doc, method=None):
    
    task_detail = doc
    if task_detail.equipment_code:
        equipment_doc = frappe.get_doc("Equipment", task_detail.equipment_code)
        task_detail_doc = frappe.get_doc("Task Detail", task_detail.name)
        
        valid_statuses = ["Completed", "Rejected", "Overdue","Cancelled"]
        valid_workflow_states = ["Approved", "Rejected","Cancelled"]

        def is_task_detail_existing(child_table, task_name, status):
            for detail in child_table:
                if detail.task == task_name and detail.status == status:
                    return True
            return False

        def should_create_entry(status, workflow_state):
            if status == "Completed":
                return not is_task_detail_existing(equipment_doc.equipment_task_details, task_detail.name, "Completed")
            elif status == "Rejected" and workflow_state == "Rejected":
                return not is_task_detail_existing(equipment_doc.equipment_task_details, task_detail.name, "Rejected")
            elif status == "Cancelled" and workflow_state == "Cancelled":
                return not is_task_detail_existing(equipment_doc.equipment_task_details, task_detail.name, "Cancelled")
            else:
                return not is_task_detail_existing(equipment_doc.equipment_task_details, task_detail.name, status)

        def is_material_entry_existing(child_table, task_name, material_name):
            for detail in child_table:
                if detail.task == task_name and detail.material_name == material_name:
                    return True
            return False

        if equipment_doc and task_detail.status in valid_statuses:
            if should_create_entry(task_detail.status, task_detail.workflow_state):
                detail = equipment_doc.append("equipment_task_details", {})
                detail.task = task_detail.name
                detail.parameter = task_detail.parameter
                detail.date = task_detail.creation
                
                if task_detail.status == "Overdue" and task_detail.workflow_state in valid_workflow_states:
                    detail.status = f"{task_detail.workflow_state} / {task_detail.status}"
                else:
                    detail.status = task_detail.status
                
                detail.passfail = task_detail.result

        if task_detail_doc.material_returned and task_detail.status in valid_statuses:
            material_returned = task_detail_doc.get("material_returned", [])
            if material_returned:
                for material_issue in material_returned:
                    if not is_material_entry_existing(equipment_doc.equipment_material_moment, task_detail.name, material_issue.material_code):
                        detail = equipment_doc.append("equipment_material_moment", {})
                        detail.task = task_detail.name
                        detail.material_type = material_issue.type
                        detail.material_name = material_issue.material_code
                        detail.quantity = material_issue.issue_quantity
                        detail.return_quantity = material_issue.return_quantity
                        detail.scrap = material_issue.scrap
                        detail.reusable = material_issue.reusable
                        detail.approval_date = material_issue.approval_date
                        detail.issued_date = material_issue.issued_date
                        
                    
        equipment_doc.save()