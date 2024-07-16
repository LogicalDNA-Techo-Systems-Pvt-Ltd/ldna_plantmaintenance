# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from frappe.utils import nowdate, getdate


# class TaskDetail(Document):
#     def validate(self):
#         previous_doc = self.get_doc_before_save()
#         if previous_doc:
#             previous_acceptance_criteria = previous_doc.get("acceptance_criteria")
#             current_acceptance_criteria = self.acceptance_criteria

#             # Check for changes in acceptance criteria for binary parameters
#             if self.parameter_type == 'Binary':
#                 if previous_acceptance_criteria != current_acceptance_criteria:
#                     self.result = 'Fail'
#                 else:
#                     self.result = 'Pass'
#             # Check for list parameters
#             elif self.parameter_type == 'List':
#                 if self.acceptance_criteria_for_list and self.parameter_dropdown != self.acceptance_criteria_for_list:
#                     self.result = 'Fail'
#                 else:
#                     self.result = 'Pass'
                    
#     def update_task_status():
#         today = getdate(nowdate())
#         overdue_tasks = frappe.get_all("Task Detail", filters={"plan_end_date": ["<", today], "status": ["not in", ["Complete", "Overdue"]]}, fields=["name"])
#         for task in overdue_tasks:
#             frappe.db.set_value("Task Detail", task.name, "status", "Overdue")
#         frappe.db.commit()

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate

class TaskDetail(Document):
    def validate(self):
        previous_doc = self.get_doc_before_save()

        # Validate acceptance criteria changes for Binary parameters
        if self.parameter_type == 'Binary':
            if previous_doc and previous_doc.acceptance_criteria != self.acceptance_criteria:
                self.result = 'Fail'
            else:
                self.result = 'Pass'

        # Validate acceptance criteria for List parameters
        elif self.parameter_type == 'List':
            if self.acceptance_criteria_for_list and self.parameter_dropdown != self.acceptance_criteria_for_list:
                self.result = 'Fail'
            else:
                self.result = 'Pass'

        # Check Actual Start Date against current date
        if self.actual_start_date and getdate(self.actual_start_date) < getdate(nowdate()):
            frappe.throw("Actual Start Date should be greater than or equal to the current date.")

        # Validate if actual_value matches acceptance_criteria for Binary parameters
        if self.parameter_type == 'Binary':
            if self.actual_value != self.acceptance_criteria:
                self.result = 'Fail'
            else:
                self.result = 'Pass'
