# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
class Item(Document):
    
    def validate(self):
        self.validate_item_code_name_combination()
        # Add other validations as needed

    def validate_item_code_name_combination(self):
        if(self.item_code and self.item_name):
            if (self.item_name == self.item_code):
                frappe.throw("Item code and Item name should not be equal. ")
    