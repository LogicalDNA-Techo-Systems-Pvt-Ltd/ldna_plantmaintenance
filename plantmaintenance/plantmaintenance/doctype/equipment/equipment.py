# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
class Equipment(Document):
    
    def validate(self):
        self.validate_equipment_code_name_combination()
        # Add other validations as needed

    def validate_equipment_code_name_combination(self):
        if(self.equipment_code and self.equipment_name):
            if (self.equipment_name == self.equipment_code):
                frappe.throw("Equipment code and Equipment name should not be equal. ")
    