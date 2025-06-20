# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheStatus(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		creche_status: DF.Data | None
		creche_status_hi: DF.Data | None
		creche_status_od: DF.Data | None
		is_active: DF.Check
		name: DF.Int | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
