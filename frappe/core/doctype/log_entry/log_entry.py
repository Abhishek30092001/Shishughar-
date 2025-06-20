# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LogEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		docname: DF.Data | None
		doctype_name: DF.Data | None
		event: DF.Data | None
		json: DF.LongText | None
		timestamp: DF.Datetime | None
		user: DF.Data | None
	# end: auto-generated types

	pass
