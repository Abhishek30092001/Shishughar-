# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildEnrollmentandExit(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		age_at_enrollment_in_months: DF.Int
		age_of_exit: DF.Int
		app_updated_by: DF.Data | None
		app_updated_on: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Data | None
		block_id: DF.Link
		child_dob: DF.Date
		child_id: DF.Data | None
		child_name: DF.Data
		childenrollguid: DF.Data | None
		creche_id: DF.Link
		date_of_enrollment: DF.Date
		date_of_enrollment_awc: DF.Date | None
		date_of_exit: DF.Date | None
		district_id: DF.Link
		gender_id: DF.Link | None
		gp_id: DF.Link
		height: DF.Float
		height_for_age: DF.Float
		height_for_age_zscore: DF.Data | None
		hhcguid: DF.Data | None
		hhguid: DF.Data | None
		is_active: DF.Check
		is_child_enrolled_awc: DF.Check
		is_exited: DF.Check
		measurement_date: DF.Date | None
		measurement_equipment: DF.Link | None
		measurement_taken: DF.Check
		name: DF.Int | None
		other_reason: DF.Data | None
		partner_id: DF.Link
		reason_for_exit: DF.Link | None
		state_id: DF.Link
		village_id: DF.Link
		weight: DF.Float
		weight_for_age: DF.Float
		weight_for_age_zscore: DF.Data | None
		weight_for_height: DF.Float
		weight_for_height_zscore: DF.Data | None
	# end: auto-generated types

	pass
