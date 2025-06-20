# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class VaccineDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		name: DF.Int | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		vaccinated: DF.Check
		vaccination_date: DF.Date | None
		vaccine_created_at: DF.Data | None
		vaccine_id: DF.Link | None
		vaccine_updated_by: DF.Data | None
	# end: auto-generated types

	pass
