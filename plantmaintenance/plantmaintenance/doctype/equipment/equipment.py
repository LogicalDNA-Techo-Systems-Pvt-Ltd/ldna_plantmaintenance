# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
class Equipment(Document):
    
    def validate(self):
        self.validate_equipment_code_name_combination()
        # Add other validations as needed

    def validate_equipment_code_name_combination(self):
        if(self.equipment_code and self.equipment_name):
            if (self.equipment_name == self.equipment_code):
                frappe.throw("Equipment code and Equipment name should not be equal. ")


@frappe.whitelist()
def get_location_list_based_on_plant(plant):
    if plant:
        location_list = frappe.get_all("Location CT", filters={"parent": plant}, fields=["location"])
   
        plant_location =  [loc['location'] for loc in location_list]

        return plant_location
    return []

# @frappe.whitelist()
# def get_functional_location_list_based_on_location(location):
#     if location:
#         functional_location_list = frappe.get_all("Functional Location CT", filters={"parent": location}, fields=["functional_location"])
        
#         functional_location =  [func_loc['functional_location'] for func_loc in functional_location_list]

#         return functional_location
#     return []

@frappe.whitelist()
def get_section_based_on_location(location):
    if location:
        section_list = frappe.get_all("Section CT", filters={"parent": location}, fields=["section"])
        
        section =  [sec['section'] for sec in section_list]
       
        return section
    return []

@frappe.whitelist()
def get_work_center_based_on_section(section):
    if section:
        work_center_list = frappe.get_all("Work Center CT", filters={"parent": section}, fields=["work_center"])
        
    
        work_center =  [wrk_cent['work_center'] for wrk_cent in work_center_list]

        return work_center
    return []

@frappe.whitelist()
def get_equipment_based_on_work_center(work_center):
    equipment_list = frappe.get_all('Equipment', 
        filters={'work_center': work_center}, 
        fields=['name']
    )
    return [eq.name for eq in equipment_list]




# If change the activity group from equipment then delete the task of that activity group for that equipment.

# @frappe.whitelist()
# def update_activity_group_and_delete_tasks(doc, method):
#     old_activity_group = frappe.get_value('Equipment', doc.name, 'activity_group')
#     new_activity_group = doc.activity_group

#     if old_activity_group != new_activity_group:
#         task_details = frappe.get_all('Task Detail',
#                                       filters={'equipment_code': doc.name,
#                                                'activity_group': old_activity_group,
#                                                'status': 'Open'},
#                                       fields=['name'])
        
#         for task_detail in task_details:
#             frappe.delete_doc('Task Detail', task_detail['name'])

#         frappe.db.set_value('Equipment', doc.name, 'activity_group', new_activity_group)


# @frappe.whitelist()
# def update_activity_group_and_delete_tasks(doc, method):
#     old_activity_group = frappe.get_value('Equipment', doc.name, 'activity_group')
#     new_activity_group = doc.activity_group

#     if old_activity_group != new_activity_group:
#         task_details = frappe.get_all(
#             'Task Detail',
#             filters={
#                 'equipment_code': doc.name,
#                 'activity_group': old_activity_group,
#                 'status': ['in', [
#                     'Open',
#                     'Hold',
#                     'In Progress',
#                     'Pending Approval',
#                     'Rejected',
#                     'Approved',
#                     'Completed',
#                     'Cancelled',
#                     'Overdue'
#                 ]]
#             },
#             fields=['name']
#         )

#         task_names = [td['name'] for td in task_details]

#         equipment_doc = frappe.get_doc('Equipment', doc.name)
#         equipment_doc.equipment_task_details = [
#             row for row in equipment_doc.equipment_task_details if row.task not in task_names
#         ]
#         equipment_doc.save(ignore_permissions=True)

#         for task_name in task_names:
#             try:
#                 task_doc = frappe.get_doc('Task Detail', task_name)

#                 if task_doc.docstatus == 1:
#                     task_doc.flags.ignore_validate = True
#                     task_doc.cancel()

#                 task_doc.delete(ignore_permissions=True)

#             except Exception as e:
#                 frappe.log_error(f"Error deleting Task Detail {task_name}: {str(e)}")

#         frappe.db.set_value('Equipment', doc.name, 'activity_group', new_activity_group)



@frappe.whitelist()
def update_activity_group_and_delete_tasks(doc, method):
    if getattr(doc, "__called_from_update_activity_group", False):
        return

    # 🔁 Step 1: Get NEW activity groups via current doc → equipment_group → Equipment Group → activity_group
    new_activity_groups = set()
    for row in doc.equipment_group:
        equipment_group_name = row.equipment_group
        activity_groups = frappe.get_all(
            'Activity Group CT',
            filters={
                'parent': equipment_group_name,
                'parenttype': 'Equipment Group'
            },
            pluck='activity_group'
        )
        new_activity_groups.update(activity_groups)

    # 🔁 Step 2: Get OLD activity groups from DB
    old_equipment_groups = frappe.get_all(
        'Equipment Group CT',
        filters={
            'parent': doc.name,
            'parenttype': 'Equipment'
        },
        pluck='equipment_group'
    )

    old_activity_groups = set()
    for eg in old_equipment_groups:
        ags = frappe.get_all(
            'Activity Group CT',
            filters={
                'parent': eg,
                'parenttype': 'Equipment Group'
            },
            pluck='activity_group'
        )
        old_activity_groups.update(ags)

    # 🧮 Step 3: Detect removed activity groups
    removed_groups = old_activity_groups - new_activity_groups
    if not removed_groups:
        return

    # ✅ Step 4: Delete Task Details for removed activity groups
    task_details = frappe.get_all(
        'Task Detail',
        filters={
            'equipment_code': doc.name,
            'activity_group': ['in', list(removed_groups)],
            'status': ['in', [
                'Open', 'Hold', 'In Progress', 'Pending Approval', 'Rejected',
                'Approved', 'Completed', 'Cancelled', 'Overdue'
            ]]
        },
        fields=['name']
    )

    task_names = [td['name'] for td in task_details]

    if not task_names:
        return

    # ✅ Step 5: Remove from Equipment Task Details
    equipment_doc = frappe.get_doc('Equipment', doc.name)
    equipment_doc.__called_from_update_activity_group = True
    equipment_doc.equipment_task_details = [
        row for row in equipment_doc.equipment_task_details if row.task not in task_names
    ]
    equipment_doc.save(ignore_permissions=True)

    # ✅ Step 6: Cancel and delete task detail docs
    for task_name in task_names:
        try:
            task_doc = frappe.get_doc('Task Detail', task_name)
            if task_doc.docstatus == 1:
                task_doc.flags.ignore_validate = True
                task_doc.cancel()
            task_doc.delete(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error deleting Task Detail {task_name}: {str(e)}")


def validate(doc, method):
    if doc.workflow_state == "Approval Pending":
        return

    if not doc.equipment_group or not doc.equipment_code:
        return

    for row in doc.equipment_group:
        equipment_group = row.equipment_group

        activity_rows = frappe.get_all(
            "Activity Group CT",
            filters={
                "parent": equipment_group,
                "parenttype": "Equipment Group",
                "equipment_code": doc.equipment_code
            },
            limit=1
        )

        if not activity_rows:
            frappe.throw(
                f"Equipment Code <b>{doc.equipment_code}</b> is not defined "
                f"for Equipment Group <b>{equipment_group}</b>."
            )
