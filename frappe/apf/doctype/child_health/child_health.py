# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildHealth(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		action_taken: DF.LongText
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		block_id: DF.Link
		child_health_guid: DF.Data | None
		child_id: DF.Link
		childenrolledguid: DF.Data | None
		creche_id: DF.Link | None
		date: DF.Date
		district_id: DF.Link
		gp_id: DF.Link
		name: DF.Int | None
		partner_id: DF.Link
		state_id: DF.Link
		symptoms: DF.LongText
		village_id: DF.Link
	# end: auto-generated types

	pass
