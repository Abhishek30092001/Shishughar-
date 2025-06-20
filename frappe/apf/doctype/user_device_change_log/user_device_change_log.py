# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class UserDeviceChangeLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		app_device_version: DF.Data | None
		created_on: DF.Datetime | None
		mobile_no: DF.Data | None
		name: DF.Int | None
		new_device_id: DF.Data | None
		old_device_id: DF.Data | None
	# end: auto-generated types

	pass
