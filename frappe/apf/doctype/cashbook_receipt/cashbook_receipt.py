# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CashbookReceipt(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Int
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		block_id: DF.Link
		cashbook_receipt_guid: DF.Data | None
		comments: DF.Data | None
		creche_id: DF.Link
		date: DF.Date
		district_id: DF.Link
		gp_id: DF.Link
		item: DF.Link | None
		name: DF.Int | None
		partner_id: DF.Link
		state_id: DF.Link
		status: DF.Link | None
		village_id: DF.Link
	# end: auto-generated types

	pass
