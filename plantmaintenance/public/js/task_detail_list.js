frappe.listview_settings['Task Detail'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Load Task'), function() {
            frappe.msgprint(__('Custom Load Task Button Clicked'));
        });
    }
};
