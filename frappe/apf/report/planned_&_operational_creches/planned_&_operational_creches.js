// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Planned & Operational Creches"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": ["2022", "2023", "2024", "2025"],
			"default": new Date().getFullYear().toString(),
			"on_change": function () {
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": [
				{ "value": "1", "label": "January" },
				{ "value": "2", "label": "February" },
				{ "value": "3", "label": "March" },
				{ "value": "4", "label": "April" },
				{ "value": "5", "label": "May" },
				{ "value": "6", "label": "June" },
				{ "value": "7", "label": "July" },
				{ "value": "8", "label": "August" },
				{ "value": "9", "label": "September" },
				{ "value": "10", "label": "October" },
				{ "value": "11", "label": "November" },
				{ "value": "12", "label": "December" }
			],
			"default": (new Date().getMonth() + 1).toString(),
			"on_change": function () {
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "partner",
			"label": __("Partner"),
			"fieldtype": "Link",
			"options": "Partner",
			"default": frappe.defaults.get_user_default("partner"),
			"on_change": function () {
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "state",
			label: __("State"),
			fieldtype: "Link",
			options: "State",
			get_query: function () {
				return {
					filters: {
						"is_active": 1
					}
				};
			},
			on_change: function () {
				frappe.query_report.set_filter_value("district", "");
				frappe.query_report.set_filter_value("block", "");
				frappe.query_report.set_filter_value("gp", "");
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "district",
			label: __("District"),
			fieldtype: "Link",
			options: "District",
			get_query: function () {
				let state = frappe.query_report.get_filter_value("state");
				return state ? { filters: { state_id: state } } : {};
			},
			on_change: function () {
				frappe.query_report.set_filter_value("block", "");
				frappe.query_report.set_filter_value("gp", "");
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "block",
			label: __("Block"),
			fieldtype: "Link",
			options: "Block",
			get_query: function () {
				let district = frappe.query_report.get_filter_value("district");
				return district ? { filters: { district_id: district } } : {};
			},
			on_change: function () {
				frappe.query_report.set_filter_value("gp", "");
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "level",
			"label": __("Level"),
			"fieldtype": "Select",
			"options": [
				{ "value": "", "label": __("Level") },
				{ "value": "1", "label": __("Partner") },
				{ "value": "2", "label": __("State") },
				{ "value": "3", "label": __("District") },
				{ "value": "4", "label": __("Block") },
			],
			"default": "",
			"on_change": function () {
				frappe.query_report.refresh();
			}
		},
		// {
		// 	"fieldname": "date_range",
		// 	"label": __("Creche Opening Date"),
		// 	"fieldtype": "DateRange",
		// 	"default": "",
		// 	"on_change": function () {
		// 		frappe.query_report.refresh();
		// 	}
		// }
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Check if this is the Total row
		if (data && (data.partner === "Total" || data.state === "Total")) {
			value = `<strong>${value}</strong>`; // Make text bold
		}

		return value;
	}
};
