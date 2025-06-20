import frappe
from frappe.utils.file_manager import upload
@frappe.whitelist()
def upload_image(doctype,docname,filename,isprivate,filedata,docfield):
	upload()
	update_image_to_field(doctype,docname,docfield)
	return 'r'
