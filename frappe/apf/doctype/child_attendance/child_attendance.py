# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildAttendance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.child_attendance_list.child_attendance_list import ChildAttendanceList
		from frappe.types import DF

		app_created_by: DF.Data | None
		app_created_on: DF.Datetime | None
		block_id: DF.Link
		breakfast: DF.Int
		childattendancelist: DF.Table[ChildAttendanceList]
		childattenguid: DF.Data | None
		close_time: DF.Time | None
		creche_id: DF.Link
		date_of_attendance: DF.Date
		district_id: DF.Link
		egg: DF.Int
		evening_snacks: DF.Int
		gp_id: DF.Link
		is_shishu_ghar_is_closed_for_the_day: DF.Check
		isecd_activities_done_for_the_day: DF.Check
		lunch: DF.Int
		name: DF.Int | None
		open_time: DF.Time | None
		partner_id: DF.Link
		reason_for_closure_id: DF.Link | None
		reason_other: DF.Data | None
		state_id: DF.Link
		village_id: DF.Link
	# end: auto-generated types

	pass
