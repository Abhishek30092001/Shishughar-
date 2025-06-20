import frappe
import calendar
from frappe.utils import nowdate
from datetime import date

def execute(filters=None):
    columns = get_columns(filters)
    data = get_summary_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 150},
        {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 160},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Creche IDX", "fieldname": "creche_idx", "fieldtype": "Data", "width": 150},
        {"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170},
        {"label": "Total Days Submitted", "fieldname": "submitted", "fieldtype": "Int", "width": 200},
        {"label": "Total Days Not Submitted", "fieldname": "not_submitted", "fieldtype": "Int", "width": 200},
    ]
    
    month = int(filters.get("month", nowdate().split('-')[1]))
    year = int(filters.get("year", nowdate().split('-')[0]))
    last_day = calendar.monthrange(year, month)[1]

    for day in range(1, last_day + 1):
        columns.append({
            "label": f"{day:02d}-{month:02d}-{year}",
            "fieldname": f"day_{day}",
            "fieldtype": "Data",
            "width": 120
        })
        
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    partner = frappe.db.get_value("User", frappe.session.user, "partner")
    month = int(filters.get("month", nowdate().split('-')[1]))
    year = int(filters.get("year", nowdate().split('-')[0]))
    last_day = calendar.monthrange(year, month)[1]

    # Handle creche opening date filters
    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None

    # Get state filter
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s 
        ORDER BY ts.state_name
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state = filters.get("state") or (current_user_state[0]['state_id'] if current_user_state else None)
    state = None if not state else state

    # Process date range filters
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range
        elif range_type == "before" and single_date:
            cstart_date, cend_date = date(2017, 1, 1), single_date
        elif range_type == "after" and single_date:
            cstart_date, cend_date = single_date, date.today()
        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

    # Other filters
    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None

    # Build filters dictionary
    filters_dict = {
        'selected_partner': partner if partner else filters.get('partner'),
        'state': state,
        'district': filters.get('district'),
        'supervisor_id': filters.get('supervisor_id'),
        'block': filters.get('block'),
        'gp': filters.get('gp'),
        'creche': filters.get('creche'),
        'month': month,
        'year': year,
        'cstart_date': cstart_date,
        'cend_date': cend_date,
        'creche_status_id': creche_status_id,
        'phases': phases_cleaned
    }

    # Build conditions for the query
    conditions = []
    if filters_dict['selected_partner']:
        conditions.append("cs.partner_id = %(selected_partner)s")
    if filters_dict['state']:
        conditions.append("cs.state_id = %(state)s")
    if filters_dict['district']:
        conditions.append("cs.district_id = %(district)s")
    if filters_dict['block']:
        conditions.append("cs.block_id = %(block)s")
    if filters_dict['gp']:
        conditions.append("cs.gp_id = %(gp)s")
    if filters_dict['creche']:
        conditions.append("cs.c_name = %(creche)s")
    if filters_dict['supervisor_id']:
        conditions.append("cs.supervisor_id = %(supervisor_id)s")
    if cstart_date and cend_date:
        conditions.append("cs.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    if filters_dict['phases']:
        conditions.append("(%(phases)s IS NULL OR FIND_IN_SET(cs.phase, %(phases)s))")
    if filters_dict['creche_status_id']:
        conditions.append("(%(creche_status_id)s IS NULL OR cs.creche_status_id = %(creche_status_id)s)")

    condition_str = " AND ".join(conditions) if conditions else "1=1"

    # Generate dynamic day columns
    daily_columns = []
    for day in range(1, last_day + 1):
        daily_columns.append(f"""
        CASE SUBSTRING(month_status, {day}, 1)
            WHEN '0' THEN 'Not Submitted'
            WHEN '1' THEN 'Open'
            WHEN '2' THEN 'Closed'
            WHEN '4' THEN 'Not Opened Yet'
            WHEN '8' THEN 'Future Date'
            ELSE 'Unknown'
        END AS day_{day}
        """)

    # Main query
    sql_query = f"""
    SELECT
        cs.partner_name AS partner,
        cs.state_name AS state,
        cs.district_name AS district,
        cs.block_name AS block,
        cs.gp_name AS gp,
        cs.creche_name AS creche_name,
        cs.creche_id AS creche_id,
        cs.c_name AS creche_idx,
        DATE_FORMAT(cs.creche_opening_date, '%%d-%%m-%%Y') AS 'creche_opening_date',
        {", ".join(daily_columns)}
    FROM (
        SELECT
            cs.*,
            SUBSTRING_INDEX(
                SUBSTRING_INDEX(cs.creche_status_by_day, '|', %(month)s),
                '|', -1
            ) AS month_status
        FROM `tabCreche Summary` cs
        WHERE cs.year = %(year)s
        AND {condition_str}
    ) AS cs
    ORDER BY cs.partner_name, cs.state_name, cs.district_name, cs.block_name, cs.gp_name, cs.creche_name
    """

    # Execute query and process results
    data = frappe.db.sql(sql_query, filters_dict, as_dict=True)
    
    # Calculate submitted and not submitted counts
    for row in data:
        submitted_count = sum(1 for day in range(1, last_day + 1) if row.get(f"day_{day}") in ["Open", "Closed"])
        not_submitted_count = sum(1 for day in range(1, last_day + 1) if row.get(f"day_{day}") == "Not Submitted")
        row["submitted"] = submitted_count
        row["not_submitted"] = not_submitted_count

    # Calculate daily totals for summary row
    daily_totals = {}
    for day in range(1, last_day + 1):
        daily_totals[f"day_{day}"] = sum(1 for row in data if row.get(f"day_{day}") in ["Open", "Closed"])

    # Add summary row
    summary_row = {
        "creche_name": "<b style='color:black;'>Total</b>",
        "submitted": sum(row.get("submitted", 0) for row in data),
        "not_submitted": sum(row.get("not_submitted", 0) for row in data),
    }
    for day in range(1, last_day + 1):
        summary_row[f"day_{day}"] = daily_totals[f"day_{day}"]
    data.append(summary_row)
    
    return data