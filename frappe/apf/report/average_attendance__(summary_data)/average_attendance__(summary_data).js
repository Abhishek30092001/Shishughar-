// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Average Attendance  (Summary Data)"] = {
    onload: function(report) {
        // Find the existing actions container
        let actions_container = $(".page-actions");
        
        // Create the Update Creche Summary button with loading spinner container
        let update_button = $(`
            <button class="btn btn-primary">
                <span class="button-text">${__("Refresh Data")}</span>
                <span class="button-spinner" style="display: none; margin-left: 5px;">
                    <i class="fa fa-spinner fa-spin"></i>
                </span>
            </button>
        `).click(function() {
            // Disable the button and show spinner
            update_button.prop('disabled', true).addClass('btn-disabled');
            update_button.find('.button-text').text(__("Updating..."));
            update_button.find('.button-spinner').show();
            
            frappe.call({
                method: "frappe.val.test_attd.update_creche_summary",
                callback: function(r) {
                    // Enable button and hide spinner
                    update_button.prop('disabled', false).removeClass('btn-disabled');
                    update_button.find('.button-text').text(__("Refresh Data"));
                    update_button.find('.button-spinner').hide();
                    
                    if (r.message) {
                        // Update the last modified display immediately
                        this.update_last_modified_display();
                        frappe.msgprint(__("Creche summary updated successfully"));
                        report.refresh();
                    }
                }.bind(this), // Bind the context to maintain 'this' reference
                error: function(err) {
                    // Enable button and hide spinner
                    update_button.prop('disabled', false).removeClass('btn-disabled');
                    update_button.find('.button-text').text(__("Refresh Data"));
                    update_button.find('.button-spinner').hide();
                    
                    frappe.msgprint(__("Error updating creche summary: ") + err);
                }
            });
        }.bind(this)); // Bind the context to maintain 'this' reference
        
        // Add the button to the actions container
        actions_container.prepend(update_button);
        
        // Create and add the last updated display
        let last_updated_container = $('<div class="last-updated-display" style="font-style: italic; margin-right: 15px;"></div>');
        actions_container.prepend(last_updated_container);
        
        // Load the last updated value
        this.update_last_modified_display();
    },

    update_last_modified_display: function() {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Creche Summary",
                fieldname: "modified",
                order_by: "modified desc",
                limit: 1
            },
            callback: (r) => {
                let display_text = __("Data not available");
                if (!r.exc && r.message && r.message.modified) {
                    display_text = __("Summary generated as on: {0}", [frappe.datetime.str_to_user(r.message.modified)]);
                }
                $(".last-updated-display").html(display_text);
            }
        });
    },

    refresh: function(report) {
        this.update_last_modified_display();
    },
	filters: [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Select",
			options: ["2024", "2025"],
			default: frappe.datetime.get_today().split('-')[0],
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
			options: "Creche"
		},
		{
			fieldname: "level",
			label: __("Level"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "1", label: __("Partner") },
				{ value: "2", label: __("State") },
				{ value: "3", label: __("District") },
				{ value: "4", label: __("Block") },
				{ value: "5", label: __("Supervisor") },
				{ value: "6", label: __("GP") },
				{ value: "7", label: __("Creche") },
			],
			default: "7",
			on_change: function () {
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "band",
			label: __("Attendance (%) Slab"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
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
			fieldname: "phases",
			label: __("Phase"),
			fieldtype: "MultiSelect",
			options: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
			reqd: 0,
			default: ""
		},
		{
			fieldname: "creche_status_id",
			label: __("Creche Status"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "1", label: __("Planned") },
				{ value: "2", label: __("Plan dropped") },
				{ value: "3", label: __("Active/Operational") },
				{ value: "4", label: __("Closed") },
			],
			default: "3",
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