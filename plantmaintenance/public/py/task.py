import frappe
from frappe.utils import getdate, add_days
from dateutil.relativedelta import relativedelta
import calendar

@frappe.whitelist()
def generate_future_tasks():
    start_date = getdate("2025-02-11")
    today = getdate()
    end_date = add_days(today, 90)

    equipment_list = frappe.db.get_list(
        "Task Detail",
        filters={},
        pluck="equipment_code",
        distinct=True
    )

    if not equipment_list:
        frappe.logger().info("No equipment found for future task generation.")
        return

    frappe.logger().info(f"Starting scheduled task generation for equipment: {equipment_list}")

    for equipment_code in equipment_list:
        existing_tasks = frappe.get_all(
            "Task Detail",
            filters={
                "equipment_code": equipment_code,
                "plan_start_date": [">=", start_date]
            },
            fields=["equipment_code", "activity", "activity_group", "parameter", "frequency", "plan_start_date", "type"]
        )

        for task in existing_tasks:
            if task.get("type") and task["type"] != "Preventive":
                continue
            if not task.get("parameter"):
                continue

            frequency = task["frequency"]
            plan_start_date = getdate(task["plan_start_date"])
            # next_due_date = max(plan_start_date, today)
            next_due_date = plan_start_date

            while next_due_date <= end_date:
                task_exists = frappe.db.exists("Task Detail", {
                    "equipment_code": task["equipment_code"],
                    "activity": task["activity"],
                    "parameter": task["parameter"],
                    "plan_start_date": next_due_date
                })

                if task_exists:
                    next_due_date = calculate_next_due_date(next_due_date, frequency)
                    continue

                equipment_fields = ["equipment_name", "sub_section", "old_tag_dcs", "description"]
                equipment_name, sub_section, old_tag_dcs, description = frappe.db.get_value("Equipment", task['equipment_code'], equipment_fields)

                parameter_doc = frappe.get_doc("Parameter", task['parameter']) if task["parameter"] else None
                parameter_type = parameter_doc.parameter_type if parameter_doc else None
                minimum_value = parameter_doc.minimum_value if parameter_doc else None
                maximum_value = parameter_doc.maximum_value if parameter_doc else None
                standard_value = parameter_doc.standard_value if parameter_doc else None

                task_detail = frappe.new_doc("Task Detail")
                task_detail.update({
                    "approver": frappe.session.user if frappe.session.user else "Administrator",
                    "equipment_code": task['equipment_code'],
                    "equipment_name": equipment_name,
                    "activity_group": task['activity_group'],
                    "activity": task['activity'],
                    "parameter": task['parameter'],
                    "frequency": task['frequency'],
                    "plan_start_date": next_due_date,
                    "day": calendar.day_name[next_due_date.weekday()],
                    "date": next_due_date,
                    "unique_key": f"{task['equipment_code'][:3]}_{next_due_date}_{frappe.generate_hash(length=5)}",
                    "location": "",
                    "section": "",
                    "old_tag_dcs": old_tag_dcs,
                    "sub_section": sub_section,
                    "description": description,
                    "parameter_type": parameter_type,
                    "minimum_value": minimum_value,
                    "maximum_value": maximum_value,
                    "standard_value": standard_value
                })
                task_detail.insert(ignore_permissions=True)

                next_due_date = calculate_next_due_date(next_due_date, frequency)

    frappe.logger().info("Scheduled Task Generation Completed")


def calculate_next_due_date(current_date, frequency):
    if frequency == 'Daily':
        return add_days(current_date, 1)
    elif frequency == 'Weekly':
        return add_days(current_date, 7)
    elif frequency == 'By Weekly':
        return add_days(current_date, 14)
    elif frequency == 'Monthly':
        return current_date + relativedelta(months=1)
    elif frequency == 'Quarterly':
        return current_date + relativedelta(months=3)
    elif frequency == 'Half-Yearly':
        return current_date + relativedelta(months=6)
    elif frequency == 'Yearly':
        return current_date + relativedelta(years=1)
    elif frequency == 'Two-Yearly':
        return current_date + relativedelta(years=2)
    elif frequency == 'Five-Yearly':
        return current_date + relativedelta(years=5)
    return current_date
