frappe.pages['mis_dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Mis Dashboard',
		single_column: true
	});


  page.main.append(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/frappe-charts@1.2.4/dist/frappe-charts.min.iife.js"></script>        <title>Creche Report</title>
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
                display: grid;
                gap: 15px;
                padding: 30px 20px;
                background-color: white;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
                grid-template-columns: repeat(10, 1fr); /* Default for large and medium devices */
                }

                select {
                width: 100%;
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
                background-color: #5979aa;
                color: white;
                }

                .reset-btn:hover {
                background-color: #5072A7;
                }

                .search-btn {
                background-color: #4CAF50;
                color: white;
                }

                .search-btn:hover {
                background-color: #388E3C;
                }

                /* Responsive Adjustments */
                @media (max-width: 768px) {
                .filters {
                    grid-template-columns: repeat(2, 1fr); /* 2 items per row for small devices */
                }
                }


                .tabs {
                border-radius: 10px;
                background-color: #fff;
                display: grid;
                gap: 15px;
                margin-top: 5px;
                margin-bottom:10px;
                grid-template-columns: repeat(8, 1fr);
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }

                .tab {
                padding: 5px;
                text-align: center;
                font-size: 0.75rem;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                .tab:hover {
                background-color: #eaeaea;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }

                @media (min-width: 1024px) {
                .tabs {
                    grid-template-columns: repeat(8, 1fr);
                }
                }

                @media (max-width: 1023px) and (min-width: 769px) {
                .tabs {
                    grid-template-columns: repeat(4, 1fr);
                }
                }

                @media (max-width: 768px) {
                .tabs {
                    grid-template-columns: repeat(2, 1fr);
                }
                .tab {
                    font-size: 0.9rem;
                    padding: 8px;
                }
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
            margin-bottom:10px;
            }
                  /* main-container */
            .main-container {
            display: flex;
            gap: 15px;
            height: 60vh;
            margin-bottom: 20px;
            }

            /* Indicators Section */
            .indicators {
            flex: 1 1 30%;
            background-color: #f9f9f9;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            gap: 15px;
            max-height: 100%;
            }

            /* Header */
            .indicator-header {
            margin-top: 15px;
            margin-bottom: 0px !important;
            font-size: 1.2rem;
            font-weight: bold;
            text-align: center;
            color: #333;
            }

            /* Indicator List */
            .indicator-list {
            list-style: circle;
            padding-top: 10px;
            margin: 0;
            height: 100%;  
            overflow-y: auto;  
            border: 1px solid #ddd;
            background-color: #ffffff;
            max-height: 100%;
            border-radius:0 0 8px 8px;
            }

            .indicator-item {
            padding: 10px 15px;
            margin: 0;
            border-bottom: 1px solid #f0f0f0;
            cursor: pointer;
            transition: background-color 0.3s ease;
            }

            .indicator-item:last-child {
            border-bottom: none; /* Remove border for the last item */
            }

            .indicator-item:hover {
            background-color: #eaeaea;
            }


            /* Charts Section */
            .charts {
            flex: 1 1 70%; /* 70% width for large devices */
            flex-direction:column;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            max-height: 100%;
            }
            .chart-header{
             text-align: left;
            }
            #chartField {
            width: 100%;
            min-height: 300px;
            border: 2px dashed #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 1.2rem;
            max-height: 100%;
            }

            /* Responsive Adjustments */
            @media (max-width: 768px) {
            .main-container {
                flex-direction: column; /* Stack sections for small devices */
            }

            .indicators, .charts {
                flex: 1 1 100%; /* Full width for small devices */
            }
            }
            .tab.active {
              color: #fff;
              background-color: #5979aa;
              border: 1px solid #426DAD;
            }
            .indicator-item {
              padding: 5px;
              cursor: pointer;
            }

            .indicator-item.selected {
              list-style: circle;
              background-color: #5979aa;
              color: white;
            }
           .graph-svg-tip, .graph-svg-tip > .svg-pointer{
                background: #363636;
            }
            .graph-svg-tip > .title, .graph-svg-tip > .title > strong {
                color: #fff;
            }
            .graph-svg-tip.comparison .title, .graph-svg-tip.comparison .title strong{
                color: #fff !important;
            }
            .tab.disabled {
              pointer-events: none;
              opacity: 0.6;       
              cursor: not-allowed; 
            }
            svg.frappe-chart {
              overflow: visible;
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
          <select id="yearDropdown">
            <option value="">Year</option>
          </select>
          <select id="monthDropdown">
            <option value="">Month</option>
          </select>
        
          <!-- Modern Buttons -->
          <div class="filter-buttons">
            <button id="searchButton" class="modern-btn search-btn">Search</button>
            <button id="resetButton" type="button" class="modern-btn reset-btn">Reset</button>
          </div>
        </div>

        <!-- Tabs Section -->
        <div class="tabs">
          <div class="tab" id="demography">Demography</div>
          <div class="tab" id="operational_details">Operational Details</div>
          <div class="tab" id="anthropometry">Anthropometry</div>
          <div class="tab" id="creche_related_activities">Creche Activities</div>
          <div class="tab" id="red_flag">Red Flag</div>
          <div class="tab" id="comparison_of_base_line">Baseline Comparison</div>
          <div class="tab" id="time_series_monthly_analysis">Time Series Analysis</div>
          <div class="tab" id="other_details">Other Details</div>
        </div>
        <!--filter-desc-->
        <div class="filter-desc"></div>
         <!-- cards and indicators list -->
                <section class="main-container">
                  <!-- Indicators Section -->
                  <div class="indicators">
                      <h3 class="indicator-header">Select Indicator</h3>
                      <ul class="indicator-list" id="indicatorList"></ul>
                  </div>

                  <!-- Charts Section -->
                  <div class="charts">
                      <h3 class="chart-header"></h3>  
                      <div class="spinner-container" style="margin: auto;">
                            <span class="loader"></span>
                        </div>        
                      <div id="chartField"></div>

                  </div>
                </section>
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
let chartIndicator;
let chartEndpoint;
let chartType;
let chartColors;
const indicatorsList = {
  demography: [
    {
      indicator: "Eligible vs enrolled children",
      type: "line",
      colors: ["#0047AB", "#0BDA51"],
      endpoint: "get_eligible_enrolled_data",
    },
    {
      indicator: "Children enrolled at age in months",
      type: "pie",
      endpoint: "age_in_months",
    },
    {
      indicator: "Specially abled children",
      type: "pie",
      endpoint: "get_specially_abled_children",
    },
    {
      indicator: "Education level of mother",
      type: "pie",
      // colors: ["#FFF1C5"],
      endpoint: "get_education_level_mother",
    },
    // {
    //   indicator: "Average enrollment age",
    //   type: "bar",
    //   endpoint: "avg_enroll_in_month",
    // },
    {
      indicator: "Registered households",
      type: "bar",
      endpoint: "get_reg_HH",
    },
    {
      indicator: "Households religion wise",
      type: "pie",
      endpoint: "get_religion_data",
    },
    {
      indicator: "Households caste wise",
      type: "pie",
      endpoint: "get_caste_data",
    },
    {
      indicator: "Households occupation wise",
      type: "pie",
      endpoint: "get_occupation_data",
    },
    {
      indicator: "Households migrating",
      type: "pie",
      endpoint: "hh_migration_data",
    },
    // {
    //   indicator: "Households migrating more than 6 months",
    //   type: "line",
    //   endpoint: "/endpoint/households_migrating_more_than_6_months",
    // },
    // {
    //   indicator: "Households migrating less than 6 months",
    //   type: "bar",
    //   endpoint: "/endpoint/households_migrating_less_than_6_months",
    // },
  ],
  anthropometry: [
    {
      indicator: "Underweight children",
      type: "bar",
      endpoint: "get_underweight_children",
    },
    {
      indicator: "Stunted children",
      type: "bar",
      endpoint: "get_stuned_children",
    },
    {
      indicator: "Wasted children",
      type: "bar",
      endpoint: "get_wasted_children",
    },
  ],
  operational_details: [
    {
      indicator: "Average number of days creche open",
      type: "bar",
      endpoint: "avg_creche_open",
    },
    // {
    //   indicator: "Average attendance per child",
    //   type: "bar",
    //   endpoint: "avg_attendance_per_child",
    // },
    {
      indicator: "Children received THR from AWC",
      type: "bar",
      endpoint: "awc_thr",
    },
    {
      indicator: "Children whose weight has been taken at AWC",
      type: "bar",
      endpoint: "weight_awc",
    },
    {
      indicator: "Children eligible and taken to VHND",
      type: "bar",
      endpoint: "curr_eligible_vhnd",
    },
    {
      indicator: "Children eligible and not taken to VHND",
      type: "bar",
      endpoint: "curr_eligible_not_vhnd",
    },
    {
      indicator: "Absenteeism (N)",
      type: "bar",
      endpoint: "absent_present",
    },
    {
      indicator: "Child exit reason",
      type: "pie",
      endpoint: "get_exit_reasons",
    },
    {
      indicator: "Number of checkins ",
      type: "bar",
      endpoint: "get_creche_checkin",
    },
    {
      indicator: "Creche house types",
      type: "pie",
      endpoint: "creche_house_types",
    },
    {
      indicator: "Hard to reach creches",
      type: "pie",
      endpoint: "hard_to_reach_creche",
    },
    {
      indicator: "Grievances registered",
      type: "pie",
      endpoint: "get_grievance_data",
    },
  ],
  red_flag: [
    {
      indicator: "Red flag children",
      type: "bar",
      endpoint: "red_flag_chidren",
    },
    // {
    //   indicator: "Children admitted to NRC",
    //   type: "line",
    //   endpoint: "/endpoint/children_admitted_nrc",
    // },
    // {
    //   indicator: "Children referred to Health centre",
    //   type: "bar",
    //   endpoint: "/endpoint/children_referred_to_health_centre",
    // },
    // {
    //   indicator: "Red flag children on the basis of anthropometry",
    //   type: "line",
    //   endpoint: "red_flag_anthro",
    // },
    // {
    //   indicator: "Children referred to NRC",
    //   type: "bar",
    //   endpoint: "/endpoint/children_referred_to_nrc",
    // },
    {
      indicator: "Children on the basis of illness",
      type: "line",
      endpoint: "red_flag_illness",
    },
  ],
  comparison_of_base_line: [
    {
      indicator: "Weight for age Status",
      type: "bar",
      endpoint: "weight_for_age_status",
    },
    {
      indicator: "Height for age Status",
      type: "bar",
      endpoint: "height_for_age_status",
    },
    {
      indicator: "Weight for Height Status",
      type: "bar",
      endpoint: "weight_for_height_status",
    },
    {
      indicator: "MUAC Status",
      type: "line",
      endpoint: "/endpoint/muac_status",
    },
  ],
  time_series_monthly_analysis: [
    {
      indicator: "Height for Age Status",
      type: "bar",
      endpoint: "height_for_age_status",
      colors: ["#E03C32", "#FFD301", "#7BB662"],
    },
    {
      indicator: "Weight for Age Status",
      type: "bar",
      endpoint: "weight_for_age_status",
      colors: ["#E03C32", "#FFD301", "#7BB662"],
    },
    {
      indicator: "Weight for Height Status",
      type: "bar",
      endpoint: "weight_for_height_status",
      colors: ["#E03C32", "#FFD301", "#7BB662"],
    },
    // {
    //   indicator: "Status of one month growth faltered children ? Percentages",
    //   type: "line",
    //   endpoint: "/endpoint/one_month_growth_faltered",
    // },
    // {
    //   indicator: "Status of two month growth faltered children ? percentages",
    //   type: "bar",
    //   endpoint: "/endpoint/two_month_growth_faltered",
    // },
    // {
    //   indicator:
    //     "Status of more than two month growth faltered children ? percentages",
    //   type: "line",
    //   endpoint: "/endpoint/more_than_two_month_growth_faltered",
    // },
    // {
    //   indicator: "Average number of creche open days",
    //   type: "bar",
    //   endpoint: "/endpoint/average_creche_open_days",
    // },
    // {
    //   indicator: "Average attendance of the children",
    //   type: "line",
    //   endpoint: "/endpoint/average_attendance_children",
    // },
    // {
    //   indicator: "percentage of total redflag children",
    //   type: "bar",
    //   endpoint: "/endpoint/percentage_redflag_children",
    // },
    {
      indicator: "Children referred to NRC",
      type: "bar",
      endpoint: "child_ref_nrc",
    },
    {
      indicator: "Children admitted to NRC",
      type: "bar",
      endpoint: "child_adm_nrc",
    },
    {
      indicator: "Children referred to Health centre",
      type: "bar",
      endpoint: "ref_health_care",
    },
    {
      indicator: "Children visited Health centre",
      type: "bar",
      endpoint: "visited_health_care",
    },
  ],
  creche_related_activities: [
    {
      indicator: "Number of Creche Committee Meetings",
      type: "line",
      endpoint: "creche_committee_meeting",
    },
    {
      indicator: "Meetings Participation",
      type: "line",
      endpoint: "meetings_and_participations",
    },
    {
      indicator: "Meeting for which AWW present",
      type: "line",
      endpoint: "meetings_and_participations_aww",
    },
    {
      indicator: "Meetings for which ASHA Present",
      type: "line",
      endpoint: "meetings_and_participations_asha",
    },
  ],
  other_details: [
    {
      indicator: "Children with disability",
      type: "bar",
      endpoint: "children_having_disability",
    },
    {
      indicator: "Children with long-term illness",
      type: "bar",
      endpoint: "children_having_long_illness",
    },
  ],
};

const tabs = document.querySelectorAll(".tab");
const indicatorList = document.getElementById("indicatorList");

function renderIndicators(tabId) {
  indicatorList.innerHTML = "";
  if (indicatorsList[tabId]) {
    const indicators = indicatorsList[tabId];
    indicators.forEach((indicator, index) => {
      const li = document.createElement("li");
      li.classList.add("indicator-item");
      li.textContent = indicator.indicator;

      if (index === 0) {
        li.classList.add("selected");
        chartEndpoint = indicator.endpoint;
        chartType = indicator.type;
        chartIndicator = indicator.indicator;
        chartColors = indicator.colors;
        fetchChartData(chartEndpoint);
      }
      li.addEventListener("click", function () {
        const allIndicators =
          indicatorList.querySelectorAll(".indicator-item");
        allIndicators.forEach((ind) => ind.classList.remove("selected"));
        li.classList.add("selected");
        chartEndpoint = indicator.endpoint;
        chartType = indicator.type;
        chartIndicator = indicator.indicator;
        chartColors = indicator.colors;
        fetchChartData(chartEndpoint);
      });

      indicatorList.appendChild(li);
    });
  }
}

function handleTabClick(event) {
  tabs.forEach((t) => t.classList.remove("active"));
  event.target.classList.add("active");

  renderIndicators(event.target.id);

  const firstIndicator = indicatorList.querySelector("li");
  if (firstIndicator) {
    firstIndicator.classList.add("selected");
  }
}

tabs.forEach((tab) => {
  tab.addEventListener("click", handleTabClick);
});

document.querySelector(".tab").classList.add("active");
renderIndicators(document.querySelector(".tab").id);

// Adding the 'disabled' class to the specified tabs temp-
const tabsToDisable = ["comparison_of_base_line"];

tabsToDisable.forEach((tabId) => {
  const tab = document.getElementById(tabId);
  if (tab) {
    tab.classList.add("disabled");
  }
});

// tabs script ended

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
async function fetchSupervisorData() {
  try {
    const response = await fetch(`${BASE_URL}/api/method/supervisor_list`, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    const supervisorList = data.data;

    const supervisorSelect = document.getElementById("supervisorSelect");
    console.log(supervisorSelect, "23456");
    supervisorList.forEach((supervisor) => {
      const option = document.createElement("option");
      option.value = supervisor.supervisor_id;
      option.textContent = supervisor.full_name;
      supervisorSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Error fetching partner data:", error);
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

    const response = await fetch(
      `${BASE_URL}/api/method/get_states_dropdown`,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

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
    stateDropdown.innerHTML =
      '<option value="">Error loading states</option>';
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

      dropdown.innerHTML = `<option value="">Month</option>`;

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

async function fetchChartData(endpoint) {
  let spinnerContainer = document.querySelector(".spinner-container");
  let chartField = document.querySelector("#chartField");
  spinnerContainer.style.display = "flex";
  chartField.style.display = "none";
  let apiUrl = `${BASE_URL}/api/method/frappe.val.mis_dashboard.${endpoint}`;

  // Create an object to hold the query parameters
  let params = {
    year: year,
    month: month,
    partner_id: selectedPartnerId,
    state_id: stateId,
    district_id: district_id,
    block_id: block_id,
    gp_id: gp_id,
    creche_id: creche_id,
  };

  // Filter out undefined or empty parameters
  params = Object.fromEntries(
    Object.entries(params).filter(
      ([key, value]) => value !== undefined && value !== ""
    )
  );

  // Build the URL with the parameters
  const queryParams = new URLSearchParams(params).toString();
  let Url = `${apiUrl}/?${queryParams}`;

  try {
    const response = await fetch(Url);
    const data = await response.json();

    if (data && data.data) {
      await renderChart(data.data, chartType, chartColors);
      return;
    } else {
      throw new Error("Invalid data format received.");
    }
  } catch (error) {
    console.error("Error fetching chart data:", error);
    return null;
  } finally {
    chartField.style.display = "flex";
    spinnerContainer.style.display = "none";
    console.log("set to none");
  }
}

async function renderChart(data, type, colors) {
  const chartHeader = document.querySelector(".chart-header");
  chartHeader.textContent = `${chartIndicator}`;

  let chartElement = document.querySelector("#chartField");
  Object.assign(chartElement.style, {
    width: "100%",
    minHeight: "300px",
    border: "2px dashed #ddd",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#999",
    fontSize: "1.2rem",
    maxHeight: "100%",
  });
  const options = {
    data: data,
    type: type,
    colors: colors || [
      "#FF5733",
      "#33FF57",
      "#3357FF",
      "#F833FF",
      "#FFB833",
      "#33FFF6",
      "#F6FF33",
      "#8D33FF",
    ],
    legend: {
      position: "bottom",
      offsetX: 0,
      offsetY: 10,
      clickable: true,
      fontSize: 12,
    },
    barOptions: {
      spaceRatio: 0.5,
      stacked: type === "bar",
    },
    padding: { top: 30, bottom: 30, left: 20, right: 20 },
    width: 500,
    height: 300,
    responsive: true,
  };

  // if (type === "bar") {
  //   options.stacked = true;
  // }

  const chart = new frappe.Chart("#chartField", options);
}

document
  .getElementById("searchButton")
  .addEventListener("click", async function () {
    // const spinnerContainer = document.querySelector(".spinner-container");
    const filterDesc = document.querySelector(".filter-desc");
    const partner =
      document.getElementById("partnerSelect").selectedIndex > 0
        ? document.getElementById("partnerSelect").options[
            document.getElementById("partnerSelect").selectedIndex
          ].text
        : "";
    const state =
      document.getElementById("stateDropdown").selectedIndex > 0
        ? document.getElementById("stateDropdown").options[
            document.getElementById("stateDropdown").selectedIndex
          ].text
        : "";
    const district =
      document.getElementById("districtDropdown").selectedIndex > 0
        ? document.getElementById("districtDropdown").options[
            document.getElementById("districtDropdown").selectedIndex
          ].text
        : "";
    const block =
      document.getElementById("blockDropdown").selectedIndex > 0
        ? document.getElementById("blockDropdown").options[
            document.getElementById("blockDropdown").selectedIndex
          ].text
        : "";
    const gp =
      document.getElementById("gpDropdown").selectedIndex > 0
        ? document.getElementById("gpDropdown").options[
            document.getElementById("gpDropdown").selectedIndex
          ].text
        : "";
    const creche =
      document.getElementById("crecheDropdown").selectedIndex > 0
        ? document.getElementById("crecheDropdown").options[
            document.getElementById("crecheDropdown").selectedIndex
          ].text
        : "";
    const month =
      document.getElementById("monthDropdown").selectedIndex > 0
        ? document.getElementById("monthDropdown").options[
            document.getElementById("monthDropdown").selectedIndex
          ].text
        : "";

    const container = document.querySelector("#chartField");
    container.innerHTML = "";
    // spinnerContainer.style.display = "flex";
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
    ].filter((value) => value !== null);

    const filterText = filterValues.join(" - ");

    filterDesc.innerHTML = `
    <div style="font-family: 'Arial', sans-serif; padding: 10px; color: white !important; background-color: #5979aa; float:right; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); width: fit-content; display: flex; align-items: center; justify-content: center; position: relative;">
      <span style="font-size: 13px; color: white !important; font-weight: bold; margin-right: 25px; text-transform: Uppercase;">${filterText.toUpperCase()}</span>
      <button onclick="location.reload();" style="position: absolute; right: 5px; background: transparent; border: none; color: white; font-size: 20px; cursor: pointer;">
        &times;
      </button>
    </div>
  `;
    await fetchChartData(chartEndpoint);
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
      console.log(`Partner selected: ${stateId}`);
      await populateDistrictDropdown(stateId);
    }
  });
document
  .getElementById("districtDropdown")
  .addEventListener("change", async (event) => {
    district_id = event.target.value;

    if (district_id) {
      console.log(`district selected: ${district_id}`);
      await populateBlockDropdown(district_id);
    }
  });
document
  .getElementById("blockDropdown")
  .addEventListener("change", async (event) => {
    block_id = event.target.value;

    if (block_id) {
      console.log(`district selected: ${block_id}`);
      await populateGramPanchayatDropdown(block_id);
    }
  });
document
  .getElementById("gpDropdown")
  .addEventListener("change", async (event) => {
    gp_id = event.target.value;

    if (gp_id) {
      console.log(`district selected: ${gp_id}`);
      await populatecrecheDropdown(gp_id);
    }
  });
document
  .getElementById("crecheDropdown")
  .addEventListener("change", async (event) => {
    creche_id = event.target.value;

    if (creche_id) {
      console.log(`district selected: ${creche_id}`);
    }
  });
document
  .getElementById("monthDropdown")
  .addEventListener("change", async (event) => {
    month = event.target.value;

    if (month) {
      console.log(`district selected: ${month}`);
    }
  });
document
  .getElementById("yearDropdown")
  .addEventListener("change", async (event) => {
    year = event.target.value;

    if (year) {
      console.log(`district selected: ${year}`);
    }
  });
document.getElementById("resetButton").addEventListener("click", () => {
  console.log("clickeddd reset");
  location.reload();
});
fetchPartnerData();
// fetchSupervisorData();
populateYearDropdown();
populateMonthsDropdown();
fetchStatesData();
};





          // <select id="supervisorSelect">
          //   <option value="">Supervisor</option>
          // </select>