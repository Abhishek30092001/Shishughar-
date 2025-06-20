# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.entitlement_child_table.entitlement_child_table import Entitlementchildtable
		from frappe.apf.doctype.specially_abled_child_table.specially_abled_child_table import Speciallyabledchildtable
		from frappe.types import DF

		any_other: DF.Data | None
		any_other_gender: DF.Data | None
		any_other_relation: DF.Data | None
		any_other_specify_illness: DF.Data | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Data | None
		birth_order_of_the_child: DF.Int
		block_id: DF.Link
		chhguid: DF.Data | None
		child_dob: DF.Date | None
		child_name: DF.Data | None
		child_specially_abled: DF.Check
		created_by: DF.Data | None
		created_on: DF.Datetime | None
		currently_brestfeeding: DF.Check
		district_id: DF.Link
		do_they_migrate_for_work: DF.Check
		does_child_have_any_disability: DF.Check
		does_child_have_any_longterm_illness_more_than_6_months: DF.Check
		education_level_of_parentscaregiver: DF.Link | None
		entitlement_any_other: DF.Data | None
		entitlement_received_by_the_family_at_present: DF.TableMultiSelect[Entitlementchildtable]
		entitlement_received_id: DF.Data | None
		family_lives_in: DF.Link | None
		father_name: DF.Data | None
		gender_id: DF.Link | None
		gp_id: DF.Link
		hhguid: DF.Data | None
		how_many_siblings_does_the_child_have: DF.Int
		if_yes: DF.Link | None
		is_active: DF.Check
		is_the_child_enrolled_for_take_home_ration: DF.Check
		land_available_for_cultivation: DF.Check
		mobile: DF.Data | None
		mother_name: DF.Data | None
		name: DF.Int | None
		name_of_primary_caregiver: DF.Data | None
		relationship_with_child: DF.Link | None
		source_of_drinking_water_in_the_household: DF.Link | None
		specially_abled_option: DF.TableMultiSelect[Speciallyabledchildtable]
		state_id: DF.Link
		type_of_house: DF.Link | None
		updated_by: DF.Data | None
		updated_on: DF.Datetime | None
		village_id: DF.Link
	# end: auto-generated types

	pass
