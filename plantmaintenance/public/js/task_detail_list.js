frappe.listview_settings['Task Detail'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Load Task'), function() {
            frappe.msgprint(__('Custom Load Task Button Clicked'));
        });
    }
};


frappe.views.calendar["Task Detail"] = {

	field_map: {
		"start": "plan_start_date",
		"end": "plan_end_date",
        "title": "parameter",
		"frequency": "frequency",
		"allDay": "allDay",
		// "progress": "progress"
	}
};