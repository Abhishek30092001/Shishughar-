frappe.query_reports["Daily Creche Attendance Activity"] = {
    filters: [
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: [
                "2024",
                "2025"
            ],
            default: frappe.datetime.get_today().split('-')[0],
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { "value": "01", "label": "January" },
                { "value": "02", "label": "February" },
                { "value": "03", "label": "March" },
                { "value": "04", "label": "April" },
                { "value": "05", "label": "May" },
                { "value": "06", "label": "June" },
                { "value": "07", "label": "July" },
                { "value": "08", "label": "August" },
                { "value": "09", "label": "September" },
                { "value": "10", "label": "October" },
                { "value": "11", "label": "November" },
                { "value": "12", "label": "December" }
            ],
            default: frappe.datetime.get_today().split('-')[1],
        },
        {
            fieldname: "partner",
            label: __("Partner"),
            fieldtype: "Link",
            options: "Partner"
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
            fieldname: "creche",
            label: __("Creche"),
            fieldtype: "Link",
            options: "Creche",
            reqd: 0,
            get_query: function () {
                const partner = frappe.query_report.get_filter_value("partner");
                if (partner) {
                    return {
                        filters: {
                            partner_id: partner
                        }
                    };
                } else {
                    return {};
                }
            },
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

    formatter: function (value, row, column, data, default_formatter) {


        if (value === null || value === undefined) return "";
        value = default_formatter(value, row, column, data);

        if (value === "Not Submitted") {
            return `<b style='color:#ff6456;'>${value}</b>`;
        }

        if (data.creche_name && data.creche_name.includes("Total")) {
            return `<b style='color:black;'>${value}</b>`;
        }

        let day_match = column.fieldname.match(/day_(\d+)/);
        let date_parts = column.label.split("-");
        let day = day_match ? day_match[1] : null;
        let month = date_parts[1];
        let year = date_parts[2];

        if (value === "Closed" && day && month && year) {
            let element_id = `${data.creche_idx}_${day}_${month}_${year}`;

            return `<span 
            id="${element_id}" 
            title=""
            style="cursor: pointer;"
            onmouseover="fetch_reason_on_hover(this, '${data.creche_idx}', '${year}-${month}-${day}')"
            onmouseleave="hide_tooltip()"
        >${value}</span>`;
        }

        return value;
    },
    onload: function () {
        console.log("Report Loaded: Daily Creche Attendance Activity");

        const style = document.createElement("style");
        style.innerHTML = `
            .dt-instance-1 .dt-cell--col-8  {
                display: none !important;
            }
        `;
        document.head.appendChild(style);
    }
}

const reasonMapping = {
    "1": "Local Festival",
    "2": "Public Holiday",
    "3": "Training",
    "4": "Any Other",
    "5": "Weekly Off"
};

window.fetch_reason_on_hover = function (element, creche_id, date_of_attendance) {
    if (!element.getAttribute("data-fetched")) {
        // show_tooltip(element, "Fetching reason...");

        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Child Attendance",
                filters: { creche_id, date_of_attendance },
                fieldname: ["reason_for_closure_id", "reason_other"] // Fetch both fields
            },
            callback: function (response) {
                let reasonId = response.message?.reason_for_closure_id || "No reason provided";
                let otherReason = response.message?.reason_other || "";

                let reason = reasonMapping[reasonId] || "Unknown Reason";

                // If reason is "Any Other", append the other reason
                if (reasonId === "4" && otherReason) {
                    reason = `Any Other - ${otherReason}`;
                }

                element.setAttribute("data-fetched", "true");
                show_tooltip(element, reason);
            },
            error: function () {
                show_tooltip(element, "Failed to fetch reason");
            }
        });
    } else {
        show_tooltip(element, element.getAttribute("data-tooltip") || "No reason provided");
    }
};



function show_tooltip(element, message) {
    let existingTooltip = document.querySelector(".custom-tooltip");
    if (existingTooltip) existingTooltip.remove();

    let tooltip = document.createElement("div");
    tooltip.className = "custom-tooltip";
    tooltip.innerText = message;

    document.body.appendChild(tooltip);

    let rect = element.getBoundingClientRect();
    tooltip.style.position = "absolute";
    tooltip.style.top = `${rect.bottom + window.scrollY + 5}px`;
    tooltip.style.left = `${rect.left + window.scrollX}px`;
    tooltip.style.background = "#333";
    tooltip.style.color = "#fff";
    tooltip.style.padding = "5px 10px";
    tooltip.style.borderRadius = "5px";
    tooltip.style.zIndex = "9999";
    tooltip.style.boxShadow = "0 2px 5px rgba(0,0,0,0.3)";
    tooltip.style.whiteSpace = "nowrap";
    tooltip.style.animation = "fade-in 0.2s ease-in-out";

    element.tooltipElement = tooltip;
    element.setAttribute("data-tooltip", message);
}

window.hide_tooltip = function () {
    let tooltip = document.querySelector(".custom-tooltip");
    if (tooltip) tooltip.remove();
};

