from frappe import _

def get_data():
    return{
        
        "transactions": [
            {
                "label": _("Reference"),
                "items": [
                    "Activity Group",
                    
                ]},
                {
                "label": _("Transactions"),
                "items": [
                    "Task Allocation",
                    "Task Detail"
                   
                ]
            },
        ]
       
    }
 