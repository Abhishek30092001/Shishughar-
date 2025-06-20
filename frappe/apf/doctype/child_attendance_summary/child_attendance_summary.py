# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildAttendanceSummary(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		absent_days: DF.Data | None
		age_at_enrollment_in_months: DF.Data | None
		attend_slot: DF.Data | None
		attendance: DF.LongText | None
		block_id: DF.Link | None
		block_name: DF.Data | None
		c_idx: DF.Data | None
		child_id: DF.Data | None
		child_profile_id: DF.Data | None
		childattenguid: DF.Data | None
		childenrolledguid: DF.Data | None
		creche_closing_date: DF.Data | None
		creche_id: DF.Link | None
		creche_name: DF.Data | None
		creche_opening_date: DF.Data | None
		creche_status_id: DF.Data | None
		date_of_enrollment: DF.Data | None
		date_of_exit: DF.Data | None
		district_id: DF.Link | None
		district_name: DF.Data | None
		eligible_days: DF.Data | None
		gender_id: DF.Data | None
		gp_id: DF.Link | None
		gp_name: DF.Data | None
		hhcguid: DF.Data | None
		hhguid: DF.Data | None
		name: DF.Int | None
		name_of_child: DF.Data | None
		partner_id: DF.Link | None
		partner_name: DF.Data | None
		phase: DF.Data | None
		present_days: DF.Data | None
		state_id: DF.Link | None
		state_name: DF.Data | None
		supervisor_id: DF.Data | None
		supervisor_name: DF.Data | None
		year: DF.Data | None
	# end: auto-generated types

	pass
