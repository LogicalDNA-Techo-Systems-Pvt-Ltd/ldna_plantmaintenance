// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.ui.form.on("Schedule List", {
	refresh(frm) {

        frm.add_custom_button(__('Schedule Task'), function() {
            // Handle button click event
            // Redirect to another DocType
            frappe.set_route('Form', 'Task Allocation');
        });

         
         


        if (frm.fields_dict.generate_schedule) {
            $(frm.fields_dict.generate_schedule.input).off('click').on('click', () => {
                frappe.model.clear_table(frm.doc, "scheduled_details");

                let frequency = frm.doc.frequency;
                let numberOfVisits = frm.doc.number_of_visits;

                let planDate = frappe.datetime.str_to_obj(frm.doc.plan_date);
                for (let i = 0; i < numberOfVisits; i++) {
                    let maintenanceDate = new Date(planDate);

                    if (frequency === 'Daily') {
                        maintenanceDate.setDate(planDate.getDate() + i);
                    } else if (frequency === 'Weekly') {
                        maintenanceDate.setDate(planDate.getDate() + i * 7);
                    } else if (frequency === 'Monthly') {
                        maintenanceDate.setMonth(planDate.getMonth() + i);
                    } else if (frequency === 'Yearly') {
                        maintenanceDate.setFullYear(planDate.getFullYear() + i);
                    } else if (frequency === 'Random') {
                         let randomDays = Math.floor(Math.random() * 365) + 1;
                        maintenanceDate.setDate(planDate.getDate() + randomDays);
                    }


                    maintenanceDate = frappe.datetime.obj_to_str(maintenanceDate);

                    let child = frappe.model.add_child(frm.doc, "scheduled_details");

                    child.no = i + 1;
                    child.plant = frm.doc.plant;
                    child.section = frm.doc.section;
                    child.maintenance_date = maintenanceDate;
                 }

                 frm.refresh_field("scheduled_details");
            });
        }


        

         
},

});
