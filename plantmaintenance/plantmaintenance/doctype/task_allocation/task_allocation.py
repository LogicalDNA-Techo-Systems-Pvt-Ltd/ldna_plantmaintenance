import frappe
from frappe.model.document import Document

class TaskAllocation(Document):
    def on_update(self):
        if self.docstatus == 0:
            self.update_task_details()

    def update_task_details(self):
        for detail in self.get('task_allocation_details'):
            task_detail_name = self.get_existing_task_detail_name(detail.equipment_code)
            
            if task_detail_name:
                task_detail = frappe.get_doc("Task Detail", task_detail_name)
                task_detail.update({
                    "approver": frappe.session.user,
                    "equipment_id": detail.equipment_code,
                    "equipment_name": detail.equipment_name,
                    "work_center": self.work_central,
                    "plant_section": self.plant_section,
                    "priority": detail.priority,
                    "expected_start_date": detail.date,
                    # "expected_end_date": self.end_date,
                    "assigned_to": detail.assign_to,
                    "activity": detail.activity,
                    "parameter": detail.parameter,
                })
                task_detail.save(ignore_permissions=True)
            else:
                self.create_task_detail(detail)

    def create_task_detail(self, detail):
        task_detail = frappe.new_doc("Task Detail")
        task_detail.update({
            "task_allocation_id": self.name,
            "approver": frappe.session.user,
            "equipment_id": detail.equipment_code,
            "equipment_name": detail.equipment_name,
            "work_center": self.work_central,
            "plant_section": self.plant_section,
            "expected_start_date": detail.date,
            # "expected_end_date": self.end_date,
            "assigned_to": detail.assign_to,
            "activity": detail.activity,
            "parameter": detail.parameter,
            "priority": detail.priority,
        })
        task_detail.insert(ignore_permissions=True)

    def get_existing_task_detail_name(self, equipment_code):
        return frappe.db.get_value("Task Detail", {
            "task_allocation_id": self.name,
            "equipment_id": equipment_code,
        }, "name")
