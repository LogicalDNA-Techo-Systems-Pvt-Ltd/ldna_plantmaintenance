import frappe
import requests
import json

@frappe.whitelist()
def send_onesignal_notification(content,user_external_id):
  
    url = "https://api.onesignal.com/notifications?c=push"
    
    payload = {
     
        "app_id": "36e69d56-7847-41a0-bd6c-ea63020a2e19",
        "contents": {"en": content},
        "headings": {"en": "Notification Title"},
        "include_external_user_ids": user_external_id
    }

    headers = {
        
        "accept": "application/json",   
        "content-type": "application/json",
        "Authorization": "BASIC OWQ1YjBjZTQtZTFjZC00MDZkLWEwMjktZmVmN2M0MDk3YjM4"
    }
    
   
    response = requests.post(url, headers=headers, data=json.dumps(payload))
   
    if response.status_code == 200:
        return "Notification sent successfully."
    else:
        frappe.throw("Failed to send notification.")
