# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Parameter(Document):
        def onload(self):
                if self.number_of_readings:
                        NumberOfReadings = int(self.number_of_readings)
                        if NumberOfReadings > 10:
                                frappe.throw("Number of readings should be less than or equal to 10.")
                else:
                        self.number_of_readings = 0
