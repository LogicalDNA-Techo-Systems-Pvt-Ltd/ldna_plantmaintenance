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



#This code is to fetch the task detail in equipment's history tab PD.
@frappe.whitelist()
def equipment_task_details(doc, method=None):
    
    task_detail = doc
    if task_detail.equipment_code:
        equipment_doc = frappe.get_doc("Equipment", task_detail.equipment_code)
        task_detail_doc = frappe.get_doc("Task Detail", task_detail.name)
        
        valid_statuses = ["Completed", "Rejected", "Overdue"]
        valid_workflow_states = ["Approved", "Rejected"]

        def is_task_detail_existing(child_table, task_name, status):
            for detail in child_table:
                if detail.task == task_name and detail.status == status:
                    return True
            return False

        def should_create_entry(status, workflow_state):
            if status == "Completed":
                return not is_task_detail_existing(equipment_doc.task_detail_ct, task_detail.name, "Completed")
            elif status == "Rejected" and workflow_state == "Rejected":
                return not is_task_detail_existing(equipment_doc.task_detail_ct, task_detail.name, "Rejected")
            else:
                return not is_task_detail_existing(equipment_doc.task_detail_ct, task_detail.name, status)

        def is_material_entry_existing(child_table, task_name, material_name):
            for detail in child_table:
                if detail.task == task_name and detail.material_name == material_name:
                    return True
            return False

        if equipment_doc and task_detail.status in valid_statuses:
            if should_create_entry(task_detail.status, task_detail.workflow_state):
                detail = equipment_doc.append("task_detail_ct", {})
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
                    if not is_material_entry_existing(equipment_doc.material_movement_ct, task_detail.name, material_issue.material_code):
                        detail = equipment_doc.append("material_movement_ct", {})
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
