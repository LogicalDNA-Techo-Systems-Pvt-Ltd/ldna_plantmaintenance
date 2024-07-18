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

