// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Avg Attendance Summary Test"] = {
	onload: function(report) {
		let actions_container = $(".page-actions");
	
		// 🧹 Clean up existing custom elements (avoid bleed into other reports)
		actions_container.find(".refresh-creche-summary-btn").remove();
		actions_container.find(".last-updated-display").remove();
	
		// ✅ Add the "Last Generated" display box
		let last_updated_container = $('<div class="last-updated-display" style="font-style: italic; margin-right: 15px;"></div>');
		actions_container.prepend(last_updated_container);
	
		// ✅ Create the Refresh Button
		let update_button = $(`
			<button class="btn btn-primary refresh-creche-summary-btn">
				<span class="button-text">${__("Refresh Data")}</span>
				<span class="button-spinner" style="display: none; margin-left: 5px;">
					<i class="fa fa-spinner fa-spin"></i>
				</span>
			</button>
		`).click(function() {
			update_button.prop('disabled', true).addClass('btn-disabled');
			update_button.find('.button-text').text(__("Updating..."));
			update_button.find('.button-spinner').show();
	
			frappe.call({
				method: "frappe.val.test_attd.update_creche_summary",
				callback: function(r) {
					update_button.prop('disabled', false).removeClass('btn-disabled');
					update_button.find('.button-text').text(__("Refresh Data"));
					update_button.find('.button-spinner').hide();
	
					if (r.message) {
						this.update_last_modified_display();
						frappe.msgprint(__("Creche summary updated successfully"));
						report.refresh();
					}
				}.bind(this),
				error: function(err) {
					update_button.prop('disabled', false).removeClass('btn-disabled');
					update_button.find('.button-text').text(__("Refresh Data"));
					update_button.find('.button-spinner').hide();
					frappe.msgprint(__("Error updating creche summary: ") + err);
				}
			});
		}.bind(this));
	
		// ✅ Add both elements to the page-actions container
		actions_container.prepend(update_button);
	
		// 🔁 Load initial last modified info
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
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "district",
			label: __("District"),
			fieldtype: "Link",
			options: "District"
		},
		{
			fieldname: "block",
			label: __("Block"),
			fieldtype: "Link",
			options: "Block"
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