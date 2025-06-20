frappe.pages['app-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'App Dashboard',
        single_column: true
    });

    // Add filters
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
            "fieldname": "creche",
            "label": __("Creche"),
            "fieldtype": "Link",
            "options": "Creche",
            "default": "700" // Default to creche 700 as in your example
        }
    ];

    // Add filter fields to page
    filters.forEach(filter => {
        page.add_field(filter);
    });

    // Add action buttons
    let searchBtn = page.add_button(__("Search"), async () => {
        searchBtn.prop('disabled', true);
        try {
            await renderCards();
        } finally {
            searchBtn.prop('disabled', false);
        }
    });

    let resetBtn = page.add_button(__("Reset"), () => {
        filters.forEach(filter => {
            if (filter.default) {
                page.fields_dict[filter.fieldname].set_value(filter.default);
            } else {
                page.fields_dict[filter.fieldname].set_value('');
            }
        });
    });

    // Style buttons
    searchBtn.css({
        "background-color": "#5979aa",
        "color": "white",
        "border-radius": "8px",
        "padding": "8px 16px",
        "font-weight": "bold",
        "margin-right": "10px"
    });
    
    resetBtn.css({
        "background-color": "#F0F0F0",
        "color": "black",
        "border-radius": "8px",
        "padding": "8px 16px",
        "font-weight": "bold"
    });

    // Add dashboard container
    page.main.append(`
        <div class="dashboard-container">
            <div class="dashboard-header" style="margin-bottom: 20px;"></div>
            <div class="spinner-container" style="display: none;">
                <span class="loader"></span>
            </div>
            <div class="cards-container"></div>
        </div>
    `);

    // Add CSS styles
    $('<style>').text(`
        /* Dashboard Styles */
        .dashboard-container {
            padding: 20px;
        }
        
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .dashboard-title {
            font-size: 24px;
            font-weight: 600;
            color: #36414C;
        }
        
        .dashboard-period {
            font-size: 16px;
            color: #6c7680;
        }
        
        /* Cards Layout */
        .cards-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .card {
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }
        
        .card-title {
            font-size: 14px;
            color: #6c7680;
            margin-bottom: 10px;
            font-weight: 500;
        }
        
        .card-value {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 0;
        }
        
        /* Status Colors */
        .status-good {
            color: #2ecc71;
        }
        
        .status-warning {
            color: #f39c12;
        }
        
        .status-danger {
            color: #e74c3c;
        }
        
        .status-neutral {
            color: #3498db;
        }
        
        /* Spinner */
        .spinner-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }
        
        .loader {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: inline-block;
            position: relative;
            border: 3px solid;
            border-color: #3498db #3498db transparent transparent;
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
            border-color: #3498db #3498db transparent transparent;
            animation: rotation 1.5s linear infinite;
        }
        
        @keyframes rotation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes rotationBack {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(-360deg); }
        }
        
        /* Responsive Styles */
        @media (max-width: 768px) {
            .cards-container {
                grid-template-columns: 1fr;
            }
            
            .dashboard-header {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    `).appendTo('head');

    // Function to fetch data and render cards
    async function renderCards() {
        // Show loading spinner
        $('.spinner-container').show();
        $('.cards-container').empty();
        
        try {
            // Get filter values
            const year = page.fields_dict.year.get_value();
            const month = page.fields_dict.month.get_value();
            const creche = page.fields_dict.creche.get_value();
            
            if (!year || !month || !creche) {
                frappe.msgprint(__("Please select year, month and creche"));
                return;
            }
            
            // Fetch data from API
            const response = await frappe.call({
                method: 'frappe.val.app_dashboard.app_dashboard',
                args: {
                    year: year,
                    month: month,
                    creche: creche
                },
                callback: function(r) {
                    // This handles the response
                    if (r.message) {
                        return r.message;
                    }
                    return null;
                }
            });
            
            if (!response || !response.message) {
                throw new Error("No data received from server");
            }
            
            const data = response.message.data;
            
            if (!data || !Array.isArray(data)) {
                throw new Error("Invalid data format received");
            }
            
            // Hide spinner
            $('.spinner-container').hide();
            
            // Update header
            const monthName = page.fields_dict.month.get_selected_option().label;
            const crecheName = data.find(item => item.title === 'Creche')?.value || '';
            
            $('.dashboard-header').html(`
                <div>
                    <h2 class="dashboard-title">${crecheName} Dashboard</h2>
                    <div class="dashboard-period">${monthName} ${year}</div>
                </div>
            `);
            
            // Group data by category
            const enrollmentData = data.filter(item => 
                ['Current Eligible Children', 'Cumulative Enrolled Children', 'Enrollment Percentage', 'Attendance Percentage'].includes(item.title)
            );
            
            const nutritionData = data.filter(item => 
                item.title.includes('Weight for Age') || item.title.includes('Weight for Height')
            );
            
            const healthData = data.filter(item => 
                ['Major Illness', 'Growth Faltering 1', 'Growth Faltering 2', 'Referred', 'NRC'].includes(item.title)
            );
            
            const visitsData = data.filter(item => 
                ['Home Visits Done', 'Home Visits Planned'].includes(item.title)
            );
            
            // Render cards
            renderCardGroup('Enrollment Metrics', enrollmentData);
            renderCardGroup('Nutrition Status', nutritionData);
            renderCardGroup('Health Indicators', healthData);
            renderCardGroup('Home Visits', visitsData);
            
        } catch (error) {
            $('.spinner-container').hide();
            frappe.msgprint(__('Error fetching data: ') + (error.message || 'Unknown error'));
            console.error('API Error:', error);
        }
    }
    
    function renderCardGroup(title, items) {
        if (!items || items.length === 0) return;
        
        const groupHtml = `
            <div class="card-group" style="grid-column: 1 / -1;">
                <h3 style="margin-bottom: 15px; color: #36414C; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px;">${title}</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;">
                    ${items.map(item => renderCard(item)).join('')}
                </div>
            </div>
        `;
        
        $('.cards-container').append(groupHtml);
    }
    
    function renderCard(item) {
        if (!item || !item.title) return '';
        
        const statusClass = getStatusClass(item.title, item.value);
        const formattedValue = formatValue(item.title, item.value);
        
        return `
            <div class="card">
                <div class="card-title">${item.title}</div>
                <div class="card-value ${statusClass}">${formattedValue}</div>
            </div>
        `;
    }
    
    function getStatusClass(title, value) {
        if (!title || value === undefined || value === null) return 'status-neutral';
        
        if (title.includes('Percentage')) {
            if (title === 'Attendance Percentage') {
                if (value < 70) return 'status-danger';
                if (value < 85) return 'status-warning';
                return 'status-good';
            } else {
                if (value < 80) return 'status-danger';
                if (value < 100) return 'status-warning';
                return 'status-good';
            }
        }
        
        if (title.includes('Severe') || title.includes('Major Illness') || title.includes('Growth Faltering')) {
            return value > 0 ? 'status-danger' : 'status-good';
        }
        
        if (title.includes('Moderate')) {
            return value > 0 ? 'status-warning' : 'status-good';
        }
        
        return 'status-neutral';
    }
    
    function formatValue(title, value) {
        if (value === undefined || value === null) return 'N/A';
        
        if (title.includes('Percentage')) {
            return value + '%';
        }
        return value;
    }

    // Initial render
    renderCards();
};