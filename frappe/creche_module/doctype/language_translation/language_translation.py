# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LanguageTranslation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		english: DF.Data
		hindi: DF.Data | None
		key_name: DF.Data | None
		odia: DF.Data | None
	# end: auto-generated types

	pass
