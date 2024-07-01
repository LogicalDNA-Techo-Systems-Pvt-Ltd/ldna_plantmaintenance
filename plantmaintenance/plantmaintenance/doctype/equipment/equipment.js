// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Equipment", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on('Equipment', {
    on_hold: function(frm) {
        if (frm.doc.on_hold) {
            frm.set_value('on_scrap', 0);
        }
    },
    on_scrap: function(frm) {
        if (frm.doc.on_scrap) {
            frm.set_value('on_hold', 0);
        }
    }
});






        
// frappe.ui.form.on("Equipment",{
//     refresh: function(frm){
//         frm.get_field("equipment_code").wrapper.style.width = "50%";
//         frm.get_field("equipment_group").wrapper.style.width = "50%";
//         frm.get_field("company_code").wrapper.style.width = "50%";
//         frm.get_field("activity_group").wrapper.style.width = "50%";
//         frm.get_field("type_of_technical_object").wrapper.style.width = "50%";
//         frm.get_field("description_of_technical_object").wrapper.style.width = "50%";
//         frm.get_field("manufacturer_of_asset").wrapper.style.width = "50%";
//         frm.get_field("equipment_name").wrapper.style.width = "50%";

        
//     }   

// });









// frappe.ui.form.on("Equipment", {
//     onload: function(frm) {
//         // Define an empty array to store locations
//         var locations = [];

//         // Fetch locations from Plant doctype based on the selected plant in Equipment
//         frappe.call({
//             method: 'frappe.client.get_list',
//             args: {
//                 doctype: 'Plant',
//                 filters: {
//                     plant: frm.doc.plant  // Filter by the selected plant in Equipment
//                 },
//                 fields: ['location']  // Adjust fields as per your requirement
//             },
//             callback: function(r) {
//                 if (r.message && r.message.length > 0) {
//                     // Populate locations array with fetched locations
//                     locations = r.message.map(function(plant) {
//                         return plant.location;
//                     });

//                     // Set query for location field in Location child table
//                     frm.fields_dict['location'].grid.get_field('location').get_query = function(doc, cdt, cdn) {
//                         return {
//                             filters: {
//                                 'location': ['in', locations]
//                             }
//                         };
//                     };

//                     // Refresh the form to apply the query
//                     frm.refresh_field('location');
//                 }
//             }
//         });
//     }
// });
