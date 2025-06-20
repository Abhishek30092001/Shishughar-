# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Phase(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		name: DF.Int | None
		phase_hi: DF.Data | None
		phase_od: DF.Data | None
		phases: DF.Data | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
