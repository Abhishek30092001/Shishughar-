# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheCheckIn(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.visit_purpose_child_table.visit_purpose_child_table import VisitPurposechildtable
		from frappe.types import DF

		any_other: DF.Data | None
		app_created_by: DF.Data | None
		app_created_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		block_id: DF.Link
		ccinguid: DF.Data | None
		checkin_location: DF.SmallText | None
		creche_id: DF.Link
		creche_image: DF.Attach | None
		date_of_checkin: DF.Date
		district_id: DF.Link
		gp_id: DF.Link
		image_preview: DF.Check
		latitude: DF.Data
		longitude: DF.Data
		name: DF.Int | None
		partner_id: DF.Link
		picture: DF.AttachImage | None
		remarks: DF.SmallText | None
		state_id: DF.Link
		supervisor_id: DF.Link | None
		village_id: DF.Link
		visit_purpose: DF.TableMultiSelect[VisitPurposechildtable]
	# end: auto-generated types

	pass
