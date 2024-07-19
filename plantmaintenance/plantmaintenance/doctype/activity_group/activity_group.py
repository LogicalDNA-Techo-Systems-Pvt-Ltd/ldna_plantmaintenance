# Copyright (c) 2024, LogicalDNA and contributors
# For license information, please see license.txt

 

import frappe
from frappe.model.document import Document

class ActivityGroup(Document):
    def validate(self):
        self.remove_duplicate_activities()

    def remove_duplicate_activities(self):
        unique_activities = {}
        duplicates = []

        for act in self.get('activity'):
                key = act.activity
                if key in unique_activities:
                        duplicates.append(act)
                else:
                    unique_activities[key] = act
        for duplicate in duplicates:
               self.remove(duplicate)

    def remove(self, act):
         self.get('activity').remove(act)
