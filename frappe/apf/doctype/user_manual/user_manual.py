# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class UserManual(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attachment: DF.Attach | None
		language: DF.Literal["English", "Hindi", "Odia"]
		name: DF.Int | None
		url: DF.Data | None
		version: DF.Data | None
	# end: auto-generated types

	pass
