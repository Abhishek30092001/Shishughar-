# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class State(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		census_state_code: DF.Data | None
		is_active: DF.Check
		state_code: DF.Data
		state_hi: DF.Data | None
		state_name: DF.Data
		state_od: DF.Data | None
	# end: auto-generated types

	pass
