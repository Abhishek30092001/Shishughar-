# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DemographicDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		demo_guid: DF.Data | None
		demographic_details: DF.Link | None
		name: DF.Int | None
		no_of_hamlets_in_village: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		population_of_village: DF.Int
		population_q1: DF.Int
		population_q2: DF.Int
		population_q3: DF.Int
		population_q4: DF.Int
		total_no_of_village_in_village: DF.Int
		year_id: DF.Link | None
	# end: auto-generated types

	pass
