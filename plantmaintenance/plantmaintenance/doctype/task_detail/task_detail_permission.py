
# # import frappe

# # def task_detail_permission(user):
# #     user = frappe.session.user

# #     user_doc = frappe.get_doc("User", user)
# #     user_roles = [role.role for role in user_doc.roles]

    
# #     if frappe.db.exists("User Work Center", user):
# #         user_work_center = frappe.get_doc("User Work Center", user)
# #         user_work_centers = [wc.work_center for wc in user_work_center.work_center] if hasattr(user_work_center, 'work_center') else []
# #     else:
# #         user_work_centers = []

# #     if 'Maintenance Manager' in user_roles:
# #         if user_work_centers:
# #             work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
# #             return """
# #             (`tabTask Detail`.`approver` = '{user}' OR `tabTask Detail`.`approver` IS NULL) AND (`tabTask Detail`.`work_center` IN ({work_centers_condition}))
# #             """.format(user=user, work_centers_condition=work_centers_condition)
# #         else:
# #             return """
# #             (`tabTask Detail`.`approver` = '{user}' OR `tabTask Detail`.`approver` IS NULL)
# #             """.format(user=user)
# #     elif 'Maintenance User' in user_roles:
# #         if user_work_centers:
# #             work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
# #             return """
# #             (`tabTask Detail`.`assigned_to` = '{user}' OR `tabTask Detail`.`assigned_to` IS NULL) AND (`tabTask Detail`.`work_center` IN ({work_centers_condition}))
# #             """.format(user=user, work_centers_condition=work_centers_condition)
# #         else:
# #             return """
# #             (`tabTask Detail`.`assigned_to` = '{user}' OR `tabTask Detail`.`assigned_to` IS NULL)
# #             """.format(user=user)
        
import frappe

def task_detail_permission(user):
    user = frappe.session.user
    print(user)

    user_doc = frappe.get_doc("User", user)
    
    user_full_name = user_doc.full_name

    user_roles = [role.role for role in user_doc.roles]

    if frappe.db.exists("User Work Center", user):
        user_work_center = frappe.get_doc("User Work Center", user)
        user_work_centers = [wc.work_center for wc in user_work_center.work_center] if hasattr(user_work_center, 'work_center') else []
    else:
        user_work_centers = []

    if 'Maintenance Manager' in user_roles:
        if user_work_centers:
            work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
            return """
            (`tabTask Detail`.`approver` = '{user}' OR `tabTask Detail`.`approver` IS NULL) AND (`tabTask Detail`.`work_center` IN ({work_centers_condition}))
            """.format(user=user, work_centers_condition=work_centers_condition)
        else:
            return """
            (`tabTask Detail`.`approver` = '{user}' OR `tabTask Detail`.`approver` IS NULL)
            """.format(user=user)
    elif 'Maintenance User' in user_roles:
        if user_work_centers:
            work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
            return """
            (`tabTask Detail`.`assigned_to` LIKE '%%{user}%%' OR `tabTask Detail`.`assigned_to` LIKE '%%{user_full_name}%%' OR `tabTask Detail`.`assigned_to` IS NULL) AND 
            (`tabTask Detail`.`work_center` IN ({work_centers_condition}))
            """.format(user=user, user_full_name=user_full_name, work_centers_condition=work_centers_condition)
        else:
            return """
            (`tabTask Detail`.`assigned_to` LIKE '%%{user}%%' OR `tabTask Detail`.`assigned_to` LIKE '%%{user_full_name}%%' OR `tabTask Detail`.`assigned_to` IS NULL)
            """.format(user=user, user_full_name=user_full_name)


