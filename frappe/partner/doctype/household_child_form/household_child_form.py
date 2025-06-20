# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HouseholdChildForm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		any_other_gender: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		appupdated_by: DF.Data | None
		appupdated_on: DF.Datetime | None
		child_age: DF.Int
		child_dob: DF.Date | None
		child_name: DF.Data
		current_creche: DF.Int
		deleted_by: DF.Data | None
		deleted_on: DF.Date | None
		gender_id: DF.Link
		hhcguid: DF.Data | None
		hhguid: DF.Data | None
		is_active: DF.Check
		is_deleted: DF.Check
		is_dob_available: DF.Check
		is_verified: DF.Check
		name: DF.Int | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		relation_with_child_other: DF.Data | None
		relationship_with_child: DF.Link | None
		verified_by: DF.Data | None
		verified_on: DF.Datetime | None
	# end: auto-generated types

	pass
