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

@frappe.whitelist()
def get_functional_location_list_based_on_location(location):
    if location:
        functional_location_list = frappe.get_all("Functional Location CT", filters={"parent": location}, fields=["functional_location"])
        
        functional_location =  [func_loc['functional_location'] for func_loc in functional_location_list]

        return functional_location
    return []

@frappe.whitelist()
def get_section_based_on_func_location(func_loc):
    if func_loc:
        section_list = frappe.get_all("Section CT", filters={"parent": func_loc}, fields=["section"])
        
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

# @frappe.whitelist()
# def equipment_task_details(task_detail):
#     task_detail = json.loads(task_detail)

#     equipment_doc = frappe.get_doc("Equipment",task_detail['equipment_code'])
#     task_detail_doc = frappe.get_doc("Task Detail", task_detail['name'])
#     if equipment_doc:
#         detail = equipment_doc.append("task_detail_ct",{})
#         detail.task = task_detail['name']
#         detail.parameter = task_detail['parameter']
#         detail.date = task_detail['creation']
#         detail.status = task_detail['status']
#         detail.passfail = task_detail['result']
        
#     if task_detail_doc.material_returned:
#             material_returned = task_detail_doc.get("material_returned", [])
#             print("material returned",material_returned)
#             if material_returned:
#                 for material_issue in material_returned:
#                     print(material_issue.material_name)
#                     print(material_issue.type)
#                     print(material_issue.issue_quantity)
#                     detail = equipment_doc.append("material_moment_ct", {})
#                     detail.material_type = material_issue.type
#                     detail.material_name = material_issue.material_code
#                     detail.date = task_detail['creation']
#                     detail.quantity = material_issue.issue_quantity

#     equipment_doc.save()


@frappe.whitelist()
def equipment_task_details(task_detail):
    task_detail = json.loads(task_detail)

    equipment_doc = frappe.get_doc("Equipment", task_detail['equipment_code'])
    task_detail_doc = frappe.get_doc("Task Detail", task_detail['name'])
    
    if equipment_doc:
        task_exists = any(d.task == task_detail['name'] for d in equipment_doc.task_detail_ct)
        
        if not task_exists:
            detail = equipment_doc.append("task_detail_ct", {})
            detail.task = task_detail['name']
            detail.parameter = task_detail['parameter']
            detail.date = task_detail['actual_start_date']
            detail.status = task_detail['status']
            detail.passfail = task_detail['result']
            
    if task_detail_doc.material_returned:
            material_returned = task_detail_doc.get("material_returned", [])
            print("material returned",material_returned)
            if material_returned:
                for material_issue in material_returned:
                    print(material_issue.material_name)
                    print(material_issue.type)
                    print(material_issue.issue_quantity)
                    detail = equipment_doc.append("material_moment_ct", {})
                    detail.material_type = material_issue.type
                    detail.material_name = material_issue.material_code
                    detail.date = task_detail['actual_start_date']
                    detail.quantity = material_issue.issue_quantity,
                    detail.return_quantity = material_issue.return_quantity

    equipment_doc.save()