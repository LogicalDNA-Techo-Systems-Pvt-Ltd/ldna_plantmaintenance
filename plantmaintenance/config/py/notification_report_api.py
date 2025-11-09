

import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=False)
def get_notification_report(filters=None):
    try:
        if not frappe.has_permission("Task Detail", "read"):
            frappe.throw(_("You don't have permission to access this report"))
        
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        if filters.get("from_date"):
            from frappe.utils import getdate
            filters["from_date"] = getdate(filters["from_date"])
        
        if filters.get("to_date"):
            from frappe.utils import getdate
            filters["to_date"] = getdate(filters["to_date"])
        
        from plantmaintenance.plantmaintenance.report.notification_reports.notification_reports import execute
        
        columns, data = execute(filters)
        
        response = {
            "success": True,
            "message": _("Report data fetched successfully"),
            "total_records": len(data),
            "columns": columns,
            "data": data
        }
        
        return response
    
    except frappe.PermissionError:
        frappe.log_error(frappe.get_traceback(), "Notification Report API - Permission Error")
        return {
            "success": False,
            "message": _("Permission Denied. You don't have access to this report."),
            "data": []
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Notification Report API Error")
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@frappe.whitelist(allow_guest=False)
def get_notification_report_filters():
    try:
        filters_data = {
            "success": True,
            "filters": {
                "work_centers": frappe.get_all("Work Center", pluck="name", order_by="name"),
                "equipment_groups": frappe.get_all("Equipment Group", pluck="name", order_by="name"),
                "locations": frappe.get_all("Location", pluck="name", order_by="name"),
                "statuses": ["Open", "Working", "Pending Review", "Completed", "Cancelled"],
                "types": ["Breakdown Maintenance", "Preventive Maintenance", "Predictive Maintenance", "Routine Maintenance"],
                "frequencies": ["Daily", "Weekly", "Monthly", "Quarterly", "Half Yearly", "Yearly"]
            }
        }
        return filters_data
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Notification Report Filters API Error")
        return {
            "success": False,
            "message": str(e),
            "filters": {}
        }


@frappe.whitelist(allow_guest=False)
def export_notification_report(filters=None, format_type="json"):
    try:
        result = get_notification_report(filters)
        
        if not result.get("success"):
            return result
        
        if format_type == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            headers = [col["label"] for col in result["columns"]]
            writer.writerow(headers)
            
            for row in result["data"]:
                row_data = [row.get(col["fieldname"], "") for col in result["columns"]]
                writer.writerow(row_data)
            
            return {
                "success": True,
                "format": "csv",
                "data": output.getvalue()
            }
        
        else: 
            return result
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Notification Report Export API Error")
        return {
            "success": False,
            "message": str(e)
        }