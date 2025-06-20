# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MobileAppVersionRelease(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		app_version: DF.Data
		date_of_release: DF.Date
		name: DF.Int | None
		release_notes: DF.SmallText | None
	# end: auto-generated types

	pass
