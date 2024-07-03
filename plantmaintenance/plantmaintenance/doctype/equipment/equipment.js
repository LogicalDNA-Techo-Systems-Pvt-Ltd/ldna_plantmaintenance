// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Equipment", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on('Equipment', {
    plant: function(frm){
        if (frm.doc.plant){
            frm.set_value('location', ''); 
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_location_list_based_on_plant',
                args: {
                    plant: frm.doc.plant,
                },
                callback: function(response){
                    if (response.message){
                        console.log(response.message)
                        var Location = response.message
                        frm.set_query('location', () => {
                            return {
                                filters: {
                                    location: ['in', Location]
                                }
                            }
                        })
                    }
                }
            })
        }
    },
    location: function(frm){
        if (frm.doc.location){
            frm.set_value('functional_location','');
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_functional_location_list_based_on_location',
                args: {
                    location: frm.doc.location,
                },
                callback: function(response){
                    if (response.message){
                        console.log(response.message)
                        var FunctionalLocation = response.message
                        frm.set_query('functional_location', () => {
                            return {
                                filters: {
                                    functional_location: ['in', FunctionalLocation]
                                }
                            }
                        })
                    }
                }
            })
        }
    },
    functional_location: function(frm){
        if (frm.doc.functional_location){
            frm.set_value('section','')
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_section_based_on_func_location',
                args: {
                    func_loc: frm.doc.functional_location,
                },
                callback: function(response){
                    if (response.message){
                        
                        var Section = response.message
                        console.log(Section)

                        frm.set_query('section', () => {
                            return {
                                filters: {
                                    section: ['in', Section]
                                }
                            }
                        })
                    }
                }
            })

        }
    },
    section: function(frm){
        if (frm.doc.section){
            frm.set_value('work_center','')
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.doctype.equipment.equipment.get_work_center_based_on_section',
                args: {
                    section: frm.doc.section,
                },
                callback: function(response){
                    if (response.message){
                        console.log(response.message)
                        var WorkCenter = response.message
                        frm.set_query('work_center', () => {
                            return {
                                filters: {
                                    work_center: ['in', WorkCenter]
                                }
                            }
                        })
                    }
                }
            })

        }
    },
});

// function filterChildFields(frm, tableName, fieldTrigger, fieldName, fieldFiltered) {
//     frm.fields_dict[tableName].grid.get_field(fieldFiltered).get_query = function(doc, cdt, cdn) {
//         var child = locals[cdt][cdn];
//         return {    
//             filters:[
//                 [fieldName, '=', child[fieldTrigger]]
//             ]
//         }
//     }
// }






        
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
