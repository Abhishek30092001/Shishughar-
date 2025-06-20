# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PartnerStock(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		is_active: DF.Check
		item_required_per_child_per_months: DF.Float
		items: DF.Data | None
		name: DF.Int | None
		partner_id: DF.Link | None
		partner_stock_hi: DF.Data | None
		partner_stock_od: DF.Data | None
		seq_id: DF.Int
		stock_type: DF.Link | None
	# end: auto-generated types

	pass
