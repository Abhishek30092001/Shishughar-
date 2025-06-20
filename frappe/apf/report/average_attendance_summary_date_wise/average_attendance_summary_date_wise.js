const creche_status_mapping = {
	"Planned": "1",
	"Plan dropped": "2",
	"Active/Operational": "3",
	"Closed": "4"
};
frappe.query_reports["Average Attendance Summary Date Wise"] = {
	filters: [
		// {
		// 	fieldname: "year",
		// 	label: __("Year"),
		// 	fieldtype: "Select",
		// 	options: ["2024", "2025"],
		// 	default: frappe.datetime.get_today().split('-')[0],
		// },
		// {
		// 	fieldname: "month",
		// 	label: __("Month"),
		// 	fieldtype: "Select",
		// 	options: [
		// 		{ value: "01", label: "January" },
		// 		{ value: "02", label: "February" },
		// 		{ value: "03", label: "March" },
		// 		{ value: "04", label: "April" },
		// 		{ value: "05", label: "May" },
		// 		{ value: "06", label: "June" },
		// 		{ value: "07", label: "July" },
		// 		{ value: "08", label: "August" },
		// 		{ value: "09", label: "September" },
		// 		{ value: "10", label: "October" },
		// 		{ value: "11", label: "November" },
		// 		{ value: "12", label: "December" }
		// 	],
		// 	default: frappe.datetime.get_today().split('-')[1],
		// },
		{
			"fieldname": "time_range",
			"label": __("Date"),
			"fieldtype": "DateRange",
			"default": [
				frappe.datetime.month_start(),
				frappe.datetime.month_end()
			]
		},
		{
			fieldname: "partner",
			label: __("Partner"),
			fieldtype: "Link",
			options: "Partner",
		},
		{
			fieldname: "state",
			label: __("State"),
			fieldtype: "Link",
			options: "State",
		},
		{
			fieldname: "district",
			label: __("District"),
			fieldtype: "Link",
			options: "District",
		},
		{
			fieldname: "block",
			label: __("Block"),
			fieldtype: "Link",
			options: "Block",
		},
		{
			fieldname: "gp",
			label: __("Gram Panchayat"),
			fieldtype: "Link",
			options: "Gram Panchayat",
		},
		{
			fieldname: "supervisor_id",
			label: __("Supervisor"),
			fieldtype: "Link",
			options: "User",
			get_query: function () {
				let creche = frappe.query_report.get_filter_value("creche");
				return creche ? { filters: { creche: creche } } : {};
			},
		},
		{
			fieldname: "creche",
			label: __("Creche"),
			fieldtype: "Link",
			options: "Creche",
		},
		{
			fieldname: "level",
			label: __("Level"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("Level") },
				{ value: "1", label: __("Partner") },
				{ value: "2", label: __("State") },
				{ value: "3", label: __("District") },
				{ value: "4", label: __("Block") },
				{ value: "5", label: __("Supervisor") },
				{ value: "6", label: __("GP") },
				{ value: "7", label: __("Creche") },
			],
			default: "",
			on_change: function () {
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "band",
			label: __("Attendance (%) Slab"),
			fieldtype: "Select",
			options: [
				{ value: " ", label: __("Attendance (%) Slab") },
				{ value: "1", label: __("0 to 25") },
				{ value: "2", label: __("26 to 50") },
				{ value: "3", label: __("51 to 75") },
				{ value: "4", label: __("76 to 100") },
			],
			default: "",
			on_change: function () {
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
			fieldname: "creche_status",
			label: __("Creche Status"),
			fieldtype: "Select",
			options: ["", ...Object.keys(creche_status_mapping)], // Show labels
			on_change: function () {
				const selected_text = frappe.query_report.get_filter_value("creche_status");
				const selected_id = creche_status_mapping[selected_text] || "";

				console.log("Selected Label:", selected_text);
				console.log("Mapped ID:", selected_id);

				// Set ID in a hidden field instead of replacing label
				frappe.query_report.set_filter_value("creche_status_id", selected_id);
			}
		},
		{
			fieldname: "creche_status_id",
			fieldtype: "Data",
			hidden: 1
		},
		{
			fieldname: "date_range",
			label: __("Creche Opening Date"),
			fieldtype: "DateRange",
			default: "",
			on_change: function () {
				frappe.query_report.refresh();
			}
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		if (value === undefined || value === null) {
			return "";
		}

		// 2️⃣ Attendance percentage ke liye color-coded background
		if (column.fieldname === "attendance_percentage" && data) {
			let percentage = parseFloat(value);
			let bgColor = "white"; // Default
			if (percentage >= 0 && percentage <= 25) {
				bgColor = "#FFADB0"; // Red
			} else if (percentage > 25 && percentage <= 50) {
				bgColor = "#FDC483"; // Orange
			} else if (percentage > 50 && percentage <= 75) {
				bgColor = "#f6fc82"; // Yellow
			} else if (percentage > 75 && percentage <= 100) {
				bgColor = "#D7FD9A"; // Green
			}
			return `<div style="background-color: ${bgColor}; color: black; width: 100%; height: 100%; padding: 5px; display: flex; align-items: center; justify-content: center; font-weight: bold;">${value}</div>`;
		}

		if (data && data.state && data.state.includes("Total")) {
			return `<b style="color: black;">${value}</b>`;
		}

		return default_formatter(value, row, column, data);
	}
};
