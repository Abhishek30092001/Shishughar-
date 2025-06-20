frappe.query_reports["Growth Monitoring Child wise"] = {
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
			fieldname: "gp",
			label: __("Gram Panchayat"),
			fieldtype: "Link",
			options: "Gram Panchayat",
			get_query: function () {
				let block = frappe.query_report.get_filter_value("block");
				return block ? { filters: { block_id: block } } : {};
			},
			on_change: function () {
				frappe.query_report.set_filter_value("creche", "");
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
			"fieldname": "creche",
			"label": __("Creche"),
			"fieldtype": "Link",
			"options": "Creche",
			"reqd": 0
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
            default: "",
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
		// Check if the red_flag is "Y"
		if (data.red_flag === "Y" && column.fieldname === "child_name") {
			return `<div style="color: red;">${value}</div>`;
		}

		// // Existing red flag formatter
		// if (column.fieldname === "red_flag") {
		//     return value == "Y" ? "&#x1F6A9;" : "-";
		// }

		if (column.fieldname === "red_flag") {
			return value === "Y" ? `
                <svg viewBox="0 0 22 22" width="25" height="25" xmlns="http://www.w3.org/2000/svg">
                    <path d="m5.5917969 3c-.32661 0-.5918369.2563756-.5917969.5722656v15.4277344h1.1816406v-6.236328c2.36349 1.14393 4.4593264.544044 5.9101564-1.191406 1.62853-1.9475804 3.478663-2.5646779 5.908203-3.4296879 0 0-2.362833-2.2350562-5.908203-2.2851562-2.3163701-.03233-4.5980264-.4403063-5.9101564-2.2851563 0-.31589-.2632737-.5722656-.5898437-.5722656z" 
                        fill="#ff6456" stroke="black" stroke-width="1"/>
                </svg>

            ` : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}

		if (column.fieldname === "follow_up") {
			return value == "Y" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}
		if (column.fieldname === "measurements_taken") {
			return value == "Y" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}
		if (column.fieldname === "child_name") {
			return typeof value === "string" ? value : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}

		if (column.fieldname === "vhsnd") {
			return value == "Y" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}

		if (column.fieldname === "nrc") {
			return value == "Y" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}

		if (column.fieldname === "chc") {
			return value == "Y" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}

		if (column.fieldname === "any_medical_major_illness") {
			return value == "1" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}
		if (column.fieldname === "phc") {
			return value == "Y" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}
		if (column.fieldname === "red_flag_HV") {
			return value == "Y" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}
		if (column.fieldname === "othr") {
			return value == "Y" ? "Y" : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}


		if (column.fieldname === "growth_faltering_1") {
			return value === "Y" ? `
                <svg viewBox="0 0 22 22" width="25" height="25" xmlns="http://www.w3.org/2000/svg">
                    <path d="m5.5917969 3c-.32661 0-.5918369.2563756-.5917969.5722656v15.4277344h1.1816406v-6.236328c2.36349 1.14393 4.4593264.544044 5.9101564-1.191406 1.62853-1.9475804 3.478663-2.5646779 5.908203-3.4296879 0 0-2.362833-2.2350562-5.908203-2.2851562-2.3163701-.03233-4.5980264-.4403063-5.9101564-2.2851563 0-.31589-.2632737-.5722656-.5898437-.5722656z" 
                        fill="#ffc44f" stroke="black" stroke-width="1"/>
                </svg>

            ` : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}

		if (column.fieldname === "growth_faltering_2") {
			return value === "Y" ? `
                <svg viewBox="0 0 22 22" width="25" height="25" xmlns="http://www.w3.org/2000/svg">
                    <path d="m5.5917969 3c-.32661 0-.5918369.2563756-.5917969.5722656v15.4277344h1.1816406v-6.236328c2.36349 1.14393 4.4593264.544044 5.9101564-1.191406 1.62853-1.9475804 3.478663-2.5646779 5.908203-3.4296879 0 0-2.362833-2.2350562-5.908203-2.2851562-2.3163701-.03233-4.5980264-.4403063-5.9101564-2.2851563 0-.31589-.2632737-.5722656-.5898437-.5722656z" 
                        fill="#f98327" stroke="black" stroke-width="1"/>
                </svg>
            ` : (!isNaN(value) && value > 0 ? `<b>${value}</b>` : "-");
		}


		if (["weight_for_age_status", "height_for_age_status", "weight_for_height_status"].includes(column.fieldname)) {
			let color = "#b8b7b5"; // Default color

			if (value == "Severe") color = "#FFADB0";
			else if (value == "Moderate") color = "#f6fc82";
			else if (value == "Normal") color = "#D7FD9A";
			else if (value == undefined) return "-";
			return `<div style="background-color: ${color}; color: black; width: 100%; height: 100%; padding: 5px; display: flex; align-items: center; justify-content: center;">${value}</div>`;
		}

		// Default formatter for other fields
		return default_formatter(value, row, column, data);
	}
};
