
frappe.views.calendar["Task Detail"] = {

	field_map: {
		"start": "plan_start_date",
		"end": "plan_end_date",
        "title": "parameter",
		"frequency": "frequency",
		"allDay": "allDay",
	}
};
frappe.listview_settings['Task Detail'] = {
    onload: function(listview) {
        let today = frappe.datetime.get_today();
        listview.filter_area.add([[listview.doctype, 'plan_start_date', '=', today]]);

        listview.refresh();
    }
};
