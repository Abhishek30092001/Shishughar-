// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Avg Attendance Summary test report"] = {
    filters: [
        {
            fieldname: "date_input_type",
            label: __("Date Input Type"),
            fieldtype: "Select",
            options: [
                { value: "date_range", label: __("Date Range") },
                { value: "month_year", label: __("Month/Year") }
            ],
            default: "date_range",
            on_change: function () {
                const dateInputType = frappe.query_report.get_filter_value("date_input_type");

                if (dateInputType === "date_range") {
                    // Reset year & month
                    frappe.query_report.set_filter_value("year", "");
                    frappe.query_report.set_filter_value("month", "");
                    frappe.query_report.set_filter_value("time_range", [frappe.datetime.month_start(), frappe.datetime.month_end()]);

                    // Remove month/year filters dynamically
                    frappe.query_report.get_filter("year").toggle(false);
                    frappe.query_report.get_filter("month").toggle(false);
                    frappe.query_report.get_filter("time_range").toggle(true);
                } else if (dateInputType === "month_year") {
                    // Reset date range
                    frappe.query_report.set_filter_value("time_range", "");

                    // Set default year & month
                    frappe.query_report.set_filter_value("year", frappe.datetime.get_today().split('-')[0]);
                    frappe.query_report.set_filter_value("month", frappe.datetime.get_today().split('-')[1]);

                    // Remove date range filter dynamically
                    frappe.query_report.get_filter("time_range").toggle(false);
                    frappe.query_report.get_filter("year").toggle(true);
                    frappe.query_report.get_filter("month").toggle(true);
                }

                // Refresh the report for changes to take effect
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "time_range",
            label: __("Date Range"),
            fieldtype: "DateRange",
            default: [frappe.datetime.month_start(), frappe.datetime.month_end()],
            hidden: 0 // Initially visible
        },
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: ["2024", "2025"],
            default: frappe.datetime.get_today().split('-')[0],
            hidden: 1 // Initially hidden
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { value: "01", label: "January" },
                { value: "02", label: "February" },
                { value: "03", label: "March" },
                { value: "04", label: "April" },
                { value: "05", label: "May" },
                { value: "06", label: "June" },
                { value: "07", label: "July" },
                { value: "08", label: "August" },
                { value: "09", label: "September" },
                { value: "10", label: "October" },
                { value: "11", label: "November" },
                { value: "12", label: "December" }
            ],
            default: frappe.datetime.get_today().split('-')[1],
            hidden: 1 // Initially hidden
        },
        {
            fieldname: "partner",
            label: __("Partner"),
            fieldtype: "Link",
            options: "Partner",
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

