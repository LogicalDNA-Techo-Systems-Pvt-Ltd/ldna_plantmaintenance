# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Settings(Document):
	pass

@frappe.whitelist()
def get_context():
    return frappe.render_template('plantmaintenance/plantmaintenance/doctype/settings/settings.html')

