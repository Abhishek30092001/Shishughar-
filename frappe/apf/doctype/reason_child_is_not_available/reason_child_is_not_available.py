# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ReasonChildisnotavailable(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		is_active: DF.Check
		name: DF.Int | None
		reason_child_is_not_a_available: DF.Data | None
		reason_child_is_not_available_hi: DF.Data | None
		reason_child_is_not_available_od: DF.Data | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
