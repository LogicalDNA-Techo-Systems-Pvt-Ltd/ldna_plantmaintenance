# Copyright (c) 2025, LogicalDNA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UserDetails(Document):
	pass


@frappe.whitelist()
def get_maintenance_managers(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT name, full_name FROM `tabUser`
        WHERE name IN (
            SELECT parent FROM `tabHas Role`
            WHERE role = 'Maintenance Manager'
        ) AND enabled = 1
        AND name != 'Administrator'
        ORDER BY full_name
    """)

@frappe.whitelist()
def get_maintenance_users(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT name, full_name FROM `tabUser`
        WHERE name IN (
            SELECT parent FROM `tabHas Role`
            WHERE role = 'Maintenance User'
        ) AND enabled = 1
        AND name != 'Administrator'
        ORDER BY full_name
    """)


@frappe.whitelist()
def get_process_managers(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT name, full_name FROM `tabUser`
        WHERE name IN (
            SELECT parent FROM `tabHas Role`
            WHERE role = 'Process Manager'
        ) AND enabled = 1
        AND name != 'Administrator'
        ORDER BY full_name
    """)