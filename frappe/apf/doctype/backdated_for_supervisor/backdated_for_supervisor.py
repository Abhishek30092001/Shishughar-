# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Backdatedforsupervisor(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		back_dated_data_entry_allowed: DF.Int
		data_edit_allowed: DF.Int
		date: DF.Date
		module: DF.Literal["", "Creche", "Creche Caregiver", "Household Form", "Child Profile", "Child Enrollment and Exit", "Child Exit", "Child Immunization", "Health Details", "Event Details", "Child Referral", "Child Follow up", "Creche Committee Meeting", "Child Attendance", "Child Growth Monitoring", "Creche Monitoring Checklist", "Cashbook", "Creche Stock", "Creche Check In", "Grievance", "Village"]
		name: DF.Int | None
		partner_id: DF.Link
		supervisor_id: DF.Link
		unique_id: DF.Data | None
	# end: auto-generated types

	pass
