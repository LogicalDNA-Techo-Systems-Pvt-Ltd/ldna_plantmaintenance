// frappe.listview_settings['Task Detail'] = {
//     onload: function(listview) {
//         listview.page.add_inner_button(__('Load Task'), function() {
//             frappe.msgprint(__('Custom Load Task Button Clicked'));
//         });
//     }
// };


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


// frappe.listview_settings["Task Detail"] = {
//     add_fields: ["status"],
//     onload: function (doc) {
// 		console.log(doc)
// 		console.log("alll")
// 		console.log(doc.status)
//         console.log("outttttttttttttttttinnnnnnnnnnnnnnnn")
 
//         return [__("Open"), "green", "status,=,Open"];
        
// 	},
   
// };

// frappe.listview_settings['Task Detail'] = {
// 	add_fields: ['status'],
// 	get_indicator: function(doc) {
//         console.log(doc)
// 		        if(doc.status==="Open"){
// 	        	return [__(doc.status), "green", "status,=," + doc.status];
// 	        }
	       
// 	}
// };

frappe.listview_settings["Task Detail"] = {
    add_fields: ["workflow_state"],
    onload: function (listview) {
        // Save the original refresh method
        const original_refresh = listview.refresh;

        // Override the refresh method
        listview.refresh = function () {
            // Call the original refresh method
            original_refresh.apply(this, arguments);

            // Fetch data using frappe.call
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Task Detail",
                    fields: ["name", "workflow_state"],
                    limit_page_length: 100
                },
                callback: function (response) {
                    if (response.message && response.message.length > 0) {
                        console.log(response.message); // Log the data to inspect

                        // Iterate through the tasks and access workflow_state
                        response.message.forEach(task => {
                            console.log(`Task Name: ${task.name}, Workflow State: ${task.workflow_state}`);
                        });
                    } else {
                        console.log("No tasks found or data not yet loaded.");
                    }
                }
            });
        };
    }
};


frappe.listview_settings["Task Detail"] = {
    add_fields: ["workflow_state", "status"], 
    onload: function (listview) {
        const original_refresh = listview.refresh;

        listview.refresh = function () {
            
            original_refresh.apply(this, arguments);

            setTimeout(() => {
                if (this.data && this.data.length > 0) {
                    console.log(this.data); 

                    this.data.forEach(task => {
                        let color = "black"; 
                        if (task.status === "Overdue") {
                            color = "red";
                        }

                        console.log(`Task Name: ${task.name}, Workflow State: %c${task.workflow_state}`, `color: ${color}`);
                    });
                } else {
                    console.log("No tasks found or data not yet loaded.");
                }
            }, 100);
        };

    },
    formatters: {
        workflow_state: function (value, row, cell, formatter_params) {
            // const status = row.status; 
            const status = row.status || "";
            print(status)
            let color = "black";
            if (status === "Overdue") {
                color = "red";
            }

            return `<span style="color: ${color};">${value}</span>`;
			// return [__(doc.status), "green", "status,=," + doc.status];
        }
    }

};
