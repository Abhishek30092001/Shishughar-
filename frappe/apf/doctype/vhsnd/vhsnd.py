# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class VHSND(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		add_vhsnd: DF.Data | None
		is_active: DF.Check
		name: DF.Int | None
		seq_id: DF.Int
		vhsnd_hi: DF.Data | None
		vhsnd_od: DF.Data | None
	# end: auto-generated types

	pass
