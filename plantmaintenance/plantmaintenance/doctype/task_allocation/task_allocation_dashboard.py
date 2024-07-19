from frappe import _

def get_data():
    return{
        
        "transactions": [
            
            {
                "label": _("Plant Details"),
                "items": [
                    "Plant",
                    "Location",
                    "Functional Location",
                    "Section",
                    "Work Center"
                    
                ]},
             {
                "label": _("Transactions"),
                "items": [
                   "Task Detail"
                    
                ]},
            
        ]
       
    }
 