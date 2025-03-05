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
from plantmaintenance.plantmaintenance.notification.custom_notification.notification import send_onesignal_notification
# from plantmaintenance.plantmaintenance.notification.custom_notification.notification import send_onesignal_notification_for_approval
from frappe.utils import get_url_to_form
from frappe.utils import today

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
            task_for_approval(self)
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

    plan_start_date = getdate(doc.plan_start_date)
    today_date = getdate(today())
    if doc.workflow_state == "Work in Progress" and plan_start_date > today_date:
        frappe.throw(_("You cannot proceed to 'Work in Progress' because the Plan Start Date ({}) is in the future.").format(plan_start_date))
    
    if doc.workflow_state == "Approval Pending":
        mandatory_fields = {
            'actual_value': doc.parameter_type == "Binary",
            'parameter_dropdown': doc.parameter_type == "List",
            'remark': doc.type != "Preventive",
            'breakdown_reason': doc.type == "Breakdown",
            'service_call': doc.type == "Breakdown",
            'work_permit_number': True
        }

        if doc.parameter_type == "Numeric" and doc.parameter:
            parameter = frappe.get_doc("Parameter", doc.parameter) 
            num_readings = parameter.number_of_readings 

            for i in range(1, num_readings + 1): 
                fieldname = f"reading_{i}"
                reading_value = getattr(doc, fieldname, None)

                if not reading_value: 
                    field_label = frappe.get_meta(doc.doctype).get_field(fieldname).label
                    frappe.throw(_("{0} is a mandatory field.").format(field_label))


        for fieldname, condition in mandatory_fields.items():
            if condition and not getattr(doc, fieldname, None):
               field_label = frappe.get_meta(doc.doctype).get_field(fieldname).label
               frappe.throw(_("{0} is a mandatory field.").format(field_label))

    # if doc.workflow_state == "Approved" and not doc.process_manager:
    #     field_label = frappe.get_meta(doc.doctype).get_field("process_manager").label
    #     frappe.throw(_("{0} is a mandatory field.").format(field_label))


        

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

@frappe.whitelist()
def bulk_assign_tasks(task_names, assigned_users):
    if not isinstance(task_names, list):
        task_names = json.loads(task_names)
        
    if not isinstance(assigned_users, list):
        assigned_users = json.loads(assigned_users)
    
    for task_name in task_names:
        frappe.db.set_value('Task Detail', task_name, 'assigned_to', ', '.join(assigned_users))
        task_detail = frappe.get_doc('Task Detail', task_name)
        send_allocation_email(task_detail, assigned_users)
    
    frappe.db.commit()
    return "Tasks successfully assigned."

#send Email notification for bulk allocation and push notification

def send_allocation_email(task_detail, assigned_users):
    url = get_url_to_form('Task Detail', task_detail.name)
    subject = "Task Allocated {}".format(task_detail.name)
    message_template = """
        Hi Team,
        <br><br>
        I hope this message finds you well. I wanted to inform you that your task has been allocated to you by the maintenance manager.
        <br><br>
        Kindly review the details and proceed with the activity as outlined.
        <br>
        <a href="{url}">Click here to view the task</a>
        <br><br>
        Thanks,
        <br><br>
    """

   
    emails = []
    for user_full_name in assigned_users:
        user = frappe.get_all('User', filters={'full_name': user_full_name}, fields=['email'])
        if user:
            emails.append(user[0].email)
            
   
    for email in emails:
        contents = 'Task has been allocated to you !'
        url = get_url_to_form('Task Detail', task_detail.name)
        send_onesignal_notification(email,contents,url)
        message = message_template.format(url=url)
        frappe.sendmail(
            recipients=email,
            subject=subject,
            message=message,
            now=True
        )
        
# Push Notification for approval will be sent from here

def task_for_approval(task_detail):
    if task_detail.status == "Pending Approval":
        email = frappe.get_value("User", task_detail.approver, "email")
        url = get_url_to_form('Task Detail', task_detail.name)
        contents ="Task sent for approval !"
        send_onesignal_notification(email, contents, url)


# @frappe.whitelist()
# def get_user_roles(user):
#     user_doc = frappe.get_doc("User", user)
#     return [role.role for role in user_doc.roles]



@frappe.whitelist()
def get_assigned_maintenance_users():
    if not frappe.session.user:
        return []

    user_details = frappe.get_all("User Details", filters={"user_name": frappe.session.user}, pluck="name")

    if not user_details:
        return []

    assigned_users = frappe.get_all(
        "User Details CT",
        filters={"parent": user_details[0]},
        pluck="maintenance_users",
        ignore_permissions=True  
    )

    if not assigned_users:
        return []

    user_full_names = frappe.get_all(
        "User",
        filters={"name": ["in", assigned_users]},
        pluck="full_name"
    )

    return user_full_names


@frappe.whitelist()
def get_assigned_process_manager():
    if not frappe.session.user:
        return []

    user_details = frappe.get_all("User Details", filters={"user_name": frappe.session.user}, pluck="name")

    if not user_details:
        return []
    assigned_users = frappe.get_all(
        "Process Manager CT",
        filters={"parent": user_details[0]},
        pluck="process_manager",
        ignore_permissions=True  
    )

    if not assigned_users:
        return []

    user_full_names = frappe.get_all(
        "User",
        filters={"name": ["in", assigned_users]},
        pluck="full_name"
    )

    return user_full_names or []



@frappe.whitelist()
def get_all_maintenance_managers():
    maintenance_managers = frappe.db.sql("""
        SELECT full_name 
        FROM `tabUser`
        WHERE name IN (
            SELECT parent FROM `tabHas Role`
            WHERE role = 'Maintenance Manager'
        ) 
        AND name != 'Administrator' 
        AND enabled = 1
    """, as_list=True)

    return [manager[0] for manager in maintenance_managers]



@frappe.whitelist()
def get_maintenance_managers(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT name, full_name
        FROM `tabUser`
        WHERE name IN (
            SELECT parent FROM `tabHas Role`
            WHERE role = 'Maintenance Manager'
        ) 
        AND name != 'Administrator' 
        AND enabled = 1
        AND ({search_field} LIKE %(txt)s OR full_name LIKE %(txt)s)
        LIMIT %(start)s, %(page_len)s
    """.format(search_field=searchfield), {
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    })


# @frappe.whitelist()
# def get_total_tasks_till_today():
#     total_tasks = frappe.db.count("Task Detail", filters={"plan_start_date": ["<=", today()]})
    
#     return {
#         "value": total_tasks,
#         "fieldtype": "Int",  
#         "route": ["List", "Task Detail"],  
#         "route_options": {
#             "plan_start_date": ["<=", today()] 
#         }
#     }

@frappe.whitelist()
def get_total_tasks_till_today():
    total_tasks = frappe.get_list(
        "Task Detail",
        filters={"plan_start_date": ["<=", today()]},
        fields=["name"],  
        ignore_permissions=False  
    )
    
    return {
        "value": len(total_tasks), 
        "fieldtype": "Int",  
        "route": ["List", "Task Detail"],  
        "route_options": {
            "plan_start_date": ["<=", today()] 
        }
    }

@frappe.whitelist()
def get_open_tasks_till_today():
    total_tasks = frappe.get_list(
        "Task Detail",
        filters={
            "status": "Open",
            "plan_start_date": ["<=", today()]
        },
        fields=["name"],  
        ignore_permissions=False  
    )
    
    return {
        "value": len(total_tasks), 
        "fieldtype": "Int",  
        "route": ["List", "Task Detail"],  
        "route_options": {
            "status": "Open",
            "plan_start_date": ["<=", today()] 
        }
    }



@frappe.whitelist()
def get_assigned_tasks():
    user = frappe.session.user  
    user_full_name = frappe.db.get_value("User", user, "full_name")  

    if user == "Administrator":
        total_assigned = frappe.db.count("Task Detail", filters={"assigned_to": ["!=", ""]})
        route_options = {} 
    else:
        total_assigned = frappe.db.sql("""
            SELECT COUNT(*) 
            FROM `tabTask Detail`
            WHERE FIND_IN_SET(%s, REPLACE(assigned_to, ', ', ','))
        """, (user_full_name,))[0][0]
        route_options = {
            "assigned_to": ["in", [user_full_name, f"%{user_full_name}%"]]
        }

    return {
        "value": total_assigned,
        "fieldtype": "Int",
        "route": ["List", "Task Detail", "List"],  
        "route_options": route_options  
    }

@frappe.whitelist()
def get_unassigned_tasks():
    total_unassigned_tasks = frappe.get_list(
        "Task Detail",
        filters={
            "plan_start_date": ["<=", today()],
            "assigned_to": ["in", ["", None]] 
        },
        fields=["name"],
        ignore_permissions=False
    )

    return {
        "value": len(total_unassigned_tasks),
        "fieldtype": "Int",
        "route": ["List", "Task Detail"],
        "route_options": {
            "plan_start_date": ["<=", today()],
            "assigned_to": ["in", ["", None]]
        }
    }



def set_plan_start_date(doc, method):
   if doc.type in ["Breakdown", "Shutdown", "General", "Predictive"]:
       if not doc.plan_start_date:
           doc.plan_start_date = doc.creation 

# Hide future task from list view
@frappe.whitelist()
def get_filtered_tasks():
    doctype = frappe.local.form_dict.get("doctype")

    if doctype != "Task Detail":
        return frappe.call("frappe.desk.reportview.get")  

    user_filters = frappe.local.form_dict.get("filters")

    if isinstance(user_filters, str):
        user_filters = json.loads(user_filters)

    if not isinstance(user_filters, list):
        user_filters = []

    user_filters.append(["Task Detail", "plan_start_date", "<=", today()])

    frappe.local.form_dict["filters"] = json.dumps(user_filters)

    return frappe.call("frappe.desk.reportview.get")
