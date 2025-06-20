// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Enrollment & Attendance"] = {
	"filters": [
        {
            fieldname: "partner",
            label: __("Partner"),
            fieldtype: "Link",
            options: "Partner",
            reqd: 0
        },
        {
            fieldname: "state",
            label: __("State"),
            fieldtype: "Link",
            options: "State",
            reqd: 0
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": ["2023", "2024", "2025"],
            "default": new Date().getFullYear().toString(),
            "on_change": function() {
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": [
                {"value": " ", "label": "All"},
                {"value": "1", "label": "January"},
                {"value": "2", "label": "February"},
                {"value": "3", "label": "March"},
                {"value": "4", "label": "April"},
                {"value": "5", "label": "May"},
                {"value": "6", "label": "June"},
                {"value": "7", "label": "July"},
                {"value": "8", "label": "August"},
                {"value": "9", "label": "September"},
                {"value": "10", "label": "October"},
                {"value": "11", "label": "November"},
                {"value": "12", "label": "December"}
            ],
            "default": (new Date().getMonth() + 1).toString(),
            "on_change": function() {
                frappe.query_report.refresh();
            }
        }
	]
};
