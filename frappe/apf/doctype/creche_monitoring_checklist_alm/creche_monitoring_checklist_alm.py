# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheMonitoringChecklistALM(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_remarks: DF.Data | None
		almguid: DF.Data | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		block_id: DF.Link
		broom_dustpan: DF.Link | None
		chart_poster: DF.Link | None
		child_cards: DF.Link | None
		child_register: DF.Check
		childhood_activity: DF.Link | None
		children_present_in_creche: DF.Int
		clock: DF.Link | None
		cms_uptodate: DF.Link | None
		containers: DF.Link | None
		creche_id: DF.Link
		creche_name_displayed: DF.Link | None
		creche_register: DF.Link
		date_of_visit: DF.Date
		dishwashing_soap: DF.Link | None
		district_id: DF.Link
		durries: DF.Link | None
		dustbin: DF.Link | None
		entitlement_chart: DF.Link | None
		entry_time: DF.Time | None
		exit_time: DF.Time | None
		first_aid: DF.Link | None
		food_menu: DF.Link | None
		gp_id: DF.Link
		handwashing_soap: DF.Link | None
		know_area: DF.Link | None
		ladle_drinking_water: DF.Link | None
		listing_book: DF.Link | None
		measuring_cup: DF.Link | None
		mosquito_net: DF.Link | None
		nail_cutter: DF.Link | None
		name: DF.Int | None
		partner_id: DF.Link
		plastic_buckets: DF.Link | None
		plastic_mug: DF.Link | None
		receipt_book: DF.Link | None
		redressal_contact: DF.Link | None
		register_additional_info: DF.Data | None
		smokeless_chulha: DF.Link | None
		soap_case: DF.Link | None
		state_id: DF.Link
		steel_box: DF.Link | None
		steel_drum_with_cover: DF.Link | None
		stock_additional_information: DF.Data | None
		storage_of_material: DF.Check
		toys: DF.Link | None
		toys_are_there: DF.Link
		utensils_cooking: DF.Link | None
		village_id: DF.Link
		weather_all_centrally_supplied: DF.Check
	# end: auto-generated types

	pass
