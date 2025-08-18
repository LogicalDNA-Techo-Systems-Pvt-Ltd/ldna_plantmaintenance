import frappe
from frappe.utils import getdate, today
from plantmaintenance.plantmaintenance.doctype.generate_allocation.generate_allocation import load_tasks

def generate_tasks_daily():
    try:
        end_date = getdate(today())

        load_tasks(
            plant=None,
            location=None,
            plant_section=None,
            work_center=None,
            end_date=end_date,
            equipment_list=None 
        )

        frappe.logger().info("Daily task generation successful for date: " + str(end_date))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Daily Task Generation Failed")
