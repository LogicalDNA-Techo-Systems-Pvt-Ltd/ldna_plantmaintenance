// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

 
frappe.ui.form.on('Parameter', {
    onload: function(frm) {
        render_radio_buttons(frm); 
    },
    refresh: function(frm) {
        render_radio_buttons(frm);  
    },
    before_save: function(frm) {
         HandleParameters(frm);  
    }

});

function render_radio_buttons(frm) {
    const wrapper = frm.fields_dict['parameter_type'].wrapper;  
    $(wrapper).empty();  

    const radioContainer = $('<div class="radio-buttons-container"></div>');
    radioContainer.css('display', 'flex');

    const binaryRadio = $(`
        <div class="radio-button">
            <label>
                <input type="radio" name="parameter_type" value="Binary" ${frm.doc.parameter_type === 'Binary' ? 'checked' : ''}>
                Binary
            </label>
        </div>`);
    
    binaryRadio.css('margin-right', '20px');  
    binaryRadio.find('input').on('change', function() {
        frm.set_value('parameter_type', 'Binary'); 
    });
    radioContainer.append(binaryRadio); 

    const numericRadio = $(`
        <div class="radio-button">
            <label>
                <input type="radio" name="parameter_type" value="Numeric" ${frm.doc.parameter_type === 'Numeric' ? 'checked' : ''}>
                Numeric
            </label>
        </div>`);
    
    numericRadio.find('input').on('change', function() {
        frm.set_value('parameter_type', 'Numeric'); 
    });
    radioContainer.append(numericRadio); 

    const listRadio = $(`
        <div class="radio-button">
            <label>
                <input type="radio" name="parameter_type" value="List" ${frm.doc.parameter_type === 'List' ? 'checked' : ''}>
                List
            </label>
        </div>`);
    listRadio.css('margin-left', '20px');

    listRadio.find('input').on('change', function() {
        frm.set_value('parameter_type', 'List'); 
    });
    radioContainer.append(listRadio);

    $(wrapper).append(radioContainer); 
}


function HandleParameters(frm) {
    var parameterType = frm.doc.parameter_type;
     


     if (parameterType === 'Binary') {
         frm.set_value('minimum_value', '');
        frm.set_value('maximum_value', '');
        frm.set_value('values', '');
        frm.set_value('number_of_readings','');

     } else if (parameterType === 'Numeric') {
        frm.set_value('acceptance_criteria', '');
        frm.set_value('values', '');
          
    } else if (parameterType === 'List') {
        frm.set_value('acceptance_criteria', '');
        frm.set_value('minimum_value', '');
        frm.set_value('maximum_value', '');
        frm.set_value('number_of_readings','')
    }
    
}

frappe.ui.form.on('Parameter', {
    refresh: function(frm) {
        if (!frm.is_new() && frm.doc.parameter) {
            frm.add_custom_button(__('Equipment List'), function() {
                frappe.set_route('List', 'Equipment', {
                   
                });
            }, __("View"));
        } 
    }
});  

