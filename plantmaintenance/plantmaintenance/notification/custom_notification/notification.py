import frappe
import requests
import json

@frappe.whitelist()
def send_onesignal_notification(content,user_external_id):
  
    url = "https://api.onesignal.com/notifications?c=push"
    
    payload = {
     
        "app_id": "53a209a0-ad8d-4072-ad67-e1c1919ca14f",
        "contents": {"en": content},
        "headings": {"en": "Notification Title"},
        "include_external_user_ids": user_external_id
    }

    headers = {
        
        "accept": "application/json",   
        "content-type": "application/json",
        "Authorization": "BASIC ZmFiYjJlZjgtOGRiZS00MWUzLWE1ZDktYjMxOWVlZGQ3OTNm"
    }
    
   
    response = requests.post(url, headers=headers, data=json.dumps(payload))
   
    if response.status_code == 200:
        return "Notification sent successfully."
    else:
        frappe.throw("Failed to send notification.")
