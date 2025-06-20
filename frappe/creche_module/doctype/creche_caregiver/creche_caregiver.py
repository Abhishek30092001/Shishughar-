# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheCaregiver(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		app_updated_by: DF.Data | None
		app_updated_on: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Data | None
		caregiver_code: DF.Data | None
		caregiver_name: DF.Data
		cgguid: DF.Data | None
		date_of_joinning: DF.Date
		date_of_leaving: DF.Date | None
		is_active: DF.Check
		mobile_no: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reason_for_caregiver_exit: DF.Link | None
	# end: auto-generated types

	pass




