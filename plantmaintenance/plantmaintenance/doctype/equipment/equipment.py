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



@frappe.whitelist()
def update_activity_group_and_delete_tasks(doc, method):
    old_activity_group = frappe.get_value('Equipment', doc.name, 'activity_group')
    new_activity_group = doc.activity_group

    if old_activity_group != new_activity_group:
        task_details = frappe.get_all('Task Detail',
                                      filters={'equipment_code': doc.name,
                                               'activity_group': old_activity_group,
                                               'status': 'Open'},
                                      fields=['name'])
        
        for task_detail in task_details:
            frappe.delete_doc('Task Detail', task_detail['name'])

        frappe.db.set_value('Equipment', doc.name, 'activity_group', new_activity_group)



