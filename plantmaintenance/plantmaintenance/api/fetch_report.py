import frappe
from frappe.desk.query_report import run

@frappe.whitelist(allow_guest=True)
def get_notification_report_public(from_date, to_date):
    try:
        frappe.set_user("Administrator")
        frappe.set_user("api@sbpl.com")
        
        filters = {
            "from_date": from_date,
            "to_date": to_date
        }
        
        result = run(
            report_name="Notification Reports",
            filters=filters,
            ignore_prepared_report=False
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Notification Report Error: {str(e)}")
        return {
            "error": True,
            "message": str(e)
        }