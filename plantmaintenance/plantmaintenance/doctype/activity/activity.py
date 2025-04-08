# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt



import frappe
from frappe.model.document import Document

class Activity(Document):
    def validate(self):
        pass
        self.remove_duplicate_parameters()

    def remove_duplicate_parameters(self):
        unique_parameters = {}
        duplicates = []

        for param in self.get('parameter'):
            key = param.parameter
            if key in unique_parameters:
                duplicates.append(param)
            else:
                unique_parameters[key] = param

        for duplicate in duplicates:
            self.remove(duplicate)

    def remove(self, param):
        self.get('parameter').remove(param)

# If delete the parameter from activity, then delete all the task from task detail for that activity.


@frappe.whitelist()
def delete_task_depends_activity(doc, method):
    allowed_statuses = [
        "Open", "In Progress", "Overdue", "Pending Approval", 
        "Rejected", "Approved", "Completed", "Cancelled"
    ]

    existing_tasks = frappe.get_all(
        'Task Detail',
        filters={
            'activity': doc.activity_name,
            'status': ['in', allowed_statuses]
        },
        fields=['name', 'parameter']
    )
    
    current_parameters = {row.parameter for row in doc.parameter}
    
    for task in existing_tasks:
        if task['parameter'] not in current_parameters:
            frappe.delete_doc('Task Detail', task['name'])
