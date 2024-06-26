// // Copyright (c) 2024, LogicalDNA and contributors
// // For license information, please see license.txt


frappe.ui.form.on('Task Allocation', {
    refresh: function(frm) {
        frm.add_custom_button(__('Generate Task'), function(){
        },).css({
            'background-color': 'black',  
            'color': 'white'
        });

        if (!frm.custom_buttons_created) {
            
            const buttonContainer = $('<div class="custom-button-container"></div>').appendTo(frm.fields_dict['button_container'].wrapper);

            $('<button class="btn btn-primary" style="margin-right: 10px;">Load Tasks</button>').appendTo(buttonContainer).click(function() {
                load_tasks(frm);
            });

            $('<button class="btn btn-primary" style="margin-right: 10px;">Download Tasks Excel</button>').appendTo(buttonContainer).click(function() {
                download_tasks_excel(frm);
            });

            $('<button class="btn btn-primary" style="margin-right: 10px;">Upload Assignment Excel</button>').appendTo(buttonContainer).click(function() {
                upload_assignemnt_excel(frm);
            });

            frm.custom_buttons_created = true;
        }
        
    }
});
