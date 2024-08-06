# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt



import frappe
from frappe.model.document import Document

class Activity(Document):
    def validate(self):
        self.remove_duplicate_parameters()

    def remove_duplicate_parameters(self):
        unique_parameters = {}
        duplicates = []

        for param in self.get('parameter'):
            key = param.parameter
            if key in unique_parameters:
                duplicates.append(param)
            else:
                unique_parameters[key] = param

        for duplicate in duplicates:
            self.remove(duplicate)

    def remove(self, param):
        self.get('parameter').remove(param)
