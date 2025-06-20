# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class District(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		district_code: DF.Data
		district_name: DF.Data
		is_active: DF.Check
		name: DF.Int | None
		state_id: DF.Link
	# end: auto-generated types

	pass
