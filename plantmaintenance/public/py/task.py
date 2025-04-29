# import frappe
# from frappe.utils import getdate, add_days
# from dateutil.relativedelta import relativedelta
# import calendar

# @frappe.whitelist()
# def generate_future_tasks():
#     today = getdate()
#     end_date = add_days(today, 90)

#     equipment_list = frappe.db.get_list(
#         "Task Detail",
#         filters={"type": "Preventive"},
#         pluck="equipment_code",
#         distinct=True
#     )

#     if not equipment_list:
#         frappe.logger().info("No Preventive tasks found.")
#         return

#     for equipment_code in equipment_list:
#         # Group by equipment + activity + parameter + frequency
#         key_map = {}
#         all_tasks = frappe.db.get_all(
#             "Task Detail",
#             filters={"equipment_code": equipment_code, "type": "Preventive"},
#             fields=["equipment_code", "activity", "activity_group", "parameter", "frequency", "plan_start_date"]
#         )

#         for task in all_tasks:
#             key = (task.activity, task.parameter, task.frequency)
#             if key not in key_map or getdate(task.plan_start_date) > getdate(key_map[key]["plan_start_date"]):
#                 key_map[key] = task

#         equipment_doc = frappe.db.get_value("Equipment", equipment_code,
#             ["equipment_name", "sub_section", "old_tag_dcs", "description"], as_dict=True)

#         for key, task in key_map.items():
#             if not task.parameter:
#                 continue

#             parameter_doc = frappe.get_doc("Parameter", task.parameter)

#             next_due_date = getdate(task.plan_start_date)

#             while True:
#                 next_due_date = calculate_next_due_date(next_due_date, task.frequency)
#                 if next_due_date > end_date:
#                     break

#                 if frappe.db.exists("Task Detail", {
#                     "equipment_code": equipment_code,
#                     "activity": task.activity,
#                     "parameter": task.parameter,
#                     "plan_start_date": next_due_date
#                 }):
#                     continue  # skip if this exact date already exists

#                 new_task = frappe.new_doc("Task Detail")
#                 new_task.update({
#                     "approver": frappe.session.user or "Administrator",
#                     "equipment_code": equipment_code,
#                     "equipment_name": equipment_doc.equipment_name or "",
#                     "activity_group": task.activity_group,
#                     "activity": task.activity,
#                     "parameter": task.parameter,
#                     "frequency": task.frequency,
#                     "plan_start_date": next_due_date,
#                     "day": calendar.day_name[next_due_date.weekday()],
#                     "date": next_due_date,
#                     "unique_key": f"{equipment_code[:3]}_{next_due_date}_{frappe.generate_hash(length=5)}",
#                     "location": "",
#                     "section": "",
#                     "old_tag_dcs": equipment_doc.old_tag_dcs or "",
#                     "sub_section": equipment_doc.sub_section or "",
#                     "description": equipment_doc.description or "",
#                     "parameter_type": parameter_doc.parameter_type or "",
#                     "minimum_value": parameter_doc.minimum_value or "",
#                     "maximum_value": parameter_doc.maximum_value or "",
#                     "standard_value": parameter_doc.standard_value or "",
#                 })

#                 try:
#                     new_task.insert(ignore_permissions=True)
#                 except Exception as e:
#                     frappe.logger().error(f"Insert failed for {equipment_code}: {e}")

#     frappe.logger().info("✔ Task generation completed.")


# def calculate_next_due_date(current_date, frequency):
#     if frequency == 'Daily':
#         return add_days(current_date, 1)
#     elif frequency == 'Weekly':
#         return add_days(current_date, 7)
#     elif frequency == 'By Weekly':
#         return add_days(current_date, 14)
#     elif frequency == 'Monthly':
#         return current_date + relativedelta(months=1)
#     elif frequency == 'Quarterly':
#         return current_date + relativedelta(months=3)
#     elif frequency == 'Half-Yearly':
#         return current_date + relativedelta(months=6)
#     elif frequency == 'Yearly':
#         return current_date + relativedelta(years=1)
#     elif frequency == 'Two-Yearly':
#         return current_date + relativedelta(years=2)
#     elif frequency == 'Five-Yearly':
#         return current_date + relativedelta(years=5)
#     return current_date
