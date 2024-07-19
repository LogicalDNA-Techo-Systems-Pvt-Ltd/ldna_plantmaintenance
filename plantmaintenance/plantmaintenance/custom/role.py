
import frappe
from frappe.model.document import Document


STANDARD_ROLES = ("")

class Role(Document):
    def disable_role(self):
        if self.name in STANDARD_ROLES:
            frappe.throw(frappe._("Standard roles cannot be disabled"))
        else:
            self.remove_roles()

    