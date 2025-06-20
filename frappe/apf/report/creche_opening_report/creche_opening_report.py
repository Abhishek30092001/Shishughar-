import frappe
from frappe.utils import nowdate
from datetime import date

def execute(filters=None):
    columns = get_columns(filters)
    data = get_enrollment_data(filters)
    return columns, data

def get_columns(filters):
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    selected_year = filters.get("year") if filters else nowdate().split('-')[0]

    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120}
    ]

    for month in months:
        month_label = f"{month[:3]}-{selected_year}"
        columns.append({"label": month_label, "fieldname": month.lower(), "fieldtype": "Int", "width": 120})

    return columns

@frappe.whitelist()
def get_enrollment_data(filters=None):
    if not filters:
        filters = {}

    # Initialize parameters
    params = {
        "year": int(filters.get("year")) if filters.get("year") else int(nowdate().split('-')[0])
    }

    # Get user session data
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
    
    # Get user's state access
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s 
        ORDER BY ts.state_name
    """
    current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
    state_id = filters.get("state") or (current_user_state[0]['state_id'] if current_user_state else None)

    # Handle creche opening date range filter
    range_type = filters.get("cr_opening_range_type")
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if range_type == "between" and date_range and len(date_range) == 2:
            params.update({
                "cstart_date": date_range[0],
                "cend_date": date_range[1]
            })
        elif range_type == "before" and single_date:
            params.update({
                "cstart_date": date(2017, 1, 1),
                "cend_date": single_date
            })
        elif range_type == "after" and single_date:
            params.update({
                "cstart_date": single_date,
                "cend_date": date.today()
            })
        elif range_type == "equal" and single_date:
            params.update({
                "cstart_date": single_date,
                "cend_date": single_date
            })

    # Build conditions
    conditions = ["YEAR(ci.date_of_checkin) = %(year)s"]
    
    # Partner filter
    if partner_id:
        conditions.append("c.partner_id = %(partner_id)s")
        params["partner_id"] = partner_id
        
    # State filter
    if state_id:
        conditions.append("c.state_id = %(state_id)s")
        params["state_id"] = state_id
        
    # Location filters
    location_fields = ["district", "block", "gp", "creche"]
    for field in location_fields:
        if filters.get(field):
            conditions.append(f"c.{field}_id = %({field}_id)s")
            params[f"{field}_id"] = filters.get(field)

    # Other filters
    if supervisor_id := filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = supervisor_id
        
    if creche_status_id := filters.get("creche_status_id"):
        conditions.append("c.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = creche_status_id
        
    if phases := filters.get("phases"):
        phases_cleaned = [p.strip() for p in phases.split(",") if p.strip().isdigit()]
        if phases_cleaned:
            conditions.append("c.phase IN %(phases)s")
            params["phases"] = phases_cleaned
            
    if "cstart_date" in params and "cend_date" in params:
        conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")

    condition_str = " AND ".join(conditions)
    
    # Build SQL query with parameterized values
    sql_query = f"""
        SELECT
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            c.creche_name AS creche,
            c.name AS creche_id,
            SUM(IF(MONTH(ci.date_of_checkin) = 1 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS january,
            SUM(IF(MONTH(ci.date_of_checkin) = 2 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS february,
            SUM(IF(MONTH(ci.date_of_checkin) = 3 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS march,
            SUM(IF(MONTH(ci.date_of_checkin) = 4 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS april,
            SUM(IF(MONTH(ci.date_of_checkin) = 5 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS may,
            SUM(IF(MONTH(ci.date_of_checkin) = 6 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS june,
            SUM(IF(MONTH(ci.date_of_checkin) = 7 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS july,
            SUM(IF(MONTH(ci.date_of_checkin) = 8 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS august,
            SUM(IF(MONTH(ci.date_of_checkin) = 9 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS september,
            SUM(IF(MONTH(ci.date_of_checkin) = 10 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS october,
            SUM(IF(MONTH(ci.date_of_checkin) = 11 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS november,
            SUM(IF(MONTH(ci.date_of_checkin) = 12 AND YEAR(ci.date_of_checkin) = %(year)s, 1, 0)) AS december
        FROM
            `tabCreche Check In` AS ci
        JOIN
            `tabCreche` AS c ON ci.creche_id = c.name
        JOIN
            `tabState` AS s ON c.state_id = s.name
        JOIN
            `tabDistrict` AS d ON c.district_id = d.name
        JOIN
            `tabBlock` AS b ON c.block_id = b.name
        JOIN
            `tabGram Panchayat` AS g ON c.gp_id = g.name
        JOIN
            `tabPartner` AS p ON c.partner_id = p.name
        WHERE
            {condition_str}
        GROUP BY
            p.partner_name, s.state_name, d.district_name, 
            b.block_name, g.gp_name, c.creche_name, c.name
        ORDER BY
            p.partner_name, s.state_name, d.district_name, 
            b.block_name, g.gp_name, c.creche_name
    """

    # For debugging
    frappe.logger().debug(f"Executing query: {sql_query} with params: {params}")
    
    data = frappe.db.sql(sql_query, params, as_dict=True)
    return data