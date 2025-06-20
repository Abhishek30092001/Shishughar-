# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrechePlanned(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		block_id: DF.Link | None
		district_id: DF.Link | None
		month: DF.Link | None
		name: DF.Int | None
		partner_id: DF.Link | None
		planned: DF.Int
		state_id: DF.Link | None
		year: DF.Link | None
	# end: auto-generated types

	pass
