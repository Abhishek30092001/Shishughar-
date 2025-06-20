# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.core.doctype.entitlement_child_table.entitlement_child_table import Entitlementchildtable
		from frappe.types import DF

		age_at_enrollment_in_months: DF.Int
		any_other_specify_illness: DF.Data | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Data | None
		birth_order_of_the_child: DF.Int
		chhguid: DF.Data | None
		child_dob: DF.Date
		child_id: DF.Data | None
		child_name: DF.Data
		childenrollguid: DF.Data | None
		created_by: DF.Data | None
		created_on: DF.Datetime | None
		creche_id: DF.Link
		currently_brestfeeding: DF.Check
		date_of_enrollment: DF.Date
		date_of_exit: DF.Date | None
		do_they_migrate_for_work: DF.Check
		does_child_have_any_disability: DF.Check
		does_child_have_any_longterm_illness_more_than_6_months: DF.Check
		education_level_of_parentscaregiver: DF.Link
		entitlement_any_other: DF.Data | None
		entitlement_received_by_the_family_at_present: DF.TableMultiSelect[Entitlementchildtable]
		entitlement_received_id: DF.Data | None
		family_lives_in: DF.Link | None
		gender_id: DF.Link
		hh_child_id: DF.Data | None
		how_many_siblings_does_the_child_have: DF.Int
		if_yes: DF.Link | None
		image_field: DF.Attach | None
		is_active: DF.Check
		is_exited: DF.Check
		is_the_child_enrolled_for_take_home_ration: DF.Check
		land_available_for_cultivation: DF.Check
		mobile: DF.Data | None
		name: DF.Int | None
		name_of_primary_caregiver: DF.Data | None
		partner: DF.Link | None
		relationship_with_child: DF.Link | None
		remarks: DF.Data | None
		source_of_drinking_water_in_the_household: DF.Link | None
		status: DF.Link | None
		type_of_house: DF.Link | None
		updated_by: DF.Data | None
		updated_on: DF.Datetime | None
		verification_date: DF.Date | None
	# end: auto-generated types

	pass
