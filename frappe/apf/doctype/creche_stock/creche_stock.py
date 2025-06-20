# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheStock(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.stock_child_table.stock_child_table import StockChildtable
		from frappe.types import DF

		app_updated_by: DF.Data | None
		app_updated_on: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Data | None
		block_id: DF.Link
		creche_id: DF.Link
		district_id: DF.Link
		gp_id: DF.Link
		month: DF.Link | None
		name: DF.Int | None
		partner_id: DF.Link
		sguid: DF.Data | None
		state_id: DF.Link
		stock_list: DF.Table[StockChildtable]
		village_id: DF.Link
		year: DF.Link | None
	# end: auto-generated types

	pass
