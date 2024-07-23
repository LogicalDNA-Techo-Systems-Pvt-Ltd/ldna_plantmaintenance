import frappe
from frappe.model.document import Document
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


        if self.actual_start_date and getdate(self.actual_start_date) < getdate(nowdate()):
            frappe.throw("Actual Start Date should be greater than or equal to the current date.")

        self.update_task_status()
   
    def update_task_status(self):
        today = getdate(nowdate())
        if self.plan_end_date and getdate(self.plan_end_date) < today:
            self.status = 'Overdue'
        
@frappe.whitelist()
def send_for_approval(docname):
    task_detail = frappe.get_doc('Task Detail', docname)
    all_shortages_zero = True
    for item in task_detail.material_issued:
        if item.shortage > 0:
            all_shortages_zero = False
            break
        
    if all_shortages_zero:
        send_approval_email(task_detail)
        return {"message": "Email sent to Manager for material approval."}
    else:
        return {"message": "Cannot send approval email due to shortages."}

def send_approval_email(task_detail):
    subject = "Approval Request for Material required for {}".format(task_detail.name)
    message = "Please review and issue the material with ID: {}".format(task_detail.name)
    recipient = task_detail.approver  

    if recipient:
        frappe.sendmail(
            recipients=recipient,
            subject=subject,
            message=message,
            now=True
        )