# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheCommitteeMeeting(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.attendees_child_table.attendees_child_table import Attendeeschildtable
		from frappe.apf.doctype.attendees_details.attendees_details import AttendeesDetails
		from frappe.types import DF

		any_other: DF.Data | None
		app_updated_by: DF.Data | None
		app_updated_on: DF.Datetime | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Datetime | None
		attendees_data: DF.TableMultiSelect[Attendeeschildtable]
		attendees_table: DF.Table[AttendeesDetails]
		block_id: DF.Link
		ccguid: DF.Data | None
		creche_id: DF.Link
		discussion: DF.LongText | None
		district_id: DF.Link
		gp_id: DF.Link
		image: DF.Attach | None
		major_topic: DF.LongText
		meeting_date: DF.Date
		name: DF.Int | None
		no_of_parents_attended: DF.Int
		number_of_participants: DF.Int
		partner_id: DF.Link
		state_id: DF.Link
		village_id: DF.Link
	# end: auto-generated types

	pass
