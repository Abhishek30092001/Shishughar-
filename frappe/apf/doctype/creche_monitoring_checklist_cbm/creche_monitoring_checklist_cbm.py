# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheMonitoringChecklistCBM(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		action_undertaken_red_flag_children: DF.Link | None
		additional_information: DF.Data | None
		all_child_cards: DF.Link | None
		any_additional_info: DF.Data | None
		any_additional_information: DF.Data | None
		any_new_toys_made_in_current_month: DF.Link | None
		any_other_traning_needed: DF.Check
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		are_the_children_in_creche_using_toilet: DF.Check
		are_the_children_nail_cut_and_cleaned: DF.Link | None
		are_the_dishes_washed_after_each_meal: DF.Link
		are_the_faeces_cleaned: DF.Link
		are_the_faeces_properly_disposed_of: DF.Link | None
		are_the_floors_clean: DF.Check
		are_the_food_and_ingredients_kept_covered_and_properly: DF.Check
		are_the_leftovers_discarded_on_the_same_day: DF.Check
		block_id: DF.Link
		caregiver_additional_information: DF.Data | None
		cbmguid: DF.Data | None
		children_present_in_creche: DF.Int
		children_receive_days_egg_per_week_atleast: DF.Check
		community_growth_chart_poster: DF.Link | None
		creche_caregiver_getting_involved_in_feeding: DF.Link | None
		creche_id: DF.Link
		creche_register: DF.Link | None
		date_of_visit: DF.Date
		did_any_child_get_special_nutrition_care: DF.Link | None
		did_children_get_lemon_drop: DF.Link | None
		did_children_get_one_drop_extra_oil: DF.Link | None
		district_id: DF.Link
		do_creche_caregiver_wash_their_hand_with_soap: DF.Check
		does_the_menu_in_the_creche_follow_the_meal_plan_as_given: DF.Link | None
		early_childhood_activity_poster: DF.Link | None
		ecd_information: DF.Data | None
		entitlement_chart_poster: DF.Link | None
		entry_time: DF.Time | None
		exit_time: DF.Time | None
		feeding_information: DF.Data | None
		food: DF.Data | None
		food_menu_poster: DF.Link | None
		gp_id: DF.Link
		grievance_redressal_contact: DF.Link | None
		hygiene: DF.Data | None
		indent_and_receipt_book: DF.Link | None
		is_the_cms_app_uptodate_with_data: DF.Link | None
		is_the_creche_premises_clean: DF.Check
		is_the_ecd_activities_happened_on_the_day_of_visit: DF.Link | None
		is_trash_disposed_off_properly: DF.Check
		know_your_area_poster: DF.Link | None
		line_listing_book: DF.Link | None
		mention_action_taken: DF.Link | None
		name: DF.Int | None
		need_refresher_on_understanding_anthropometric: DF.Check
		need_refresher_training_creche_operational_management: DF.Check
		need_refresher_training_on_ecd: DF.Check
		need_refresher_training_on_health_and_hygiene: DF.Check
		need_refresher_traning_on_register: DF.Check
		observation_after_use_toilets: DF.Link | None
		observation_during_cooking_and_feeding: DF.Check
		observation_during_cooking_and_feeding_children: DF.Link | None
		observation_during_feeding_do_creche_caregivers_wash_children: DF.Link | None
		on_the_day_of_the_visit_did_you_observe_children: DF.Link | None
		partner_id: DF.Link
		referral: DF.Data | None
		state_id: DF.Link
		the_creche_name_displayed_outside_creche: DF.Data | None
		toys_are_available: DF.Link
		training_information: DF.Data | None
		village_id: DF.Link
		whether_the_nails_of_creche_caregiver_cut_and_clean: DF.Check
	# end: auto-generated types

	pass
