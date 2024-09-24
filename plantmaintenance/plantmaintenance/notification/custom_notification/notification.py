import frappe
import requests
import json


@frappe.whitelist()
def send_onesignal_notification(email,contents,urlm):
    url = "https://api.onesignal.com/notifications?c=push"
    formatted_contents = f"{contents} Click here to view: {urlm}"


    payload = {
        "app_id": "9b2f794c-30a2-4cde-8cde-595677f346b5",
         "contents": {
            "en": formatted_contents
    },
   
    "include_external_user_ids": [email],
    
    }
   
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Basic N2I3MmJhYzYtZDZmNi00ZTEwLWExYWMtZDY4MGU1YTkwYTNh"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.text)

    if response.status_code == 200:
        return "Notification sent successfully."
    else:
        frappe.throw("Failed to send notification.")
        
   