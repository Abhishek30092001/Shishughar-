# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StockChildtable(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		closing_stock: DF.Float
		month: DF.Link | None
		name: DF.Int | None
		opening_stock: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		quantity_received: DF.Float
		stock_item: DF.Link | None
		usage: DF.Float
		wastage: DF.Float
		year: DF.Link | None
	# end: auto-generated types

	pass
