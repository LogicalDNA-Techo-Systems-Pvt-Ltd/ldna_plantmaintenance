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


# @frappe.whitelist()
# def delete_task_depends_activity(doc, method):
#     allowed_statuses = [
#         "Open", "In Progress", "Overdue", "Pending Approval", 
#         "Rejected", "Approved", "Completed", "Cancelled"
#     ]

#     existing_tasks = frappe.get_all(
#         'Task Detail',
#         filters={
#             'activity': doc.activity_name,
#             'status': ['in', allowed_statuses]
#         },
#         fields=['name', 'parameter']
#     )
    
#     current_parameters = {row.parameter for row in doc.parameter}
    
#     for task in existing_tasks:
#         if task['parameter'] not in current_parameters:
#             frappe.delete_doc('Task Detail', task['name'])


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
            try:
                task_doc = frappe.get_doc('Task Detail', task['name'])

                if task_doc.docstatus == 1:
                    task_doc.cancel()

                linked_equipments = frappe.get_all(
                    'Equipment',
                    filters=[['Equipment Task Details CT', 'task', '=', task['name']]],
                    fields=['name']
                )

                for equipment in linked_equipments:
                    equipment_doc = frappe.get_doc('Equipment', equipment.name)
                    equipment_doc.set("equipment_task_details", [
                        row for row in equipment_doc.equipment_task_details if row.task != task['name']
                    ])
                    equipment_doc.save()

                frappe.delete_doc('Task Detail', task['name'], force=1)

            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Error deleting Task Detail: {task['name']}")
