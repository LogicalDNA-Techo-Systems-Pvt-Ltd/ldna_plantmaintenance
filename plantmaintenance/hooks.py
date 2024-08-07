app_name = "plantmaintenance"
app_title = "Plantmaintenance"
app_publisher = "LogicalDNA"
app_description = "Equipment Tracking and Maintenance"
app_email = "shreyas.n@logicaldna.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/home/pragati/frappe-bench/apps/plantmaintenance/plantmaintenance/public/css/custom.css"
app_include_js = "/assets/plantmaintenance/js/workspace.js"

# include js, css files in header of web template
# web_include_css = "/home/pragati/frappe-bench/apps/plantmaintenance/plantmaintenance/public/css/custom.css"
# web_include_js = "/assets/plantmaintenance/js/plantmaintenance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "plantmaintenance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"Task Detail" : "/home/pragati/frappe-bench/apps/plantmaintenance/plantmaintenance/public/js/task_detail_list.js"}
doctype_list_js = {"Task Detail" : "public/js/task_detail_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "plantmaintenance/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# hooks.py

# hooks.py

on_session_creation = [
    "plantmaintenance.plantmaintenance.custom.role.role_based_home_page"
]


# role_home_page = {
#     "Maintenance Manager": "maintenance-manager",
#     "Maintenance User": "maintenance-user",
#     "System Manager": "system-workspace"
# }


# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "plantmaintenance.utils.jinja_methods",
# 	"filters": "plantmaintenance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "plantmaintenance.install.before_install"
# after_install = "plantmaintenance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "plantmaintenance.uninstall.before_uninstall"
# after_uninstall = "plantmaintenance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "plantmaintenance.utils.before_app_install"
# after_app_install = "plantmaintenance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "plantmaintenance.utils.before_app_uninstall"
# after_app_uninstall = "plantmaintenance.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "plantmaintenance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	# "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
    "Task Detail":"plantmaintenance.plantmaintenance.doctype.task_detail.task_detail_permission.task_detail_permission"
}
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }



# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }


override_doctype_class = {
	"Role": "plantmaintenance.plantmaintenance.custom.role.Role"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
    "Parameter": {
        "on_update": "plantmaintenance.plantmaintenance.doctype.parameter.parameter.update_activity_parameter"
    },
    "Task Detail": {
        "on_update": "plantmaintenance.plantmaintenance.doctype.equipment.equipment.equipment_task_details"
    },
    "Task Allocation": {
        "before_save": "plantmaintenance.plantmaintenance.doctype.task_allocation.task_allocation.compare_and_delete_tasks"
    },
    "Equipment": {
        "before_save": "plantmaintenance.plantmaintenance.doctype.equipment.equipment.update_activity_group_and_delete_tasks"
    },
    "Activity":{
        "on_update":"plantmaintenance.plantmaintenance.doctype.activity.activity.delete_task_depends_activity"
    },
    "Activity Group":{
        "on_update":"plantmaintenance.plantmaintenance.doctype.activity_group.activity_group.delete_task_depends_activity_group"
    }    
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"plantmaintenance.tasks.all"
# 	],
# 	"daily": [
# 		"plantmaintenance.tasks.daily"
# 	],
# 	"hourly": [
# 		"plantmaintenance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"plantmaintenance.tasks.weekly"
# 	],
# 	"monthly": [
# 		"plantmaintenance.tasks.monthly"
# 	],
# }


# scheduler_events = {
#     "daily": [
#         "plantmaintenance.task_detail.update_task_status"
#     ]
# }

# scheduler_events = {
#     "cron": {
#         "1 * * * *": [
#             "plantmaintenance.plantmaintenance.doctype.task_detail.task_detail.update_task_status"
#         ]
#     }
# }


# Testing
# -------

# before_tests = "plantmaintenance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "plantmaintenance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Equipment": "plantmaintenance.plantmaintenance.doctype.equipment.equipment_dashboard.get_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["plantmaintenance.utils.before_request"]
# after_request = ["plantmaintenance.utils.after_request"]

# Job Events
# ----------
# before_job = ["plantmaintenance.utils.before_job"]
# after_job = ["plantmaintenance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"plantmaintenance.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
app_include_css = "/assets/plantmaintenance/css/notification.css"
