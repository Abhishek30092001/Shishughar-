
frappe.pages["report-card"].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Report Card',
        single_column: true
    });

    frappe.require("https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js");


    let filters = [
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": ["2024", "2025"],
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
                let district = page.fields_dict["district"].get_value();
                if (district) {
                    return {
                        filters: {
                            district_id: district
                        }
                    };
                }
                return {};
            }
        },
        {
            "fieldname": "gp",
            "label": __("Gram Panchayat"),
            "fieldtype": "Link",
            "options": "Gram Panchayat",
            "get_query": function () {
                let block = page.fields_dict["block"].get_value();
                if (block) {
                    return {
                        filters: {
                            block_id: block
                        }
                    };
                }
                return {};
            }
        },
        {
            "fieldname": "supervisor_id",
            "label": __("Supervisor"),
            "fieldtype": "Link",
            "options": "User",
            "get_query": function () {
                let creche = page.fields_dict["creche"].get_value();
                return creche ? { filters: { creche: creche } } : {};
            },
        },
        {
            "fieldname": "creche",
            "label": __("Creche"),
            "fieldtype": "Link",
            "options": "Creche",
            "get_query": function () {
                let gp = page.fields_dict["gp"].get_value();
                if (gp) {
                    return {
                        filters: {
                            gp_id: gp
                        }
                    };
                }
                return {};
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
        }

    ];

    filters.forEach(filter => {
        page.add_field(filter);
    });

    let cr_opening_range_type = page.add_field({
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
        default: ""
    });

    // Create Date Range Filter (Initially Hidden)
    let c_opening_range = page.add_field({
        fieldname: "c_opening_range",
        label: __("Creche Opening Range"),
        fieldtype: "DateRange",
        hidden: 1
    });

    // Create Single Date Filter (Initially Hidden)
    let single_date = page.add_field({
        fieldname: "single_date",
        label: __("Creche Opening Date"),
        fieldtype: "Date",
        hidden: 1
    });

    cr_opening_range_type.$input.on("change", function () {
        let selected_value = cr_opening_range_type.get_value();

        c_opening_range.toggle(selected_value === "between");
        single_date.toggle(["before", "after", "equal"].includes(selected_value));

        if (selected_value === "between") {
            single_date.set_value(null);
        } else if (["before", "after", "equal"].includes(selected_value)) {
            c_opening_range.set_value(null);
        }
    });



    function resetForwardFilters(currentFilter) {
        let currentIndex = filters.findIndex(filter => filter.fieldname === currentFilter);
        if (currentIndex === -1) return;

        for (let i = currentIndex + 1; i < filters.length; i++) {
            if (page.fields_dict[filters[i].fieldname].df.fieldname == "creche_status_id" || page.fields_dict[filters[i].fieldname].df.fieldname == "phases")
                continue;
            page.fields_dict[filters[i].fieldname].set_value("");
        }

    }

    filters.forEach(filter => {
        if ((filter.fieldtype === "Link" || filter.fieldtype === "Select") && filter.fieldname != "year" && filter.fieldname != "month") {
            const input = page.fields_dict[filter.fieldname].input;
            if (input) {
                input.addEventListener("change", () => {
                    resetForwardFilters(filter.fieldname);
                });
            }
        }
    });


    let searchBtn = page.add_button(`<b>Search</b>`, async () => {
        searchBtn.prop('disabled', true);
        let filter_values = {};
        filters.forEach(filter => {
            filter_values[filter.fieldname] = page.fields_dict[filter.fieldname].get_value();
        });
        await renderCards();
        searchBtn.prop('disabled', false);
    });

    let resetBtn = page.add_button(`<b>Reset</b>`, async () => {
        resetBtn.prop('disabled', true);
        location.reload();
        resetBtn.prop('disabled', true);

    });



    searchBtn.css({
        "background-color": "#5979aa",
        "color": "white",
        "border-radius": "8px",
        "padding": "8px 16px",
        "font-weight": "bold"
    });
    resetBtn.css({
        "background-color": "#F0F0F0",
        "color": "black",
        "border-radius": "8px",
        "padding": "8px 16px",
        "font-weight": "bold"
    });
    $(document).ready(function () {
        if ($(window).width() < 450) {
            $(".page-head.flex").css("padding-bottom", "10px");
        }
    });


    page.wrapper.find('.custom-actions').removeClass('hidden-xs hidden-md').css({
        "display": "flex",
        "gap": "8px"
    });
    page.wrapper.find(".menu-btn-group ").removeClass('show"').css({
        "display": "none"
    });



    page.main.append(`
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1.0">
			<title>Creche Report</title>
			<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
			<style>
				/* General Styles */
				
				body {
					margin: 0;
					font-family: 'Arial', sans-serif;
					background-color: #fff;
					color: #333;
				}
		
				/* Filters Section */
				.filters {
					display: flex;
					flex-wrap: wrap;
					gap: 15px;
					padding: 30px 20px;
					background-color: white;
					box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
					border-radius: 10px;
				}
				select {
					width: 160px;
					padding: 8px;
					font-size: 1em;
					border: 1px solid #ddd;
					border-radius: 4px;
					background-color: #fff;
					color: #333;
				}
		
				/* Filter Buttons */
				.filter-buttons {
					display: flex;
					gap: 10px;
				}
                .page-form{
                    border-radius:8px;       
                }
				.modern-btn {
					padding: 0px 20px;
					font-size: 16px;
					border: none;
					border-radius: 5px;
					cursor: pointer;
					transition: all 0.3s ease;
                    min-height: 30px;
				}
				.reset-btn {
					background-color: #5979aa; /* Red */
					color: white;
				}
				.reset-btn:hover {
					background-color: #5072A7; /* Darker Red */
				}
				.search-btn {
					background-color: #4CAF50; /* Green */
					color: white;
				}
				.search-btn:hover {
					background-color: #388E3C; /* Darker Green */
				}
		
				.cards-container {
				display: grid;
				grid-template-columns: repeat(4, 1fr); /* 4 cards in a row for large screens */
				gap: 20px;
				margin-top: 20px;
				margin-bottom: 20px;
			}
		
			@media (max-width: 1024px) {
				.cards-container {
					grid-template-columns: repeat(4, 1fr); /* 3 cards in a row for medium screens */
				}
			}
		
			@media (max-width: 768px) {
				.cards-container {
					grid-template-columns: repeat(1, 1fr); /* 1 card in a row for small screens */
				}
			}
		
			.card {
				background-color: #fff;
				padding:5px 20px;
				border-radius: 12px;
				box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
				text-align: left;
				transition: transform 0.3s ease-in-out, box-shadow 0.3s ease;
			}
		
			.card:hover {
				transform: translateY(-5px);
				box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
			}
		
			.card h3 {
				font-size: 1.2em;
				color: #333;
				margin-bottom: 10px;
			}
		
			.card p {
				font-size: 2em;
				font-weight: bold;
				color: #000;
			}
		
			.card span {
				font-size: 0.9em;
				color: #666;
			}
		
			}
			.spinner-container {
			  margin:auto !important;
			  display: flex;
			  justify-content: center;
			  align-items: center;
			  height: 100vh;
			  width: 100%;
			}
			
			
			.loader {
			  margin:auto;
			  width: 48px;
			  height: 48px;
			  border-radius: 50%;
			  display: inline-block;
			  position: relative;
			  border: 3px solid;
			  border-color: #FFF #FFF transparent transparent;
			  box-sizing: border-box;
			  animation: rotation 1s linear infinite;
			}
			
			.loader::after,
			.loader::before {
			  content: '';  
			  box-sizing: border-box;
			  position: absolute;
			  left: 0;
			  right: 0;
			  top: 0;
			  bottom: 0;
			  margin: auto;
			  border: 3px solid;
			  border-color: transparent transparent #FF3D00 #FF3D00;
			  width: 40px;
			  height: 40px;
			  border-radius: 50%;
			  animation: rotationBack 0.5s linear infinite;
			  transform-origin: center center;
			}
			
			.loader::before {
			  width: 32px;
			  height: 32px;
			  border-color: #FFF #FFF transparent transparent;
			  animation: rotation 1.5s linear infinite;
			}
			
			@keyframes rotation {
			  0% {
				transform: rotate(0deg);
			  }
			  100% {
				transform: rotate(360deg);
			  }
			}
			
			@keyframes rotationBack {
			  0% {
				transform: rotate(0deg);
			  }
			  100% {
				transform: rotate(-360deg);
			  }
			}
			.total-creche-card{
			   display: grid;
				grid-template-columns: repeat(4, 1fr);
				margin-top:20px;
                gap: 20px;
			}
			 @media (max-width: 768px) {
				.total-creche-card {
					grid-template-columns: repeat(1, 1fr);
				}
			}
			.filter-desc{
			margin-top:20px;
			}
            /* Modal Styles */
            #dataModal {
                display: none;
                position: fixed;
                z-index: 999;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0, 0, 0, 0.4);
            }

            #dataModal {
                display: none;
                position: fixed;
                z-index: 9999;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(3px);
            }

            /* Disable background scroll when modal is open */
            body.modal-open {
                overflow: hidden;
            }

            /* Modal Box */
            .modal-content {
                background-color: #fff;
                margin: 5% auto;
                padding: 20px;
                border-radius: 12px;
                width: 90%;
                max-width: 95vw;
                max-height: 95vh;
                overflow: hidden;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                position: relative;
                animation: slideDown 0.3s ease;
            }

            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Table Wrapper with Scroll */
            #modalTableContainer {
                max-height: 400px;
                overflow-y: auto;
                margin-top: 20px;
                border-radius: 8px;
                border: 1px solid #ddd;
            }

            /* Table Styles */
            #modalTableContainer table {
                width: 100%;
                border-collapse: collapse;
                table-layout: auto;
                border: 1px solid #ccc;
            }
            /* Sticky Table Header */
            #modalTableContainer thead th {
                white-space: nowrap;  
                text-align: center;  
                width: 1%;
                position: sticky;
                top: 0;
                background-color: #5979aa;
                color: white;
                z-index: 1;
            }
            #modalTableContainer::-webkit-scrollbar {
                width: 3px;             /* Thinner scrollbar */
                height: 3px;            /* Optional: thin horizontal scrollbar */
            }

            #modalTableContainer::-webkit-scrollbar-thumb {
                background-color: rgba(0, 0, 0, 0.3);  /* Scroll thumb color */
                border-radius: 4px;
            }

            #modalTableContainer::-webkit-scrollbar-track {
                background-color: transparent;        /* Track stays invisible */
            }
            /* Cell Styles */
            #modalTableContainer th,
            #modalTableContainer td {
                padding: 12px;
                text-align: center;
                border-bottom: 1px solid #eee;
                white-space: nowrap;
                border: 1px solid #ccc; 
            }
            /* CSS */
            .close-btn {
            width: 36px;
            height: 36px;
            padding: 0;
            background: rgba(0, 0, 0, 0.05);
            border: none;
            border-radius:5%;
            font-size: 24px;
            color: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.2s, transform 0.2s;
            }

            .close-btn:hover {
            background: #ffe5e9;;
            transform: rotate(90deg);
            }

            .close-btn:active {
            background: rgba(0, 0, 0, 0.15);
            transform: scale(0.9);
            }

            /* Responsive Table Text */
            @media (max-width: 768px) {
                .modal-content {
                    width: 95%;
                    padding: 15px;
                }

                #modalTableContainer th,
                #modalTableContainer td {
                    padding: 10px 6px;
                    font-size: 14px;
                }
            }
            .skeleton-table {
                width: 100%;
                border-collapse: collapse;
            }

            .skeleton-table th,
            .skeleton-table td {
                padding: 8px;
                border: 1px solid #ddd;
            }

            .skeleton-box {
                height: 16px;
                background: linear-gradient(90deg, #e0e0e0 25%, #f5f5f5 50%, #e0e0e0 75%);
                background-size: 200% 100%;
                animation: shimmer 1.2s infinite;
                border-radius: 4px;
            }

            @keyframes shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }
            /* desktop: hide the “mobile” search, show the header one */
            .search-mobile { display: none; }
            .search-desktop { display: block; }

            @media (max-width: 600px) {
                /* mobile: hide the header search, show the one below */
                .search-desktop { display: none; }
                .search-mobile { display: block; }
            }

			</style>
		</head>
		<body>
		
			<!-- Main Content -->
			<div style="display: flex; flex-direction: column;">
				<!--filter-desc-->
				<div class="filter-desc"></div>
				<div class="spinner-container" style="margin: auto;">
					<span class="loader"></span>
				</div>
				<div class="total-creche-card"></div>
		
				<!-- Card Section -->
				<div class="cards-container"></div>
		
			</div>
           <!-- Modal -->
            <div id="dataModal">
                <div class="modal-content" style="position: relative; padding-top: 30px;">

                    <div id="modalHeaderWrapper" style="
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                        align-items: center;
                        margin-bottom: 10px;
                    ">
                        <h2 style="flex: 1; min-width: 200px; margin: 0;">Current active children</h2>

                        <div class="search-desktop" class="" style="position: relative; flex: 1; min-width: 250px;">
                            <input id="modalSearchInput" type="text" placeholder="Search by Creche or Child Name..." 
                                style="width: 100%; outline: none; padding: 6px 32px 8px 10px; border: 1px solid #ccc; border-radius: 4px;">
                            <!-- 🔍 Icon -->
                            <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #888;">🔍</span>
                        </div>

                    <!-- Download Data Button -->
                    <button id="downloadDataBtn" style="padding: 6px 12px; background-color: #5979aa; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Download Data
                    </button>

                    <button class="close-btn" aria-label="Close">&times;</button>
                    </div>
                    <div class="search-mobile" style="position: relative; flex: 1; min-width: 250px;">
                            <input id="modalSearchInput" type="text" placeholder="Search by Creche or Child Name..." 
                                style="width: 100%; padding: 6px 32px 8px 10px; border: 1px solid #ccc; border-radius: 4px;">
                            <!-- 🔍 Icon -->
                            <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #888;">🔍</span>
                        </div>
                    <div id="modalTableContainer"></div>
                </div>
            </div>

		</body>
		</html>
		`);

    const BASE_URL = "https://shishughar.in";

    function formatResponses(responses) {
        const formattedResponse = [];
        const mergedData = {};

        responses.forEach((response) => {
            const data = response.data;
            Object.keys(data).forEach((colKey) => {
                if (!mergedData[colKey]) {
                    mergedData[colKey] = [];
                }
                mergedData[colKey] = mergedData[colKey].concat(data[colKey]);
            });
        });

        Object.keys(mergedData).forEach((colKey) => {
            formattedResponse.push({
                data: {
                    [colKey]: mergedData[colKey]
                }
            });
        });

        return formattedResponse;
    }

    async function fetchDashboardData() {

        const baseUrl = `${BASE_URL}/api/method/frappe.val.test_api`;

        const apiParams = {
            partner_id: null,
            state_id: null,
            district_id: null,
            gp_id: null,
            block_id: null,
            supervisor_id: null,
            creche_id: null,
            year: null,
            month: null,
            cstart_date: null,
            cend_date: null,
            c_status: null,
            phases: null
        };


        const filterToApiKeyMap = {
            partner: "partner_id",
            state: "state_id",
            district: "district_id",
            gp: "gp_id",
            block: "block_id",
            supervisor_id: "supervisor_id",
            creche: "creche_id",
            year: "year",
            month: "month",
            creche_status_id: "c_status",
            phases: "phases"

        };

        Object.entries(filterToApiKeyMap).forEach(([fieldname, apiKey]) => {
            const field = page.fields_dict[fieldname];
            if (field) {
                apiParams[apiKey] = field.get_value();
            }
        });

        const rangeType = page.fields_dict["cr_opening_range_type"].get_value();
        const singleDate = page.fields_dict["single_date"].get_value();
        const dateRange = page.fields_dict["c_opening_range"].get_value();

        if (rangeType) {
            if (rangeType === "between" && dateRange && dateRange.length === 2) {
                apiParams.cstart_date = dateRange[0];
                apiParams.cend_date = dateRange[1];

            } else if (rangeType === "before" && singleDate) {
                apiParams.cstart_date = "2017-01-01";
                apiParams.cend_date = singleDate;

            } else if (rangeType === "after" && singleDate) {
                apiParams.cstart_date = singleDate;
                apiParams.cend_date = new Date().toISOString().split("T")[0];

            } else if (rangeType === "equal" && singleDate) {
                apiParams.cstart_date = singleDate;
                apiParams.cend_date = singleDate;
            }
        }

        const constructApiUrl = (section) => {
            const apiUrl = new URL(`${baseUrl}.${section}`);
            Object.entries(apiParams).forEach(([key, value]) => {
                if (value) {
                    apiUrl.searchParams.append(key, value);
                }
            });
            return apiUrl.toString();
        };
        try {
            const apiSections = [
                "dashboard_section_one",
                "dashboard_section_one2",
                "dashboard_section_two",
                "dashboard_section_three",
                "dashboard_section_four"
            ];

            const apiEndpoints = apiSections.map(section => constructApiUrl(section));
            const responses = await Promise.all(
                apiEndpoints.map(url =>
                    fetch(url, {
                        method: "GET",
                        credentials: "same-origin",
                    }).then(response => response.json())
                )
            );
            const formattedResponseData = formatResponses(responses);
            const mergedData = {
                data: {
                    Col0: [],
                    Col1: [],
                    Col2: [],
                    Col3: [],
                    Col4: []
                }
            };
            mergedData.data['Col0'] = responses[0].data.Col0;
            formattedResponseData.forEach((response, index) => {
                const colKey = `Col${index}`;
                if (colKey === 'Col0') {
                    return;
                }
                if (response.data && response.data[colKey]) {
                    mergedData.data[colKey] = response.data[colKey];
                }
            });
            return mergedData.data;

        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    }


    function formatNumber(number) {
        return new Intl.NumberFormat("en-IN").format(number);
    }


    function openModalWithTable(columns, data, title, cardId) {
        const modal = document.getElementById("dataModal");
        const container = document.getElementById("modalTableContainer");
        const titleElement = modal.querySelector("h2");
        const searchInput = document.getElementById("modalSearchInput");
        const closeBtn = modal.querySelector(".close-btn");

        // Store the current data and columns in the modal element for later use
        modal.currentData = { columns, data, title };

        titleElement.textContent = title;
        document.body.classList.add("modal-open");
        modal.style.display = "block";


        // Only show download button for specified card types
        const downloadableCards = [
            "curactchi-9abe", "chienrthimon-c6c5", "curelichi-99bf",
            "chiexithimon-ce95", "modund-2ce9", "modwas-6828",
            "modstu-3599", "grofal-02c8", "sevund-55ab",
            "sevwas-ffdb", "sevstu-3cf6", "grofal-975f",
            "cresubatt-611c"
        ];

        if (downloadableCards.includes(cardId)) {
            modal.querySelector(".modal-content").insertBefore(downloadBtn, container);
        }

        // Rest of your existing openModalWithTable code...
        container.innerHTML = "";
        container.appendChild(createSkeletonTable(columns.length + 1, 10));

        setTimeout(() => {
            container.innerHTML = "";

            // Build table skeleton
            const table = document.createElement("table");
            table.className = "data-table";
            const thead = table.createTHead();
            const headerRow = thead.insertRow();

            // Add S.No. column
            const serialTh = document.createElement("th");
            serialTh.textContent = "S.No.";
            headerRow.appendChild(serialTh);

            columns.forEach(col => {
                const th = document.createElement("th");
                th.textContent = col;
                headerRow.appendChild(th);
            });

            const tbody = table.createTBody();
            container.appendChild(table);

            const batchSize = 500;
            let currentRenderId = 0;

            function renderTableRows(dataset) {
                const renderId = ++currentRenderId;
                tbody.innerHTML = "";

                let rowIndex = 0;
                function renderChunk() {
                    if (renderId !== currentRenderId) return;

                    const end = Math.min(rowIndex + batchSize, dataset.length);
                    for (; rowIndex < end; rowIndex++) {
                        const tr = tbody.insertRow();

                        // Add serial number cell
                        const serialCell = tr.insertCell();
                        serialCell.textContent = rowIndex + 1;

                        dataset[rowIndex].forEach(cell => {
                            const td = tr.insertCell();
                            td.textContent = cell;
                            td.style.textAlign = "left";
                        });
                    }

                    if (rowIndex < dataset.length) {
                        setTimeout(renderChunk, 0);
                    }
                }

                renderChunk();
            }

            let filteredData = [...data];
            renderTableRows(filteredData);

            searchInput.addEventListener("input", function () {
                const q = this.value.toLowerCase();
                filteredData = data.filter(row =>
                    row.some(cell =>
                        typeof cell === "string" && cell.toLowerCase().includes(q)
                    )
                );
                renderTableRows(filteredData);
            });
        }, 300);
    }

    // Modify the download button click handler to use stored data
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "downloadDataBtn") {
            const modal = document.getElementById("dataModal");
            if (modal.currentData) {
                const { columns, data, title } = modal.currentData;
                exportToExcel(["S.No.", ...columns],
                    data.map((row, index) => [index + 1, ...row]),
                    title);
            } else {
                alert("No data available to download");
            }
        }
    });

    // Keep your existing exportToExcel function
    function exportToExcel(columns, data, title) {
        const wb = XLSX.utils.book_new();
        const excelData = [columns, ...data];
        const ws = XLSX.utils.aoa_to_sheet(excelData);
        XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
        XLSX.writeFile(wb, `${title.replace(/ /g, '_')}.xlsx`);
    }


    function createSkeletonTable(colCount, rowCount) {
        const table = document.createElement("table");
        table.className = "skeleton-table";

        const thead = table.createTHead();
        const headerRow = thead.insertRow();
        for (let i = 0; i < colCount; i++) {
            const th = document.createElement("th");
            th.innerHTML = `<div class="skeleton-box"></div>`;
            headerRow.appendChild(th);
        }

        const tbody = table.createTBody();
        for (let i = 0; i < rowCount; i++) {
            const tr = tbody.insertRow();
            for (let j = 0; j < colCount; j++) {
                const td = tr.insertCell();
                td.innerHTML = `<div class="skeleton-box"></div>`;
            }
        }

        return table;
    }


    // Close modal function
    function closeModal() {
        const searchInput = document.getElementById("modalSearchInput");
        searchInput.value = ""
        document.getElementById("dataModal").style.display = "none";
        document.body.classList.remove("modal-open");
    }

    document.querySelector(".close-btn").addEventListener("click", closeModal);

    window.addEventListener("click", (event) => {
        if (event.target === document.getElementById("dataModal")) {
            closeModal();
        }
    });
    const cardIdToQueryTypeMap = {
        "curactchi-9abe": "active_children",
        "cresubatt-611c": "no_creche_attendance_submitted",
        "curelichi-99bf": "current_eligible_children",
        "chienrthimon-c6c5": "enrolled_children_this_month",
        "chiexithimon-ce95": "exited_children_this_month",
        "modund-2ce9": "moderately_underweight",
        "modwas-6828": "moderately_wasted",
        "modstu-3599": "moderately_stunted",
        "grofal-02c8": "gf1",
        "sevund-55ab": "severly_underweight",
        "sevwas-ffdb": "severly_wasted",
        "sevstu-3cf6": "severly_stunted",
        "grofal-975f": "gf2",
        "antdatsub-4b97": "anthro_data_submitted",
        "cre-983d": "no_of_creches",
        "chimestak-bffa": "measurement_data_submitted",
    };
    async function handleCardClick(cardId, item, cardElement) {
        const spinner = cardElement.querySelector('.spinner-container');
        spinner.style.display = 'flex';
        const queryType = cardIdToQueryTypeMap[cardId];
        const year = page.fields_dict["year"].get_value() || 2024;
        const month = page.fields_dict["month"].get_value() || 10;
        const partner = page.fields_dict["partner"].get_value();
        const state = page.fields_dict["state"].get_value();
        const district = page.fields_dict["district"].get_value();
        const block = page.fields_dict["block"].get_value();
        const gp = page.fields_dict["gp"].get_value();
        const supervisor_id = page.fields_dict["supervisor_id"].get_value();
        const creche = page.fields_dict["creche"].get_value();
        const phases = page.fields_dict["phases"].get_value();
        const creche_status_id = page.fields_dict["creche_status_id"].get_value();
        const rangeType = page.fields_dict["cr_opening_range_type"].get_value();
        const singleDate = page.fields_dict["single_date"].get_value();
        const dateRange = page.fields_dict["c_opening_range"].get_value();

        let cstart_date = null;
        let cend_date = null;

        if (rangeType) {
            if (rangeType === "between" && dateRange && dateRange.length === 2) {
                cstart_date = dateRange[0];
                cend_date = dateRange[1];
            } else if (rangeType === "before" && singleDate) {
                cstart_date = "2017-01-01";
                cend_date = singleDate;
            } else if (rangeType === "after" && singleDate) {
                cstart_date = singleDate;
                cend_date = new Date().toISOString().split("T")[0];
            } else if (rangeType === "equal" && singleDate) {
                cstart_date = singleDate;
                cend_date = singleDate;
            }
        }

        const rawParams = {
            year,
            month,
            query_type: queryType,
            partner_id: partner,
            state_id: state,
            district_id: district,
            block_id: block,
            gp_id: gp,
            supervisor_id,
            creche_id: creche,
            phases,
            c_status: creche_status_id,
            cstart_date,
            cend_date
        };

        const params = new URLSearchParams();
        for (const key in rawParams) {
            if (rawParams[key] !== null && rawParams[key] !== undefined && rawParams[key] !== "") {
                params.append(key, rawParams[key]);
            }
        }


        const apiUrl = `${BASE_URL}/api/method/frappe.val.web_report_card_detail.fetch_card_data?${params.toString()}`;
        const title = item.title;
        try {

            const res = await fetch(apiUrl);
            const result = await res.json();

            if (result && result.data && result.data.length > 0) {
                const columns = Object.keys(result.data[0]);
                const rows = result.data.map(entry => columns.map(key => entry[key]));
                openModalWithTable(columns, rows, title);
            } else {
                openModalWithTable([""], [["No record found"]], title);
            }
        } catch (err) {
            console.error("Error fetching card data:", err);
            openModalWithTable([""], [["Error fetching data"]], title);
        }
        finally {
            spinner.style.display = 'none';
        }
    }

    async function renderCards() {
        const container = document.querySelector('.cards-container');
        const totalCreche = document.querySelector('.total-creche-card');
        const spinnerContainer = document.querySelector(".spinner-container");
        spinnerContainer.style.display = "flex";
        totalCreche.innerHTML = ""
        container.innerHTML = ""
        const data = await fetchDashboardData();
        console.log(data, "shvjk")
        totalCreche.innerHTML = ""
        const current_active_children = data.Col0.find(item => item.id === "curactchi-9abe").value;
        const current_eligible_children = data.Col2.find(item => item.id === "curelichi-99bf").value;
        const cumulative_enrolled_children = data.Col2.find(item => item.id === "cumenrchi-845b").value;
        const cumulative_exit_children = data.Col2.find(item => item.id === "cumexichi-3df2").value;
        const current_exit_children = data.Col2.find(item => item.id === "chiexithimon-ce95").value;
        const mod_underweight_children = data.Col3.find(item => item.id === "modund-2ce9").value;
        const measurement_data_submitted = data.Col0.find(item => item.id === "chimestak-bffa")?.value || 0;
        const mod_wasted_children = data.Col3.find(item => item.id === "modwas-6828").value;
        const mod_stunted_children = data.Col3.find(item => item.id === "modstu-3599").value;
        const gf1_children = data.Col3.find(item => item.id === "grofal-02c8").value;

        const severly_underweight = data.Col4.find(item => item.id === "sevund-55ab").value;
        const severly_wasted = data.Col4.find(item => item.id === "sevwas-ffdb").value;
        const severly_stunted = data.Col4.find(item => item.id === "sevstu-3cf6").value;
        const gf2_children = data.Col4.find(item => item.id === "grofal-975f").value;


        const columnColors = {
            Col1: '#cfe5fc', // Light blue
            Col2: '#ebfced ', // Light green
            Col3: '#fce9cf', // Light orange
            Col4: '#fcd9d9'  // Light red
        };

        Object.keys(data).filter(colKey => colKey !== 'Col0').forEach((colKey) => {
            const column = document.createElement('div');
            column.style.flex = '1';
            column.style.display = 'flex';
            column.style.flexDirection = 'column';
            column.style.gap = '20px';

            data[colKey].forEach(item => {
                const card = document.createElement('div');
                card.classList.add('card');
                card.style.padding = '20px';
                card.style.minHeight = '150px';
                card.style.border = '1px solid #ccc';
                card.style.borderRadius = '8px';
                card.style.backgroundColor = columnColors[colKey];
                card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
                card.style.textAlign = 'center';
                card.style.position = 'relative';

                const cardId = item.id;

                let extraLine = '';
                if (item.id === "curactchi-9abe") {
                    const percentage = ((current_active_children / current_eligible_children) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of current eligible children)</div>`;
                } else if (item.id === "chimestak-c533") {
                    const percentage = (measurement_data_submitted / current_active_children) * 100;
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)}% of active children)</div>`;
                } else if (item.id === "cumexichi-3df2") {
                    const percentage = ((cumulative_exit_children / cumulative_enrolled_children) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of cumulative enrolled children)</div>`;
                } else if (item.id === "chiexithimon-ce95") {
                    const percentage = ((current_exit_children / current_active_children) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of current active children)</div>`;
                }
                // for gmd
                else if (item.id === "modund-2ce9") {
                    const percentage = ((mod_underweight_children / measurement_data_submitted) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of measurement data submitted)</div>`;
                }
                else if (item.id === "modwas-6828") {
                    const percentage = ((mod_wasted_children / measurement_data_submitted) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of measurement data submitted)</div>`;
                }
                else if (item.id === "modstu-3599") {
                    const percentage = ((mod_stunted_children / measurement_data_submitted) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of measurement data submitted)</div>`;
                }
                else if (item.id === "grofal-02c8") {
                    const percentage = ((gf1_children / measurement_data_submitted) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of measurement data submitted)</div>`;
                }

                else if (item.id === "sevund-55ab") {
                    const percentage = ((severly_underweight / measurement_data_submitted) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of measurement data submitted)</div>`;
                }
                else if (item.id === "sevwas-ffdb") {
                    const percentage = ((severly_wasted / measurement_data_submitted) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of measurement data submitted)</div>`;
                }
                else if (item.id === "sevstu-3cf6") {
                    const percentage = ((severly_stunted / measurement_data_submitted) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of measurement data submitted)</div>`;
                }
                else if (item.id === "grofal-975f") {
                    const percentage = ((gf2_children / measurement_data_submitted) * 100);
                    extraLine = `<div style="font-size: 10px; color: #000; font-style:italic; font-weight:600;">(${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of measurement data submitted)</div>`;
                }
                card.innerHTML = `
                    <div style="font-size: 36px; font-weight: bold; color: #333;">${formatNumber(item.value)}</div>
                    <div style="font-size: 18px; color: #666;">${item.title}</div>
                ${extraLine}
                `;

                const spinner = document.createElement('div');
                spinner.classList.add('spinner-container');
                spinner.style.position = 'absolute';
                spinner.style.top = '0';
                spinner.style.left = '0';
                spinner.style.right = '0';
                spinner.style.bottom = '0';
                spinner.style.background = 'rgba(255, 255, 255, 0.6)';
                spinner.style.zIndex = '1';
                spinner.style.display = 'none'; // hide initially

                const loader = document.createElement('span');
                loader.classList.add('loader');
                spinner.appendChild(loader);
                card.appendChild(spinner);

                if (cardIdToQueryTypeMap[cardId] && item.value) {
                    card.style.cursor = "pointer";
                    card.addEventListener("click", () => handleCardClick(cardId, item, card));
                }
                column.appendChild(card);
            });

            container.appendChild(column);
            spinnerContainer.style.display = "none";
        });

        data.Col0.forEach(item => {
            const cardId = item.id
            let extraLine = ""
            const card = document.createElement('div');
            card.classList.add('card');
            card.style.padding = '20px';
            card.style.height = '150px';
            card.style.border = '1px solid #ccc';
            card.style.borderRadius = '8px';
            card.style.backgroundColor = '#E8E8E8';
            card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            card.style.textAlign = 'center';
            if (item.title === "Current active children") {
                const percentage = ((current_active_children / current_eligible_children) * 100);
                extraLine = `<div style = "font-size: 10px; color: #000; font-style:italic; font-weight:600;" > (${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of current eligible children)</div> `;
            }
            card.innerHTML = `
                    <div style = "font-size: 36px; font-weight: bold; color: #333;" > ${formatNumber(item.value)}</div>
            <div style="font-size: 18px; color: #666;">${item.title}</div>${extraLine}
				`;

            if (item.title === "Children mesurement taken") {
                const percentage = ((measurement_data_submitted / current_active_children) * 100);
                extraLine = `<div style = "font-size: 10px; color: #000; font-style:italic; font-weight:600;" > (${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of active children)</div> `;
            }
            card.innerHTML = `
                    <div style = "font-size: 36px; font-weight: bold; color: #333;" > ${formatNumber(item.value)}</div>
            <div style="font-size: 18px; color: #666;">${item.title}</div>${extraLine}
                `;

            const spinner = document.createElement('div');
            spinner.classList.add('spinner-container');
            spinner.style.position = 'absolute';
            spinner.style.top = '0';
            spinner.style.left = '0';
            spinner.style.right = '0';
            spinner.style.bottom = '0';
            spinner.style.background = 'rgba(255, 255, 255, 0.6)';
            spinner.style.zIndex = '1';
            spinner.style.display = 'none'; // hide initially

            const loader = document.createElement('span');
            loader.classList.add('loader');
            spinner.appendChild(loader);
            card.appendChild(spinner);
            if (cardIdToQueryTypeMap[cardId] && item.value) {
                card.style.cursor = "pointer";
                card.addEventListener("click", () => handleCardClick(cardId, item, card));
            }
            totalCreche.appendChild(card);
        })
    }

    frappe.after_ajax(() => {
        renderCards();
    });

};