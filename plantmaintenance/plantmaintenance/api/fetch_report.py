import frappe
from frappe.desk.query_report import run
import json

@frappe.whitelist(allow_guest=True)
def get_notification_report_public(from_date, to_date):
    """
    Public API endpoint for Notification Reports
    """
    
    try:
        frappe.set_user("api@sbpl.com")
        
        filters = {
            "from_date": from_date,
            "to_date": to_date
        }
        
        result = run(
            report_name="Notification API Report",
            filters=filters,
            ignore_prepared_report=True, 
            user="api@sbpl.com"
        )
        
        # Clean response
        return {
            "success": True,
            "columns": result.get("columns", []),
            "data": result.get("result", []),
            "total_records": len(result.get("result", [])),
            "execution_time": result.get("execution_time", 0)
        }
        
    except Exception as e:
        frappe.log_error(f"Notification Report Error: {str(e)}", "Public Report API")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch report data"
        }