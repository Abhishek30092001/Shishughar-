# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ReviewMeetings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.training_participants_child_table.training_participants_child_table import TrainingParticipantschildtable
		from frappe.types import DF

		block_id: DF.Link | None
		creche_caregiver_participated: DF.TableMultiSelect[TrainingParticipantschildtable]
		creche_id: DF.Link | None
		date_of_meeting: DF.Date | None
		district_id: DF.Link | None
		gp_id: DF.Link | None
		name: DF.Int | None
		partner_id: DF.Link | None
		remarks: DF.SmallText | None
		state_id: DF.Link | None
		topic_discussed: DF.SmallText | None
		village_id: DF.Link | None
	# end: auto-generated types

	pass
