frappe.query_reports["Enrollment Report"] = {
    "filters": [
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": ["2023", "2024", "2025"],
            "default": new Date().getFullYear().toString()
        },

        {
            "fieldname": "partner",
            "label": __("Partner"),
            "fieldtype": "Link",
            "options": "Partner",
            "default": frappe.defaults.get_user_default("partner")
        },
        {
            "fieldname": "state",
            "label": __("State"),
            "fieldtype": "Link",
            "options": "State"
        },
        {
            "fieldname": "district",
            "label": __("District"),
            "fieldtype": "Link",
            "options": "District"
        },
        {
            "fieldname": "block",
            "label": __("Block"),
            "fieldtype": "Link",
            "options": "Block"
        },
        {
            "fieldname": "gp",
            "label": __("Gram Panchayat"),
            "fieldtype": "Link",
            "options": "Gram Panchayat"
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
            "options": "Creche"
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

        // {
        //     "fieldname": "gender",
        //     "label": __("Gender"),
        //     "fieldtype": "Select",
        //     "options": [
        //         { "value": " ", "label": __(" ") },
        //         { "value": "1", "label": __("Male") },
        //         { "value": "2", "label": __("Female") }
        //     ]
        // },
        // {
        //     "fieldname": "age_group",
        //     "label": __("Age Group"),
        //     "fieldtype": "Select",
        //     "options": [
        //         { "value": " ", "label": __(" ") },
        //         { "value": "1", "label": __("0-1 years") },
        //         { "value": "2", "label": __("1-2 years") },
        //         { "value": "3", "label": __("2-3 years") }
        //     ]
        // },
        // {
        //     "fieldname": "is_active",
        //     "label": __("Active/Inactive"),
        //     "fieldtype": "Select",
        //     "options": [
        //         { "value": " ", "label": __(" ") },
        //         { "value": "1", "label": "Active" },
        //         { "value": "0", "label": "Inactive" }
        //     ]
        // },
        // {
        //     "fieldname": "old_creche",
        //     "label": __("Old/New"),
        //     "fieldtype": "Select",
        //     "options": [
        //         { "value": " ", "label": __(" ") },
        //         { "value": "1", "label": "Old" },
        //         { "value": "0", "label": "New" }
        //     ]
        // }

    ],

    // Ensures filters are loaded before binding events
    onload: function () {
        const me = this;
        this.filters.forEach(function (filter) {
            filter.on_change = function () {
                // Check if the filter is cleared
                if (!this.get_value()) {
                    frappe.query_report.refresh();
                }
            };
        });
    },

    get_query: function () {
        const filters = this.get_filters();
        return {
            filters: {
                // Apply filters to the query
                month: filters.month || null,
                year: filters.year || new Date().getFullYear().toString()
            }
        };
    }
};