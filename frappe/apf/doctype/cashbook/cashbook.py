# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Cashbook(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		any_other: DF.Data | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		block_id: DF.Link
		cashbook_guid: DF.Data | None
		closing_balance_for_month: DF.Int
		comments: DF.Data | None
		creche_id: DF.Link
		date: DF.Date
		district_id: DF.Link
		expence: DF.Int
		expense_amount: DF.Int
		expense_details: DF.Data | None
		gp_id: DF.Link
		item: DF.Link
		money_received_by_creche_caregiver: DF.Link | None
		month: DF.Link | None
		name: DF.Int | None
		opening_balance: DF.Int
		partner_id: DF.Link
		receipt: DF.Int
		receipt_amount: DF.Int
		receipt_date: DF.Date
		state_id: DF.Link
		village_id: DF.Link
	# end: auto-generated types

	pass
