# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

 

import frappe
from frappe.model.document import Document

class ActivityGroup(Document):
    def validate(self):
        self.remove_duplicate_activities()

    def remove_duplicate_activities(self):
        unique_activities = {}
        duplicates = []

        for act in self.get('activity'):
                key = act.activity
                if key in unique_activities:
                        duplicates.append(act)
                else:
                    unique_activities[key] = act
        for duplicate in duplicates:
               self.remove(duplicate)

    def remove(self, act):
         self.get('activity').remove(act)



 
# I we delete the activity from activity group then delete the all the task from task detail of that activity for that particulr activity group.


@frappe.whitelist()
def delete_task_depends_activity_group(doc, method):
    existing_tasks = frappe.get_all('Task Detail', filters={'activity_group': doc.activity_group, 'status':'Open'}, fields=['name', 'activity'])
    
    if not doc.is_active:
        for task in existing_tasks:
            frappe.delete_doc('Task Detail', task['name'])
        return   
    current_activities = {row.activity for row in doc.activity}  # Assuming 'activity' is the child table containing activities
    
    for task in existing_tasks:
        if task['activity'] not in current_activities:
            frappe.delete_doc('Task Detail', task['name']) 


def remove_activity_group_from_equipment(doc,method):
    existing_tasks = frappe.get_all('Task Detail', filters={'activity_group': doc.activity_group, 'status':'Open'}, fields=['name', 'activity'])

    if not doc.is_active:
         equipment_with_activity_group = frappe.get_all('Equipment', filters={'activity_group': doc.activity_group}, fields=['name'])
         
         
         for equipment in equipment_with_activity_group:
              frappe.set_value('Equipment', equipment['name'], 'activity_group', None)

    


    


