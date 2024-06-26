# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TaskAllocation(Document):
    def on_update(self):
        if self.docstatus == 0:
            self.update_task_details()

    def update_task_details(self):
        for detail in self.get('task_allocation_details'):
            task_detail_name = self.get_existing_task_detail_name(self.schedule_no, detail.item_no)
            
            if task_detail_name:
                task_detail = frappe.get_doc("Task Detail", task_detail_name)
                task_detail.update({
                    "approver": frappe.session.user,
                    "location": self.location,
                    "section": self.section,
                    "expected_start_date": self.start_date,
                    "expected_end_date": self.end_date,
                    "frequency": detail.type,
                    "assigned_to": detail.employee
                })
                task_detail.save(ignore_permissions=True)
    
            else:
                self.create_task_detail(detail)

    def create_task_detail(self, detail):
        task_detail = frappe.new_doc("Task Detail")
        task_detail.update({
            "schedule_no": self.schedule_no,
            "approver": frappe.session.user,
            "location": self.location,
            "section": self.section,
            "expected_start_date": self.start_date,
            "expected_end_date": self.end_date,
            "frequency": detail.type,
            "item": detail.item_no,
            "assigned_to": detail.employee,
        })
        task_detail.insert(ignore_permissions=True)

    def get_existing_task_detail_name(self, schedule_no, item_no):
        return frappe.db.get_value("Task Detail", {
            "schedule_no": schedule_no,
            "item": item_no,
        }, "name")
