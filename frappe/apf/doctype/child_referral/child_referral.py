# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChildReferral(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.diagnosis_child_table.diagnosis_child_table import Diagnosischildtable
		from frappe.apf.doctype.referral_child_table.referral_child_table import Referralchildtable
		from frappe.apf.doctype.treatment_child_table.treatment_child_table import Treatmentchildtable
		from frappe.apf.doctype.treatment_nrc_child_table.treatment_nrc_child_table import TreatmentNRCchildtable
		from frappe.types import DF

		admission_date: DF.Date | None
		age_on_referral: DF.Int
		any_medical_major_illnesss: DF.Check
		any_other: DF.Data | None
		any_other_referred_to: DF.Data | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		block_id: DF.Link
		cgmguid: DF.Data | None
		child_id: DF.Link | None
		child_referral_guid: DF.Data | None
		child_status: DF.Link
		childenrolledguid: DF.Data | None
		creche_id: DF.Link | None
		date_of_referral: DF.Date
		diagnosis: DF.TableMultiSelect[Diagnosischildtable]
		diagnosis_other: DF.Data | None
		discharge_date: DF.Date | None
		district_id: DF.Link
		gp_id: DF.Link
		height_on_referral: DF.Float
		name: DF.Int | None
		partner_id: DF.Link
		referral_reason: DF.TableMultiSelect[Referralchildtable]
		referred_to: DF.Link | None
		referred_to_nrc: DF.Link | None
		remarks: DF.LongText | None
		schedule_date: DF.Date | None
		special_instruction: DF.Data | None
		state_id: DF.Link
		treatment_details: DF.TableMultiSelect[Treatmentchildtable]
		treatment_details_nrc: DF.TableMultiSelect[TreatmentNRCchildtable]
		treatment_details_nrc_other: DF.Data | None
		treatment_details_other: DF.Data | None
		village_id: DF.Link
		visit_count: DF.Int
		visit_date: DF.Date
		weight_on_discharge: DF.Float
		weight_on_referral: DF.Float
	# end: auto-generated types

	pass
