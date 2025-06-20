import frappe
from frappe.utils.password import passlibctx 

def check_password_appi(user, pwd, doctype="User", fieldname="password"):
	"""Checks if user and password are correct, else raises frappe.AuthenticationError"""

	result = frappe.db.sql("""select `name`, `password` from `__Auth`
		where `doctype`=%(doctype)s and `name`=%(name)s and `fieldname`=%(fieldname)s and `encrypted`=0""",
		{'doctype': doctype, 'name': user, 'fieldname': fieldname}, as_dict=True)

	if not result or not passlibctx.verify(pwd, result[0].password):
		frappe.msgprint("Incorrect User or Password", raise_exception=True)
	return user 


