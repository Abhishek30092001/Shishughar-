# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildGrowthMonitoring(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.anthropromatic_data.anthropromatic_data import AnthropromaticData
		from frappe.types import DF

		anthropromatic_details: DF.Table[AnthropromaticData]
		block_id: DF.Link
		cgmguid: DF.Data | None
		created_by: DF.Data | None
		created_on: DF.Datetime | None
		creche_id: DF.Link
		district_id: DF.Link
		gp_id: DF.Link
		is_active: DF.Check
		measurement_date: DF.Date
		name: DF.Int | None
		partner_id: DF.Link
		state_id: DF.Link
		updated_by: DF.Data | None
		updated_on: DF.Datetime | None
		village_id: DF.Link
	# end: auto-generated types

	pass
