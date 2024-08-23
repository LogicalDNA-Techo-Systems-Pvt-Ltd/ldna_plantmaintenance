import frappe
import json
from datetime import datetime



@frappe.whitelist()
def get_task_details():
    tasks = frappe.get_all("Task Detail", fields=["name"])

    task_details = []
    
    for task in tasks:
        material_issued = frappe.get_all(
            "Material Issue",
            filters={"parent": task.name, "status": "Pending Approval"},
            fields=["material_code", "material_name", "available_quantity", "required_quantity", "shortage", "status", "approval_date"]
        )

        task_detail = {
            "task_name": task.name,
            "materials": material_issued
        }

        task_details.append(task_detail)

    return task_details


import frappe
import json
from datetime import datetime

@frappe.whitelist()
def get_task_details():
    tasks = frappe.get_all("Task Detail", fields=["name"])

    task_details = []
    
    for task in tasks:
        material_issued = frappe.get_all(
            "Material Issue",
            filters={"parent": task.name, "status": "Pending Approval"},
            fields=["material_code", "material_name", "available_quantity", "required_quantity", "shortage", "status", "approval_date"]
        )

        task_detail = {
            "task_name": task.name,
            "materials": material_issued
        }

        task_details.append(task_detail)

    return task_details

@frappe.whitelist()
def approve_materials(materials):
    if not isinstance(materials, list):
        materials = json.loads(materials)

    today = datetime.today().strftime('%Y-%m-%d')
    
    for item in materials:
        task_name = item.get('task_name')
        material_code = item.get('material_code')

        task_doc = frappe.get_all(
            "Task Detail",
            filters={"name": task_name},
            fields=["name"]
        )
        
        if task_doc:
            task_doc = frappe.get_doc("Task Detail", task_name)
            
            for material in task_doc.material_issued:
                if (material.material_code == material_code and
                    material.status == "Pending Approval"):
                    material.status = "Material Issued"
                    material.issued_date = today
                    
                   
                    task_doc.append("material_returned", {
                        "material_code": material.material_code,
                        "material_name": material.material_name,
                        "issue_quantity": material.required_quantity,
                        "approval_date": material.approval_date,
                        "issued_date": today
                    })
                    
                    task_doc.save()
                    break  

    return "Selected materials successfully approved."




# @frappe.whitelist()
# def approve_materials(materials):
#     if not isinstance(materials, list):
#         materials = json.loads(materials)

#     today = datetime.today().strftime('%Y-%m-%d')
    
  
#     for item in materials:
#         task_name = item.get('task_name')
#         material_code = item.get('material_code')

#         task_doc = frappe.get_all(
#             "Task Detail",
#             filters={"name": task_name},
#             fields=["name"]
#         )
        
#         if task_doc:
#             task_doc = frappe.get_doc("Task Detail", task_name)
            
#             for material in task_doc.material_issued:
#                 if (material.material_code == material_code and
#                     material.status == "Pending Approval"):
#                     material.status = "Material Issued"
#                     material.issued_date = today
                    
                    
#                 doc.append("material_returned", {
#                     "material_code": item.material_code,
#                     "material_name": item.material_name,
#                     "issue_quantity": item.required_quantity,
#                     "approval_date": item.approval_date,
#                     "issued_date": item.issued_date
#                 })
#                     task_doc.save()
#                     break  

#     return "Selected materials successfully approved."

