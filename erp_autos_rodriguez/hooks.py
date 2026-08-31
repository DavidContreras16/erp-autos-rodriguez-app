app_name = "erp_autos_rodriguez"
app_title = "AutosRodriguez"
app_publisher = "ERP"
app_description = "Aplicacion para el manejo de compra y venta de vehiculos"
app_email = "AutosRodriguez@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "erp_autos_rodriguez",
# 		"logo": "/assets/erp_autos_rodriguez/logo.png",
# 		"title": "AutosRodriguez",
# 		"route": "/erp_autos_rodriguez",
# 		"has_permission": "erp_autos_rodriguez.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erp_autos_rodriguez/css/erp_autos_rodriguez.css"
# app_include_js = "/assets/erp_autos_rodriguez/js/erp_autos_rodriguez.js"

# include js, css files in header of web template
# web_include_css = "/assets/erp_autos_rodriguez/css/erp_autos_rodriguez.css"
# web_include_js = "/assets/erp_autos_rodriguez/js/erp_autos_rodriguez.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erp_autos_rodriguez/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "erp_autos_rodriguez/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erp_autos_rodriguez.utils.jinja_methods",
# 	"filters": "erp_autos_rodriguez.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erp_autos_rodriguez.install.before_install"
# after_install = "erp_autos_rodriguez.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "erp_autos_rodriguez.uninstall.before_uninstall"
# after_uninstall = "erp_autos_rodriguez.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "erp_autos_rodriguez.utils.before_app_install"
# after_app_install = "erp_autos_rodriguez.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "erp_autos_rodriguez.utils.before_app_uninstall"
# after_app_uninstall = "erp_autos_rodriguez.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "erp_autos_rodriguez.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erp_autos_rodriguez.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erp_autos_rodriguez.tasks.all"
# 	],
# 	"daily": [
# 		"erp_autos_rodriguez.tasks.daily"
# 	],
# 	"hourly": [
# 		"erp_autos_rodriguez.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erp_autos_rodriguez.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erp_autos_rodriguez.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "erp_autos_rodriguez.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "erp_autos_rodriguez.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erp_autos_rodriguez.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erp_autos_rodriguez.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["erp_autos_rodriguez.utils.before_request"]
# after_request = ["erp_autos_rodriguez.utils.after_request"]

# Job Events
# ----------
# before_job = ["erp_autos_rodriguez.utils.before_job"]
# after_job = ["erp_autos_rodriguez.utils.after_job"]

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
# 	"erp_autos_rodriguez.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


fixtures = [
    {"dt": "Workflow", "filters": [["name", "=", "Flujo Vehiculo"]]},
    {"dt": "Workflow State"},
    {"dt": "Workflow Action Master"},
    {"dt": "Server Script", "filters": [["name", "=", "Vehiculo - Generar Titulo"]]},
    {"dt": "Number Card", "filters": [["name", "=", "Total Vehiculos"]]},
    {"dt": "Dashboard Chart", "filters": [["name", "=", "Vehiculos por Estado"]]},
    {"dt": "Kanban Board", "filters": [["name", "=", "Vehiculos - Flujo"]]},
]
