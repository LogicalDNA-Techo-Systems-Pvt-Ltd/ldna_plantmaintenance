# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Parameter(Document):
    
	def before_save(self):
		if self.day_of_month is not None and (self.day_of_month < 1 or self.day_of_month > 31):
			frappe.throw("Day of month should be between 1 and 31 for Monthly frequency.")