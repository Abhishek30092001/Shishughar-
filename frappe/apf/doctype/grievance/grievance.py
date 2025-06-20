# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Grievance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		any_other: DF.Data | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Data | None
		block_id: DF.Link
		creche_id: DF.Link
		description: DF.LongText
		district_id: DF.Link
		gp_id: DF.Link
		grievance_date: DF.Date
		grievance_guid: DF.Data | None
		image: DF.AttachImage | None
		name: DF.Int | None
		partner_id: DF.Link
		priority: DF.Link | None
		state_id: DF.Link
		status: DF.Link | None
		title: DF.Link
		village_id: DF.Link
	# end: auto-generated types

	pass
