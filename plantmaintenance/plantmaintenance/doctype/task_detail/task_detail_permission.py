

  




import frappe

def task_detail_permission(user):
    user = frappe.session.user

    user_doc = frappe.get_doc("User", user)
    user_roles = [role.role for role in user_doc.roles]

    user_work_center = frappe.get_doc("User Work Center", user)

    user_work_centers = [wc.work_center for wc in user_work_center.work_center] if hasattr(user_work_center, 'work_center') else []

    if 'Maintenance Manager' in user_roles:
        if user_work_centers:
            work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
            return """
            (`tabTask Detail`.`approver` = '{user}') AND (`tabTask Detail`.`work_center` IN ({work_centers_condition}))
            """.format(user=user, work_centers_condition=work_centers_condition)
        else:
            return """
            (`tabTask Detail`.`approver` = '{user}')
            """.format(user=user)
    elif 'Maintenance User' in user_roles:
        if user_work_centers:
            work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
            return """
            (`tabTask Detail`.`assigned_to` = '{user}' OR `tabTask Detail`.`assigned_to` IS NULL) AND (`tabTask Detail`.`work_center` IN ({work_centers_condition}))
            """.format(user=user, work_centers_condition=work_centers_condition)
        else:
            return """
            (`tabTask Detail`.`assigned_to` = '{user}' OR `tabTask Detail`.`assigned_to` IS NULL)
            """.format(user=user)
    

    

 