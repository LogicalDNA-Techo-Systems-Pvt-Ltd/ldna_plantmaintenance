import frappe

@frappe.whitelist()
def fetch_report(report_name=None, from_date=None, to_date=None, filters=None):
    """
    Fetch report data for user

    Args:
        report_name: Name of the report to run
        from_date: Start date (default: yesterday)
        to_date: End date (default: today)
        filters: Additional filters as JSON string or dict
    """
    from frappe.desk.query_report import run as run_report
    from frappe.utils import today, add_days, now

    if not report_name:
        report_name="Notification API Report"

    # Validate report exists
    if not frappe.db.exists("Report", report_name):
        return {"success": False, "message": f"Report '{report_name}' not found."}

    # Set default dates
    if not from_date:
        from_date = add_days(today(), -1)  # yesterday
    if not to_date:
        to_date = today()

    # Parse filters
    if isinstance(filters, str):
        try:
            filters = frappe.parse_json(filters)
        except Exception:
            filters = {}
    elif not filters:
        filters = {}

    # Add date filters
    filters.update({
        "from_date": from_date,
        "to_date": to_date
    })

    try:
        # Run the report
        result = run_report(report_name, filters=filters)

        # Update last sync time
        frappe.db.set_single_value("Notification API", "last_sync", now())
        frappe.db.commit()

        return {
            "success": True,
            "message": "Report fetched successfully",
            "report_name": report_name,
            "from_date": from_date,
            "to_date": to_date,
            "columns": result.get("columns", []),
            "data": result.get("result", []),
            "total_rows": len(result.get("result", []))
        }
    except Exception as e:
        frappe.log_error(f"Error fetching report {report_name}: {str(e)}")
        return {"success": False, "message": str(e)}