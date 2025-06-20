# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HeightforageBoys(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		age_in_days: DF.Int
		age_in_months: DF.Int
		green: DF.Float
		l: DF.Data | None
		m: DF.Data | None
		name: DF.Int | None
		red: DF.Float
		s: DF.Data | None
		sd0: DF.Data | None
		sd1: DF.Data | None
		sd1neg: DF.Data | None
		sd2: DF.Data | None
		sd2neg: DF.Data | None
		sd3: DF.Data | None
		sd3neg: DF.Data | None
		sd4: DF.Data | None
		sd4neg: DF.Data | None
		yellow_max: DF.Float
		yellow_min: DF.Float
	# end: auto-generated types

	pass
