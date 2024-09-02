
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
    refresh: function (listview) {
        setTimeout(function() {
            $(".list-row-container .list-row").each(function (i, obj) {
                var row = $(this);
                
                var statusField = listview.data[i] ? listview.data[i].status : '';
                
                
                if (statusField === 'Overdue') {
                    var workflowStateElement = row.find(".indicator-pill");
                    if (workflowStateElement.length) {
                        workflowStateElement.css('background-color', 'red'); 
                    }
                }
            });
        }, 1); 
    },
    onload: function(listview) {
        let today = frappe.datetime.get_today();
        listview.filter_area.add([[listview.doctype, 'plan_start_date', '=', today]]);

        listview.refresh();
    }
};
