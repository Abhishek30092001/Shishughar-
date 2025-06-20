# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildExit(Document):
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
		appcreated_on: DF.Datetime | None
		block_id: DF.Link
		child_exit_guid: DF.Data | None
		child_id: DF.Link | None
		childenrolledguid: DF.Data | None
		creche_id: DF.Link | None
		creche_name: DF.Link | None
		date_of_enrollment: DF.Date | None
		date_of_enrollment_awc: DF.Date | None
		date_of_exit: DF.Date
		district_id: DF.Link
		gp_id: DF.Link
		is_child_enrolled_awc: DF.Check
		name: DF.Int | None
		other_reason: DF.Data | None
		partner_id: DF.Link
		reason_for_exit: DF.Link
		state_id: DF.Link
		village_id: DF.Link
	# end: auto-generated types

	pass
