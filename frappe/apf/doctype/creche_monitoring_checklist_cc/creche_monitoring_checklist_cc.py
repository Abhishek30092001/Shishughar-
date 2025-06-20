# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheMonitoringChecklistCC(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		action_undertaken_red_flag_children: DF.Link | None
		additional_info: DF.Data | None
		additional_remarks: DF.Data | None
		addtional_info: DF.Data | None
		adequate_for_enrolled_children: DF.Check
		anganwadi_additional_info: DF.Data | None
		anthro_additional_info: DF.Data | None
		any_new_toy_made_in_the_current_months: DF.Check
		any_other: DF.Data | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		ask_practice: DF.Check
		block_id: DF.Link
		broom_dustpan: DF.Link | None
		bulb_in_creche: DF.Link | None
		caregiver_additional_info: DF.Data | None
		caregiver_getting_involved: DF.Link | None
		caregiver_vhnd: DF.Link | None
		chart_poster: DF.Link | None
		child_additional_info: DF.Data | None
		child_friendly_wall_paintings: DF.Check
		childhood_activity: DF.Link | None
		children_present_in_creche: DF.Int
		children_using_toilet: DF.Check
		cleanliness_additional_info: DF.Data | None
		clock: DF.Link | None
		cmc_cc_guid: DF.Data | None
		cms_uptodate: DF.Link | None
		containers: DF.Link | None
		creche_id: DF.Link
		creche_name_displayed: DF.Link | None
		creche_premises: DF.Check
		creche_recieve_light: DF.Check
		creche_register: DF.Link | None
		date_of_visit: DF.Date
		deworming: DF.Link | None
		dishes_washed: DF.Link | None
		dishwashing_soap: DF.Link | None
		district_id: DF.Link
		durries: DF.Link | None
		dustbin: DF.Link | None
		ecd_activities_happened: DF.Link | None
		ecd_additional_info: DF.Data | None
		egg_in_menu: DF.Link | None
		entitlement_chart: DF.Link | None
		entry_time: DF.Time | None
		exit_time: DF.Time | None
		faeces_cleaned: DF.Link | None
		faeces_disposed: DF.Link | None
		feedin_additional_info: DF.Data | None
		first_aid: DF.Link | None
		floors_clean: DF.Check
		food: DF.Data | None
		food_menu: DF.Link | None
		food_store: DF.Check
		gp_id: DF.Link
		growth_monitoring: DF.Link | None
		hand_washing_station: DF.Link | None
		hand_with_soap: DF.Link | None
		hygiene: DF.Data | None
		if_noreason: DF.Data | None
		immunization: DF.Link | None
		infantometer: DF.Link | None
		iron_folic_acid: DF.Link | None
		kitchen_gardner_setup: DF.Check
		kitchen_saprated: DF.Check
		know_area: DF.Link | None
		ladle_drinking_water: DF.Link | None
		leftover_discarded: DF.Check
		lemon_drop: DF.Link | None
		listing_book: DF.Link | None
		mealplan_manual: DF.Link | None
		measuring_cup: DF.Link | None
		mention_action_taken: DF.Link | None
		method_water_purification: DF.Link | None
		mosquito_net: DF.Link | None
		nail_cut_clean: DF.Check
		nail_cutter: DF.Link | None
		nails_cleaned: DF.Link | None
		name: DF.Int | None
		nutrition_care: DF.Link | None
		observation_during_cooking: DF.Check
		observation_during_feeding: DF.Link | None
		outdoor_area_to_play: DF.Check
		partner_id: DF.Link
		plastic_buckets: DF.Link | None
		plastic_mug: DF.Link | None
		reading_available_in_creche: DF.Check
		receipt_book: DF.Link | None
		receive_day_egg: DF.Check
		redressal_contact: DF.Link | None
		referral: DF.Data | None
		seprated_space_for_store: DF.Check
		smokeless_chulha: DF.Link | None
		soap_case: DF.Link | None
		source_of_electricity: DF.Link | None
		source_of_watersupply: DF.Data | None
		stadiometer: DF.Link | None
		state_id: DF.Link
		status_of_fencing: DF.Link | None
		steel_box: DF.Link | None
		steel_drum: DF.Link | None
		thr: DF.Link | None
		toilet_facility: DF.Link | None
		toilet_not_available: DF.Data | None
		toys: DF.Link | None
		toys_are_available: DF.Link | None
		trash_disposed: DF.Check
		use_of_toilet: DF.Link | None
		utensils_cooking: DF.Link | None
		village_id: DF.Link
		vitamin_a: DF.Link | None
		water_connection_kitchen: DF.Link | None
		water_connection_toilet: DF.Check
		water_purification_other: DF.Data | None
		water_purified_service: DF.Check
		weighing_scale: DF.Link | None
		window_in_creche: DF.Check
	# end: auto-generated types

	pass
