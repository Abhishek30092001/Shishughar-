frappe.query_reports["Average Attendance Child Wise"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": ["2022", "2023", "2024", "2025"],
			"default": new Date().getFullYear().toString(),
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": [
				{ "value": "1", "label": __("January") },
				{ "value": "2", "label": __("February") },
				{ "value": "3", "label": __("March") },
				{ "value": "4", "label": __("April") },
				{ "value": "5", "label": __("May") },
				{ "value": "6", "label": __("June") },
				{ "value": "7", "label": __("July") },
				{ "value": "8", "label": __("August") },
				{ "value": "9", "label": __("September") },
				{ "value": "10", "label": __("October") },
				{ "value": "11", "label": __("November") },
				{ "value": "12", "label": __("December") }
			],
			"default": (new Date().getMonth() + 1).toString(),
		},
		{
			"fieldname": "partner",
			"label": __("Partner"),
			"fieldtype": "Link",
			"options": "Partner",
			"default": frappe.defaults.get_user_default("partner"),
		},
		{
			"fieldname": "state",
			"label": __("State"),
			"fieldtype": "Link",
			"options": "State",
			"get_query": function () {
				return {
					filters: {
						"is_active": 1
					}
				};
			},
			"on_change": function () {
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "district",
			"label": __("District"),
			"fieldtype": "Link",
			"options": "District",
			get_query: function () {
				let state = frappe.query_report.get_filter_value("state")
				return state ? { filters: { state_id: state } } : {};
			},
			"on_change": function () {
				frappe.query_report.set_filter_value("block", "");
				frappe.query_report.set_filter_value("gp", "");
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "block",
			"label": __("Block"),
			"fieldtype": "Link",
			"options": "Block",
			"get_query": function () {
				let district = frappe.query_report.get_filter_value("district");
				return { filters: { district: district || undefined } };
			},
			"on_change": function () {
				frappe.query_report.set_filter_value("gp", "");
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "gp",
			"label": __("Gram Panchayat"),
			"fieldtype": "Link",
			"options": "Gram Panchayat",
			"get_query": function () {
				let block = frappe.query_report.get_filter_value("block");
				return { filters: { block: block || undefined } };
			},
			"on_change": function () {
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "creche",
			"label": __("Creche"),
			"fieldtype": "Link",
			"options": "Creche",
			"get_query": function () {
				let gp = frappe.query_report.get_filter_value("gp");
				return { filters: { gp: gp || undefined } };
			},
			"on_change": function () {
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "supervisor_id",
			"label": __("Supervisor"),
			"fieldtype": "Link",
			"options": "User",
			"get_query": function () {
				let creche = frappe.query_report.get_filter_value("creche");
				return creche ? { filters: { creche: creche } } : {};
			},
		},
		{
			"fieldname": "band",
			"label": __("Band Level"),
			"fieldtype": "Select",
			"options": [
				{ "value": "", "label": __("Attendance (%) Slab") },
				{ "value": "1", "label": __("0%") },
				{ "value": "2", "label": __("> 0 to < 25%") },
				{ "value": "3", "label": __("25 to < 50%") },
				{ "value": "4", "label": __("50 to < 75%") },
				{ "value": "5", "label": __("75 to < 100%") },
				{ "value": "6", "label": __("100%") },
			],
			"default": "",
			"on_change": function () {
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "phases",
			"label": __("Phase"),
			"fieldtype": "MultiSelect",
			"options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
			"reqd": 0,
			"default": ""
		},
		{
			"fieldname": "creche_status_id",
			"label": __("Creche Status"),
			"fieldtype": "Select",
			"options": [
				{ "value": "", "label": __("") },
				{ "value": "1", "label": __("Planned") },
				{ "value": "2", "label": __("Plan dropped") },
				{ "value": "3", "label": __("Active/Operational") },
				{ "value": "4", "label": __("Closed") },
			],
			"default": "3",
		},
		{
			fieldname: "cr_opening_range_type",
			label: __("Creche Opening Date"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "between", label: __("Between") },
				{ value: "before", label: __("Before") },
				{ value: "after", label: __("After") },
				{ value: "equal", label: __("Equal") }
			],
			// default: "",
			on_change: function () {
				const dateRangeType = frappe.query_report.get_filter_value("cr_opening_range_type");

				const isBetween = dateRangeType === "between";
				const isSingleDate = ["before", "after", "equal"].includes(dateRangeType);
				const isCleared = dateRangeType === "";

				frappe.query_report.get_filter("c_opening_range").toggle(isBetween);
				frappe.query_report.get_filter("single_date").toggle(isSingleDate);

				if (isBetween) {
					frappe.query_report.set_filter_value("single_date", "");
				} else if (isSingleDate) {
					frappe.query_report.set_filter_value("c_opening_range", []);
				}

				if (isCleared) {
					frappe.query_report.set_filter_value("c_opening_range", []);
					frappe.query_report.set_filter_value("single_date", "");
				}

				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "c_opening_range",
			label: __("Creche Opening Range"),
			fieldtype: "DateRange",
			hidden: 1
		},
		{
			fieldname: "single_date",
			label: __("Creche Opening Date"),
			fieldtype: "Date",
			hidden: 1
		}
	],


	"formatter": function (value, row, column, data, default_formatter) {
		// Format attendance_percentage with background color
		if (column.fieldname === "attendance_percentage" && data) {
			let percentage = parseFloat(value);
			let bgColor = "white"; // Default
			if (percentage == 0) {
				bgColor = "#FF474D"; // Red
			} else if (percentage < 25) {
				bgColor = "#FF7074"; // Light red
			} else if (percentage < 50) {
				bgColor = "#FFBD54"; // Orange
			} else if (percentage < 75) {
				bgColor = "#FFE762"; // Yellow
			} else if (percentage < 100) {
				bgColor = "#8DFF92"; // Light Green
			} else if (percentage == 100) {
				bgColor = "#54FF5C"; // Green
			}
			return `<div style="background-color: ${bgColor}; color: black; width: 100%; height: 100%; padding: 5px; display: flex; align-items: center; justify-content: center;">${value}</div>`;
		}

		// Format date_of_enrollment as dd-mm-yyyy
		if (column.fieldname === "date_of_enrollment" && value) {
			const d = frappe.datetime.str_to_obj(value);
			return frappe.datetime.obj_to_str(d, "dd-mm-yyyy");
		}

		return default_formatter(value, row, column, data);
	}

};