# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HouseholdForm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.partner.doctype.household_child_form.household_child_form import HouseholdChildForm
		from frappe.types import DF

		adults_above_18_years: DF.Int
		any_other_gender: DF.Data | None
		any_other_religion: DF.Data | None
		app_created_by: DF.Data | None
		app_created_on: DF.Datetime | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		block_id: DF.Link
		children: DF.Table[HouseholdChildForm]
		children_3_to_6_years: DF.Int
		children_6_to_18_years: DF.Int
		children__3_years: DF.Int
		creche_id: DF.Link
		date_of_visit: DF.Date
		deleted_by: DF.Data | None
		deleted_on: DF.Datetime | None
		district_id: DF.Link
		do_you_take_your_children_along_with_you: DF.Check
		does_anyone_from_your_family_migrate_every_year: DF.Check
		family_members_enganged_as_migrant_workers: DF.Int
		gp_id: DF.Link
		hamlet: DF.Data | None
		hhguid: DF.Data | None
		hhid: DF.Data | None
		hosuehold_head_name: DF.Data
		is_active: DF.Check
		is_anyone_of_your_family_a_migrant_worker: DF.Check
		is_deleted: DF.Check
		is_the_family_a_pvtg: DF.Check
		landmark: DF.Data | None
		name: DF.Int | None
		no_of_months_the_migrants_were_away_last_year: DF.Link | None
		no_of_pregnant_women: DF.Int
		number_of_family_members: DF.Int
		partner_id: DF.Link
		primary_occupation_id: DF.Link | None
		primary_occupation_other: DF.Data | None
		pvtg_name: DF.Data | None
		religion: DF.Link | None
		remarks: DF.LongText | None
		respondent_age: DF.Int
		respondent_gender_id: DF.Link
		respondent_name: DF.Data
		social_category_id: DF.Link | None
		state_id: DF.Link
		verification_status: DF.Link | None
		verified_by: DF.Data | None
		verified_on: DF.Datetime | None
		village_id: DF.Link
		who_looks_after_them_at_home: DF.Data | None
	# end: auto-generated types

	pass
