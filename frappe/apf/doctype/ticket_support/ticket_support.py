# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TicketSupport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		assign_to: DF.Literal["N/A", "Satish", "Abhishek"]
		attachment: DF.Attach | None
		backend_issue_category: DF.Literal["API", "Bug In Web", "Bug in Mobile", "Data Issue"]
		block: DF.Link | None
		creche_id: DF.Link | None
		date: DF.Date | None
		description: DF.TextEditor | None
		issue_cause_category: DF.Literal["User issue category", "Unable to Sync", "Data not visible", "Data Synced but not visible on web", "Report related issues", "Master\u00a0data\u00a0missing", "App Bug", "Web Bug", "App\u00a0development"]
		issue_on_web__mobile: DF.Literal["Web", "Mobile"]
		name: DF.Int | None
		partner: DF.Link | None
		priority: DF.Literal["High", "Medium", "Low"]
		state: DF.Link | None
		status: DF.Literal["New", "With Backend Team", "Need More Info", "Resolved", "Closed", "Cancelled", "Duplicate", "Feature\u00a0Request"]
		ticket_created_on: DF.Datetime | None
		title: DF.Data
		user_login_mobile_no: DF.Data
	# end: auto-generated types

	pass
