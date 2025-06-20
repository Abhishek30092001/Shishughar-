# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheRequisition(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.requisition_child_table.requisition_child_table import RequisitionChildtable
		from frappe.types import DF

		app_updated_by: DF.Data | None
		app_updated_on: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Data | None
		bal_quantity: DF.Float
		block_id: DF.Link
		buffer: DF.Float
		cal_quantity: DF.Float
		creche_id: DF.Link
		district_id: DF.Link
		gp_id: DF.Link
		month: DF.Link | None
		name: DF.Int | None
		partner_id: DF.Link
		requisition_list: DF.Table[RequisitionChildtable]
		rguid: DF.Data | None
		state_id: DF.Link
		village_id: DF.Link
		year: DF.Link | None
	# end: auto-generated types

	pass
