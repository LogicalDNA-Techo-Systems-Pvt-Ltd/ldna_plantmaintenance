

import frappe

def task_detail_permission(user):
    if not user:
        user = frappe.session.user

    user_doc = frappe.get_doc("User", user)
    user_roles = [role.role for role in user_doc.roles]

    if 'Maintenance Manager' in user_roles:
        return """
        `tabTask Detail`.`approver` = '{user}'
        """.format(user=user)
    elif 'Maintenance User' in user_roles:
        return """
        `tabTask Detail`.`assigned_to` = '{user}'
        """.format(user=user)
    else:
        return "1 = 0"   
    

    






         
 