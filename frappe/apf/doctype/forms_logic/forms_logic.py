# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FormsLogic(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		algorithm_expression: DF.Data | None
		dependent_controls: DF.Data | None
		doc: DF.Link | None
		is_active: DF.Check
		name: DF.Int | None
		parent_control: DF.Data | None
		type_of_logic_id: DF.Link | None
	# end: auto-generated types

	pass
