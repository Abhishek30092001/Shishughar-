frappe.query_reports["Average Opening Hours"] = {
    "filters": [
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": ["2023", "2024", "2025", "2026"],
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
            "fieldname": "creche",
            "label": __("Creche"),
            "fieldtype": "Link",
            "options": "Creche"
        },
        {
            "fieldname": "old_new",
            "label": __("Old/New"),
            "fieldtype": "Select",
            "options": [
                {"value": " ", "label": __(" ")},
                {"value": "1", "label": __("Old")},
                {"value": "2", "label": __("New")}
            ],
        },
        {
            "fieldname": "active_inactive",
            "label": __("Active/Inactive"),
            "fieldtype": "Select",
            "options": [
                {"value": " ", "label": __(" ")},
                {"value": "1", "label": __("Active")},
                {"value": "0", "label": __("Inactive")}
            ],
        },
        {
            "fieldname": "hard_to_reach_village",
            "label": __("Hard to Reach Village"),
            "fieldtype": "Select",
            "options": [
                {"value": " ", "label": __(" ")},
                {"value": "1", "label": __("Yes")},
                {"value": "2", "label": __("No")}
            ],
        }
        
        // {
        //     "fieldname": "number_of_days_open",
        //     "label": __("Number of Days Open"),
        //     "fieldtype": "Int"
        // }
    ],

    onload: function() {
        const me = this;

        // Manually trigger a refresh when filters are cleared
        this.filters.forEach(function(filter) {
            filter.on_change = function() {
                // Check if the filter is cleared
                if (!this.get_value()) {
                    frappe.query_report.refresh();
                }
            };
        });
    }
};
