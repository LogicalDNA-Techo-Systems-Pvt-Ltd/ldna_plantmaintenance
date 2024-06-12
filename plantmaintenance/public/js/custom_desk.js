
frappe.ui.Desktop.prototype.setup_custom_buttons = function() {
    var toolbarIcons = $('#toolbar-icons');
    // console.log("Toolbar Icons Element: ", toolbarIcons);
    if (toolbarIcons.length) {
        toolbarIcons.append('<a class="custom-btn" href="http://logicaldna:8000/app/plant-maintenance-dashboard">Custom Button</a>');
}

var original_refresh = frappe.ui.Desktop.prototype.refresh;
frappe.ui.Desktop.prototype.refresh = function() {
    original_refresh.call(this);
    this.setup_custom_buttons();
};
}

