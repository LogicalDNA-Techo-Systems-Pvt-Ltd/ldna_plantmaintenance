// Copyright (c) 2024, LogicalDNA and contributors
// For license information, please see license.txt

frappe.ui.form.on("Settings", {
    validate: function(frm) {
        if (frm.doc.end_date && frm.doc.start_date && frm.doc.end_date < frm.doc.start_date) {
            frappe.msgprint(__('End Date should be greater than or equal to Start Date'));
            frappe.validated = false;
        }
    },
    
    onload: function(frm) {
        frappe.call({
            method: "plantmaintenance.plantmaintenance.doctype.settings.settings.get_context",
            callback: function(r) {
                var data = r.message;
                $(frm.fields_dict["subscribe_and_unsubscribe"].wrapper).html(data);
                refresh_field("subscribe_and_unsubscribe");
                bindOneSignalButtons(frm);
            }
        });
    }
});
function bindOneSignalButtons(frm) {
    $('#subscribe').on('click', function(event) {
        event.preventDefault();
        var userId = getUserId();
        if (userId) {
            OneSignal.push(["registerForPushNotifications"]);
                    var externalUserId = frappe.session.user; 
                    OneSignal.push(function() {
                    OneSignal.setExternalUserId(externalUserId);
                    updateButtonState(true); 
                })
        } else {
            frappe.msgprint(__('User is not logged in.'));
        }
    });

   
    $('#unsubscribe').on('click', function(event) {
            OneSignal.push(function() {
                OneSignal.setSubscription(false).then(function() {
                    updateButtonState(false); 
                });
            });
    });
    checkSubscriptionStatus();
}

function checkSubscriptionStatus() {
    OneSignal.push(function() {
        OneSignal.getSubscription().then(function(isSubscribed) {
            updateButtonState(isSubscribed);
        });
    });
}
function updateButtonState(isSubscribed) {
    if (isSubscribed) {
        $('#unsubscribe').show();
        $('#subscribe').hide();
    } else {
        $('#unsubscribe').hide();
        $('#subscribe').show();
    }
}
