// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.ui.form.on("Schedule List", {
<<<<<<< Updated upstream
    refresh(frm) {
=======
    onload: function(frm) {
        frm.set_query("parameter_group", function() {
            return {
                filters: {
                    "is_active": 1
                }
            };
        });
    },
	refresh(frm) {

>>>>>>> Stashed changes
        frm.add_custom_button(__('Schedule Task'), function() {
            // Handle button click event
            // Redirect to another DocType
            frappe.set_route('Form', 'Task Allocation');
        });

        if (frm.fields_dict.generate_schedule) {
            $(frm.fields_dict.generate_schedule.input).off('click').on('click', () => {
                frappe.model.clear_table(frm.doc, "schedule_details");

                let frequency = frm.doc.frequency;
                let numberOfVisits = frm.doc.number_of_visits;


                let startDate = frappe.datetime.str_to_obj(frm.doc.start_date);
                for (let i = 0; i < numberOfVisits; i++) {
                    let maintenanceDate = new Date(startDate);

                    if (frequency === 'Daily') {
                        maintenanceDate.setDate(startDate.getDate() + i);
                    } else if (frequency === 'Weekly') {
                        maintenanceDate.setDate(startDate.getDate() + i * 7);
                    } else if (frequency === 'Monthly') {
                        maintenanceDate.setMonth(startDate.getMonth() + i);
                    } else if (frequency === 'Yearly') {
                        maintenanceDate.setFullYear(startDate.getFullYear() + i);
                    } else if (frequency === 'Random') {
                         let randomDays = Math.floor(Math.random() * 365) + 1;
                        maintenanceDate.setDate(startDate.getDate() + randomDays);


                    maintenanceDate = frappe.datetime.obj_to_str(maintenanceDate);

                    let child = frappe.model.add_child(frm.doc, "schedule_details");
                    child.no = i + 1;
                    child.plant = frm.doc.plant;
                    child.section = frm.doc.section;
                    child.maintenance_date = maintenanceDate;
                }
                frm.refresh_field("schedule_details");
            });
        }
    },
    
    parameter_group: function(frm) {
        if (frm.doc.parameter_group) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Parameter Group',
                    filters: {
                        name: frm.doc.parameter_group
                    }
                },
                callback: function(r) {
                    if (r.message) {
                        console.log("--------------", r.message);
                        frm.clear_table('parameter'); // Corrected the method name
                        r.message.parameter.forEach(function(item) {
                            let child = frm.add_child('parameter');
                            child.parameter = item.parameter;
                            child.numeric = item.numeric;
                            child.minimum_value = item.minimum_value;
                            child.maximum_value = item.maximum_value;
                            child.acceptance_criteria = item.acceptance_criteria;
                        });
                        frm.refresh_field('parameter');
                    }
                }
            });
        }
    }
});
