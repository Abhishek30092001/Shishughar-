# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Village(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.caste_child_table.caste_child_table import Castechildtable
		from frappe.apf.doctype.demographic_details.demographic_details import DemographicDetails
		from frappe.types import DF

		block_id: DF.Link
		caste: DF.TableMultiSelect[Castechildtable]
		demographical: DF.Table[DemographicDetails]
		district_id: DF.Link
		gp_id: DF.Link
		is_active: DF.Check
		languages_spoken: DF.Data | None
		livelihood_pattern: DF.Data | None
		name: DF.Int | None
		no_of_hamlets_in_the_village: DF.Int
		pvtg: DF.Data | None
		pvtg_check: DF.Check
		sc: DF.Data | None
		st: DF.Data | None
		state_id: DF.Link
		village_code: DF.Data | None
		village_hi: DF.Data | None
		village_name: DF.Data
		village_od: DF.Data | None
	# end: auto-generated types

	pass
