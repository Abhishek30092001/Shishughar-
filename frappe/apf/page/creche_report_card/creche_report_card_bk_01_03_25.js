frappe.pages['creche_report_card'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Creche Report Card',
		single_column: true
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
		
				.modern-btn {
					padding: 0px 20px;
					font-size: 16px;
					border: none;
					border-radius: 5px;
					cursor: pointer;
					transition: all 0.3s ease;
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
			}
			 @media (max-width: 768px) {
				.total-creche-card {
					grid-template-columns: repeat(1, 1fr);
				}
			}
			.filter-desc{
			margin-top:20px;
			}
			</style>
		</head>
		<body>
		
			<!-- Main Content -->
			<div style="display: flex; flex-direction: column;">
				
				<!-- Filters Section -->
				<div class="filters">
					<select id="partnerSelect">
						<option value="">Partner</option>
					</select>
					<select id="stateDropdown">
						<option value="">State</option>
					</select>
					<select id="districtDropdown">
						<option value="">District</option>
					</select>
					<select id="blockDropdown">
						<option value="">Block</option>
					</select>
					<select id="gpDropdown">
						<option value="">GP</option>
					</select>
					<select id="crecheDropdown">
						<option value="">Creche</option>
					</select>
					<select id=yearDropdown>
						<option value="">Year</option>
					</select>
					<select id="monthDropdown">
						<option value="">Month</option>
					</select>
				
					<!-- Modern Buttons -->
					<div class="filter-buttons">
						<button id="searchButton" class="modern-btn search-btn">Search</button>
						<button id="resetButton" type="button" class="modern-btn reset-btn" onclick="location.reload()">Reset</button>
					</div>
				</div>
				<!--filter-desc-->
				<div class="filter-desc"></div>
				<div class="spinner-container" style="margin: auto;">
					<span class="loader"></span>
				</div>
				<div class="total-creche-card"></div>
		
				<!-- Card Section -->
				<div class="cards-container"></div>
		
			</div>
		
		</body>
		</html>
		`);

    const BASE_URL = "https://shishughar.in";
    let selectedPartnerId;
    let stateId;
    let district_id;
    let block_id;
    let gp_id;
    let creche_id;
    let year = "";
    let month = "";
    [year, month] = [new Date().getFullYear(), new Date().getMonth() + 1];
    let DashboardData;
    async function fetchPartnerData() {
        try {
            const response = await fetch(`${BASE_URL}/api/method/partner_list`, {
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            const partnerList = data.data;

            const partnerSelect = document.getElementById("partnerSelect");

            partnerList.forEach((partner) => {
                const option = document.createElement("option");
                option.value = partner.partner_id;
                option.textContent = partner.partner_name;
                partnerSelect.appendChild(option);
            });

            const totalPartnerElement = document.getElementById("total_partner");
            totalPartnerElement.textContent = `${partnerList.length}`;
        } catch (error) {
            console.error("Error fetching partner data:", error);
            document.getElementById("total_partner").textContent =
                "Failed to load data.";
        }
    }
    // fetchPartnerData();
    async function fetchStatesData() {
        try {
            const stateDropdown = document.getElementById("stateDropdown");

            if (!stateDropdown) {
                console.error("State dropdown not found!");
                return;
            }

            const response = await fetch(`${BASE_URL}/api/method/get_states_dropdown`, {
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            const stateList = data.data;

            stateDropdown.innerHTML = '<option value="">State</option>';

            if (!stateList || stateList.length === 0) {
                const noDataOption = document.createElement("option");
                noDataOption.value = "";
                noDataOption.textContent = "No states available";
                stateDropdown.appendChild(noDataOption);
                return;
            }

            stateList.forEach((state) => {
                const option = document.createElement("option");
                option.value = state.state_id;
                option.textContent = state.state_name;
                stateDropdown.appendChild(option);
            });

        } catch (error) {
            console.error("Error fetching states data:", error);
            const stateDropdown = document.getElementById("stateDropdown");
            stateDropdown.innerHTML = '<option value="">Error loading states</option>';
        }
    }

    // fetchStatesData();
    async function populateDistrictDropdown(stateId) {
        const response = await fetch(
            `${BASE_URL}/api/method/get_district_dropdown?state_id=${stateId}`
        );
        const data = await response.json();
        const dropdown = document.getElementById("districtDropdown");

        dropdown.innerHTML = '<option value="">District</option>';
        data.data.forEach((district) => {
            const option = document.createElement("option");
            option.value = district.district_id;
            option.textContent = district.district_name;
            dropdown.appendChild(option);
        });
    }
    async function populateBlockDropdown(districtId) {
        try {
            const response = await fetch(
                `${BASE_URL}/api/method/get_block_dropdown?district_id=${districtId}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );

            const result = await response.json();

            if (result.data.length > 0) {
                const dropdown = document.getElementById("blockDropdown");
                dropdown.innerHTML = '<option value="">Block</option>';
                result.data.forEach((block) => {
                    const option = document.createElement("option");
                    option.value = block.block_id;
                    option.textContent = block.block_name;
                    dropdown.appendChild(option);
                });
            } else {
                console.warn(result.message);
            }
        } catch (error) {
            console.error("Error fetching blocks:", error);
        }
    }
    async function populateGramPanchayatDropdown(blockId) {
        try {
            const response = await fetch(
                `${BASE_URL}/api/method/get_gp_dropdown?block_id=${blockId}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );

            const result = await response.json();

            if (result.data.length > 0) {
                const dropdown = document.getElementById("gpDropdown");
                dropdown.innerHTML = '<option value="">GP</option>';
                result.data.forEach((panchayat) => {
                    const option = document.createElement("option");
                    option.value = panchayat.gp_id;
                    option.textContent = panchayat.gp_name;
                    dropdown.appendChild(option);
                });
            } else {
                console.warn(result.message);
            }
        } catch (error) {
            console.error("Error fetching Gram Panchayats:", error);
        }
    }
    async function populatecrecheDropdown(gpId) {
        try {
            const response = await fetch(
                `${BASE_URL}/api/method/get_creche_dropdown?gp_id=${gpId}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );

            const result = await response.json();

            if (result.data.length > 0) {
                const dropdown = document.getElementById("crecheDropdown");
                dropdown.innerHTML = '<option value="">Creche</option>';
                result.data.forEach((creche) => {
                    const option = document.createElement("option");
                    option.value = creche.creche_id;
                    option.textContent = creche.creche_name;
                    dropdown.appendChild(option);
                });
            } else {
                console.warn(result.message);
            }
        } catch (error) {
            console.error("Error fetching creches:", error);
        }
    }
    function populateYearDropdown() {
        try {
            const currentYear = new Date().getFullYear();
            const dropdown = document.getElementById("yearDropdown");

            // Initialize the dropdown with a default "Year" option
            dropdown.innerHTML = `<option value="">Year</option>`;

            // Dynamically create year options
            for (let year = currentYear; year >= 2020; year--) {
                const option = document.createElement("option");
                option.value = year;
                option.textContent = year;

                // Set the current year as selected
                if (year === currentYear) {
                    option.selected = true;
                }

                dropdown.appendChild(option);
            }
        } catch (error) {
            console.error("Error populating the year dropdown:", error);
        }
    }

    // populateYearDropdown();

    async function populateMonthsDropdown() {
        try {
            const response = await fetch(`${BASE_URL}/api/method/months_list`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            const result = await response.json();

            if (result.data.length > 0) {
                const dropdown = document.getElementById("monthDropdown");
                const monthNames = [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ];

                const currentMonth = new Date().getMonth();

                dropdown.innerHTML = `<option value="">Select Month</option>`;

                result.data.forEach((month, index) => {
                    const option = document.createElement("option");
                    option.value = index + 1;
                    option.textContent = month;

                    if (index === currentMonth) {
                        option.selected = true;
                    }

                    dropdown.appendChild(option);
                });
            } else {
                console.warn(result.message);
            }
        } catch (error) {
            console.error("Error fetching months:", error);
        }
    }

    // populateMonthsDropdown();
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
        const baseUrl = `${BASE_URL}/api/method/frappe.val.dashboard`;
        const apiParams = {
            year: year,
            month: month,
            partner_id: selectedPartnerId,
            state_id: stateId,
            district_id: district_id,
            block_id: block_id,
            gp_id: gp_id,
            creche_id: creche_id
        };

        const constructApiUrl = (section) => {
            const apiUrl = new URL(`${baseUrl}.${section}`);
            Object.entries(apiParams).forEach(([key, value]) => {
                if (value) {
                    apiUrl.searchParams.append(key, value);
                }
            });
            return apiUrl.toString();
        };

        const spinnerContainer = document.querySelector(".spinner-container");
        const searchButton = document.getElementById("searchButton");

        if (searchButton) {
            searchButton.disabled = true;
        }

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
            const formattedResponseData = formatResponses(responses); // used to handle the duplicate keys in responses
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
                    console.log("skipped")
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
        } finally {
            if (spinnerContainer) {
                spinnerContainer.style.display = "none";
            }
            if (searchButton) {
                searchButton.disabled = false;
            }
        }
    }


    function formatNumber(number) {
        return new Intl.NumberFormat("en-IN").format(number);
    }

    async function renderCards() {
        const spinnerContainer = document.querySelector(".spinner-container");
        const data = await fetchDashboardData();
        spinnerContainer.style.display = "none";

        const totalCreche = document.querySelector('.total-creche-card');
        totalCreche.innerHTML = ""
        data.Col0.forEach(item => {
            const card = document.createElement('div');
            card.classList.add('card');
            card.style.padding = '20px';
            card.style.width = '300px';
            card.style.height = '150px';
            card.style.border = '1px solid #ccc';
            card.style.borderRadius = '8px';
            card.style.backgroundColor = '#E8E8E8';
            card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            card.style.textAlign = 'center';

            card.innerHTML = `
                    <div style = "font-size: 36px; font-weight: bold; color: #333;" > ${formatNumber(item.value)}</div>
            <div style="font-size: 18px; color: #666;">${item.title}</div>
				`;
            totalCreche.appendChild(card);
        })
        const current_enrolled_children = data.Col2.find(item => item.title === "Current enrolled children").value;
        const current_eligible_children = data.Col2.find(item => item.title === "Current eligible children").value;
        const cumulative_enrolled_children = data.Col2.find(item => item.title === "Cumulative enrolled children").value;
        const cumulative_exit_children = data.Col2.find(item => item.title === "Cumulative exit children").value;
        const current_exit_children = data.Col2.find(item => item.title === "Current exit children").value;

        const container = document.querySelector('.cards-container');
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

                let extraLine = '';
                if (item.title === "Current enrolled children") {
                    const percentage = ((current_enrolled_children / current_eligible_children) * 100);
                    extraLine = `<div style = "font-size: 10px; color: #000; font-style:italic; font-weight:600;" > (${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of current eligible children)</div> `;
                } else if (item.title === "Cumulative exit children") {
                    const percentage = ((cumulative_exit_children / cumulative_enrolled_children) * 100);
                    extraLine = `<div style = "font-size: 10px; color: #000; font-style:italic; font-weight:600;" > (${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of cumulative enrolled children)</div> `;
                } else if (item.title === "Current exit children") {
                    const percentage = ((current_exit_children / current_enrolled_children) * 100);
                    extraLine = `<div style = "font-size: 10px; color: #000; font-style:italic; font-weight:600;" > (${isNaN(percentage) ? 0 : percentage.toFixed(1)} % of current enrolled children)</div> `;
                }

                card.innerHTML = `
                <div style = "font-size: 36px; font-weight: bold; color: #333;" > ${formatNumber(item.value)}</div>
                    <div style="font-size: 18px; color: #666;">${item.title}</div>
					${extraLine}
            `;
                column.appendChild(card);
            });

            container.appendChild(column);
        });
    }
    // renderCards();
    document.getElementById("searchButton").addEventListener("click", async function () {

        const spinnerContainer = document.querySelector(".spinner-container");
        const totalCreche = document.querySelector('.total-creche-card');
        const filterDesc = document.querySelector('.filter-desc');
        const partner = document.getElementById('partnerSelect').selectedIndex > 0 ? document.getElementById('partnerSelect').options[document.getElementById('partnerSelect').selectedIndex].text : '';
        const state = document.getElementById('stateDropdown').selectedIndex > 0 ? document.getElementById('stateDropdown').options[document.getElementById('stateDropdown').selectedIndex].text : '';
        const district = document.getElementById('districtDropdown').selectedIndex > 0 ? document.getElementById('districtDropdown').options[document.getElementById('districtDropdown').selectedIndex].text : '';
        const block = document.getElementById('blockDropdown').selectedIndex > 0 ? document.getElementById('blockDropdown').options[document.getElementById('blockDropdown').selectedIndex].text : '';
        const gp = document.getElementById('gpDropdown').selectedIndex > 0 ? document.getElementById('gpDropdown').options[document.getElementById('gpDropdown').selectedIndex].text : '';
        const creche = document.getElementById('crecheDropdown').selectedIndex > 0 ? document.getElementById('crecheDropdown').options[document.getElementById('crecheDropdown').selectedIndex].text : '';
        const month = document.getElementById('monthDropdown').selectedIndex > 0 ? document.getElementById('monthDropdown').options[document.getElementById('monthDropdown').selectedIndex].text : '';



        totalCreche.innerHTML = ""
        const container = document.querySelector(".cards-container");
        container.innerHTML = ""
        spinnerContainer.style.display = "flex";
        // if (selectedPartnerId) {
        const filterValues = [
            partner ? partner : null,
            state ? state : null,
            district ? district : null,
            block ? block : null,
            gp ? gp : null,
            creche ? creche : null,
            year ? year : null,
            month ? month : null,
        ].filter(value => value !== null);

        const filterText = filterValues.join(' - ');

        filterDesc.innerHTML = `
            <div style = "font-family: 'Arial', sans-serif; padding: 10px; color: white !important; background-color: #5979aa; float:right; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); width: fit-content; display: flex; align-items: center; justify-content: center; position: relative;">

			<span style="font-size: 13px; color: white !important; font-weight: bold; margin-right: 25px; text-transform: Uppercase;">${filterText.toUpperCase()}</span>

			<button onclick="location.reload();" style="position: absolute; right: 5px; background: transparent; border: none; color: white; font-size: 20px; cursor: pointer;">
				&times;
			</button>
		</div>
                `;


        try {
            await renderCards();
        } catch (error) {
            console.error("Error making the request:", error);
        }
    });

    document
        .getElementById("partnerSelect")
        .addEventListener("change", async (event) => {
            selectedPartnerId = event.target.value;
        });
    document
        .getElementById("stateDropdown")
        .addEventListener("change", async (event) => {
            stateId = event.target.value;

            if (stateId) {
                console.log(`Partner selected: ${stateId} `);
                await populateDistrictDropdown(stateId);
            }
        });
    document
        .getElementById("districtDropdown")
        .addEventListener("change", async (event) => {
            district_id = event.target.value;

            if (district_id) {
                console.log(`district selected: ${district_id} `);
                await populateBlockDropdown(district_id);
            }
        });
    document
        .getElementById("blockDropdown")
        .addEventListener("change", async (event) => {
            block_id = event.target.value;

            if (block_id) {
                console.log(`district selected: ${block_id} `);
                await populateGramPanchayatDropdown(block_id);
            }
        });
    document
        .getElementById("gpDropdown")
        .addEventListener("change", async (event) => {
            gp_id = event.target.value;

            if (gp_id) {
                console.log(`district selected: ${gp_id} `);
                await populatecrecheDropdown(gp_id);
            }
        });
    document
        .getElementById("crecheDropdown")
        .addEventListener("change", async (event) => {
            creche_id = event.target.value;

            if (creche_id) {
                console.log(`district selected: ${creche_id} `);
            }
        });
    document
        .getElementById("monthDropdown")
        .addEventListener("change", async (event) => {
            month = event.target.value;

            if (month) {
                console.log(`district selected: ${month} `);
            }
        });
    document
        .getElementById("yearDropdown")
        .addEventListener("change", async (event) => {
            year = event.target.value;

            if (year) {
                console.log(`district selected: ${year} `);
            }
        });
    document.addEventListener("DOMContentLoaded", () => {
        const resetButton = document.getElementById("resetButton");
        if (resetButton) {
            resetButton.addEventListener("click", () => {
                console.log("Reset clicked");
                location.reload();
            });
        } else {
            console.error("Reset button not found in DOM.");
        }
    });

    // fetchStatesData();
    frappe.after_ajax(() => {
        fetchPartnerData();
        populateYearDropdown();
        populateMonthsDropdown();
        fetchStatesData();
        renderCards();
    });

};
