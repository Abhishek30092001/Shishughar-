# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Vaccines(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		categories: DF.Data | None
		days: DF.Int
		name: DF.Int | None
		site_for_vaccinations: DF.Data | None
		vaccine: DF.Data | None
		vaccine_id: DF.Data | None
	# end: auto-generated types

	pass
