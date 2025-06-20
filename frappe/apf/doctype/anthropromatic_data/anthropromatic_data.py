# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AnthropromaticData(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		age_months: DF.Int
		any_medical_major_illness: DF.Check
		awc: DF.Check
		cgmguid: DF.Data | None
		chhguid: DF.Data | None
		child_id: DF.Link | None
		childenrollguid: DF.Data | None
		do_you_have_height_weight: DF.Check
		dob_when_measurement_taken: DF.Date | None
		flag: DF.Int
		height: DF.Float
		height_for_age: DF.Float
		height_for_age_zscore: DF.Data | None
		illness_other: DF.Data | None
		measurement_equipment: DF.Link | None
		measurement_reason: DF.Link | None
		measurement_taken_date: DF.Date | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		re_age_months: DF.Int
		re_do_you_have_height_weight: DF.Check
		re_height: DF.Float
		re_height_for_age: DF.Float
		re_height_for_age_zscore: DF.Data | None
		re_measurement_equipment: DF.Link | None
		re_measurement_reason: DF.Link | None
		re_measurement_taken_date: DF.Date | None
		re_weight: DF.Float
		re_weight_for_age: DF.Float
		re_weight_for_age_zscore: DF.Data | None
		re_weight_for_height: DF.Float
		re_weight_for_height_zscore: DF.Data | None
		s_flag: DF.Int
		thr: DF.Check
		vhsnd: DF.Link | None
		weight: DF.Float
		weight_for_age: DF.Float
		weight_for_age_zscore: DF.Data | None
		weight_for_height: DF.Float
		weight_for_height_zscore: DF.Data | None
	# end: auto-generated types

	pass
