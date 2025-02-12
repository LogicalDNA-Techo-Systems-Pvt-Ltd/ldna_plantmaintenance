# import frappe

# def task_detail_permission(user):
#     user = frappe.session.user
#     print(user)
    
#     user_doc = frappe.get_doc("User", user)
#     user_full_name = user_doc.full_name
#     user_roles = [role.role for role in user_doc.roles]

#     if frappe.db.exists("User Work Center", user):
#         user_work_center = frappe.get_doc("User Work Center", user)
#         user_work_centers = [wc.work_center for wc in user_work_center.work_center] if hasattr(user_work_center, 'work_center') else []
#     else:
#         user_work_centers = []

#     if user == 'Administrator':
#         return "1=1"

#     elif 'Maintenance Manager' in user_roles:
#         if user_work_centers:
#             work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
#             return """
#             (
#                 (`tabTask Detail`.`work_center` IN ({work_centers_condition}) AND 
#                 `tabTask Detail`.`approver` = '{user}')
#             )
#             """.format(user=user, work_centers_condition=work_centers_condition)
#         else:
#             return "1=0"   

#     elif 'Maintenance User' in user_roles:
#         if user_work_centers:
#             work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
#             return """
#             (
#                 (`tabTask Detail`.`work_center` IN ({work_centers_condition}) AND 
#                 (`tabTask Detail`.`assigned_to` LIKE '%%{user}%%' OR `tabTask Detail`.`assigned_to` LIKE '%%{user_full_name}%%' OR `tabTask Detail`.`assigned_to` IS NULL)
#                 )
#                 OR
#                 (`tabTask Detail`.`work_center` NOT IN ({work_centers_condition}) AND 
#                 (`tabTask Detail`.`assigned_to` LIKE '%%{user}%%' OR `tabTask Detail`.`assigned_to` LIKE '%%{user_full_name}%%')
#                 )
#             )
#             """.format(user=user, user_full_name=user_full_name, work_centers_condition=work_centers_condition)
#         else:
#             return """
#             (
#                 `tabTask Detail`.`assigned_to` LIKE '%%{user}%%' OR 
#                 `tabTask Detail`.`assigned_to` LIKE '%%{user_full_name}%%'
#             )
#             """.format(user=user, user_full_name=user_full_name)

#     elif 'System Manager' in user_roles:
#         if user_work_centers:
#             work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
#             return """
#             (
#                 `tabTask Detail`.`work_center` IN ({work_centers_condition})
#             )
#             """.format(work_centers_condition=work_centers_condition)
#         else:
#             return "1=0"   

#     elif 'Process Manager' in user_roles:
#         if user_work_centers:
#             work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
#             return """
#             (
#                 `tabTask Detail`.`work_center` IN ({work_centers_condition}) AND
#                 `tabTask Detail`.`status` IN ('Approved', 'Completed', 'Overdue', 'Rejected')
#             )
#             """.format(work_centers_condition=work_centers_condition)
#         else:
#             return "1=0"

            


import frappe

def task_detail_permission(user):
    user = frappe.session.user
    print(user)

    user_doc = frappe.get_doc("User", user)
    user_roles = {role.role for role in user_doc.roles}  

    user_work_centers = []
    user_equipment_groups = []

    if frappe.db.exists("User Work Center", user):
        user_work_center_doc = frappe.get_doc("User Work Center", user)
        
        if hasattr(user_work_center_doc, 'work_center'):
            user_work_centers = [wc.work_center for wc in user_work_center_doc.work_center]
        
        if hasattr(user_work_center_doc, 'equipment_group'):
            user_equipment_groups = [eg.equipment_group for eg in user_work_center_doc.equipment_group]

    if user == 'Administrator':
        return "1=1"

    relevant_roles = {'Maintenance Manager', 'Maintenance User', 'Process Manager'}
    
    if user_roles & relevant_roles:  
        if user_work_centers and user_equipment_groups:
            work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
            equipment_groups_condition = ", ".join(["'{0}'".format(eg) for eg in user_equipment_groups])
            
            return """
            (`tabTask Detail`.`work_center` IN ({work_centers_condition}) 
            AND `tabTask Detail`.`equipment_group` IN ({equipment_groups_condition}))
            """.format(work_centers_condition=work_centers_condition, 
                       equipment_groups_condition=equipment_groups_condition)
        else:
            return "1=0"  

    if 'System Manager' in user_roles:
        if user_work_centers and user_equipment_groups:
            work_centers_condition = ", ".join(["'{0}'".format(wc) for wc in user_work_centers])
            equipment_groups_condition = ", ".join(["'{0}'".format(eg) for eg in user_equipment_groups])

            return """
            (`tabTask Detail`.`work_center` IN ({work_centers_condition}) 
            AND `tabTask Detail`.`equipment_group` IN ({equipment_groups_condition})
            OR `tabTask Detail`.`work_center` IS NULL)
            """.format(work_centers_condition=work_centers_condition,
                       equipment_groups_condition=equipment_groups_condition)
        else:
            return "1=1"

    return "1=0"
