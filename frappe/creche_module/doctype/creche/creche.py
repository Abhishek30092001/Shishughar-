# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Creche(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.creche_module.doctype.creche_caregiver.creche_caregiver import CrecheCaregiver
		from frappe.types import DF

		app_created_by: DF.Data | None
		app_created_on: DF.Date | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Date | None
		block_id: DF.Link
		checking: DF.Data | None
		creche_caregiver_table: DF.Table[CrecheCaregiver]
		creche_closing_date: DF.Date | None
		creche_closing_time: DF.Time | None
		creche_hi: DF.Data | None
		creche_id: DF.Data | None
		creche_name: DF.Data
		creche_od: DF.Data | None
		creche_opening_date: DF.Date | None
		creche_openning_time: DF.Time | None
		creche_status_id: DF.Link | None
		deleted_by: DF.Data | None
		deleted_on: DF.Date | None
		district_id: DF.Link
		gp_id: DF.Link
		hard_to_reach: DF.Check
		image: DF.Attach | None
		is_active: DF.Check
		latitude: DF.Data | None
		longitude: DF.Data | None
		name: DF.Int | None
		old_creche: DF.Check
		partner_id: DF.Link
		phase: DF.Link | None
		state_id: DF.Link
		supervisor_id: DF.Link
		type_of_creche_house: DF.Link | None
		village_id: DF.Link
		weekly_holiday_id: DF.Link | None
	# end: auto-generated types

	pass
