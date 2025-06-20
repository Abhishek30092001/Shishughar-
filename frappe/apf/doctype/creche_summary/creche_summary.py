# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheSummary(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		avg_attd_per_day: DF.Data | None
		block_id: DF.Link | None
		block_name: DF.Data | None
		c_idx: DF.Data | None
		c_name: DF.Data | None
		children_attendance_atleast_one_day: DF.Data | None
		creche_closing_date: DF.Date | None
		creche_id: DF.Link | None
		creche_name: DF.Data | None
		creche_opening_date: DF.Date | None
		creche_status_by_day: DF.LongText | None
		creche_status_id: DF.Data | None
		district_id: DF.Link | None
		district_name: DF.Data | None
		eligible_children: DF.Data | None
		enrolled_children: DF.Data | None
		gp_id: DF.Link | None
		gp_name: DF.Data | None
		max_attd: DF.Data | None
		mean_attd: DF.Data | None
		min_attd: DF.Data | None
		name: DF.Int | None
		partner_id: DF.Link | None
		partner_name: DF.Data | None
		phase: DF.Data | None
		state_id: DF.Link | None
		state_name: DF.Data | None
		supervisor_id: DF.Data | None
		supervisor_name: DF.Data | None
		year: DF.Data | None
	# end: auto-generated types

	pass
