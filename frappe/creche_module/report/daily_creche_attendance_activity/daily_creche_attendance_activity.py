import frappe
import calendar
from frappe.utils import nowdate
from datetime import datetime, timedelta, date

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

    # filters logic for cr_opening starts here
    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None

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

    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range

        elif range_type == "before" and single_date:
            cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)

        elif range_type == "after" and single_date:
            cstart_date, cend_date = single_date + timedelta(days=1), date.today()

        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

    # filters logic for cr_opening ends here
    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None

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

    conditions = []
    conditions_att = []

    if filters_dict['selected_partner']:
        conditions.append("cr.partner_id = %(selected_partner)s")
        conditions_att.append("tca.partner_id = %(selected_partner)s")
    if filters_dict['state']:
        conditions.append("cr.state_id = %(state)s")
        conditions_att.append("tca.state_id = %(state)s")
    if filters_dict['district']:
        conditions.append("cr.district_id = %(district)s")
        conditions_att.append("tca.district_id = %(district)s")
    if filters_dict['block']:
        conditions.append("cr.block_id = %(block)s")
        conditions_att.append("tca.block_id = %(block)s")
    if filters_dict['gp']:
        conditions.append("cr.gp_id = %(gp)s")
        conditions_att.append("tca.gp_id = %(gp)s")
    if filters_dict['creche']:
        conditions.append("cr.name = %(creche)s")
        conditions_att.append("tca.creche_id = %(creche)s")
    if filters_dict['supervisor_id']:
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
    if cstart_date and cend_date:
        conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    if filters_dict['phases']:
        conditions.append("(%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))")

    if filters_dict['creche_status_id']:
        conditions.append("(%(creche_status_id)s IS NULL OR cr.creche_status_id = %(creche_status_id)s)")


    condition_str = " AND ".join(conditions) if conditions else "1=1"
    conditions_att_str = " AND ".join(conditions_att) if conditions_att else "1=1"

    
    current_date = date.today()

    # daily_columns = [
    #     f"IFNULL(catt.day_{day}, IF(DATE('{year}-{month:02d}-{day:02d}') > DATE('{current_date}'), 'N/A', 'N')) AS day_{day}"
    #     for day in range(1, last_day + 1)
    # ]
    # daily_columns_pc = [f"MAX(CASE WHEN DAY(date_of_attendance) = {day} AND is_shishu_ghar_is_closed_for_the_day = 1 THEN 'N/A' WHEN DAY(date_of_attendance) = {day} THEN 'Y' END) AS day_{day}" for day in range(1, last_day + 1)]

    daily_columns = [
        f"""
        CASE
            WHEN cr.creche_opening_date IS NULL THEN 'N/A'
            WHEN DATE('{year}-{month:02d}-{day:02d}') < cr.creche_opening_date THEN 'N/A'
            WHEN DATE('{year}-{month:02d}-{day:02d}') > DATE('{current_date}') THEN 'N/A'
            WHEN catt.day_{day} IS NULL THEN 'Not Submitted'
            WHEN catt.day_{day} = 'N/A' THEN 'Closed'
            ELSE catt.day_{day}
        END AS day_{day}
        """
        for day in range(1, last_day + 1)
    ]

    daily_columns_pc = [
        f"""
        MAX(
            CASE
                WHEN DAY(date_of_attendance) = {day} AND is_shishu_ghar_is_closed_for_the_day = 1 THEN 'Closed'
                WHEN DAY(date_of_attendance) = {day} THEN 'Open'
            END
        ) AS day_{day}
        """
        for day in range(1, last_day + 1)
    ]
    
    sql_query = f"""
    SELECT
        p.partner_name AS partner,
        s.state_name AS state,
        d.district_name AS district,
        b.block_name AS block,
        g.gp_name AS gp,
        cr.creche_name AS creche_name,
        cr.creche_id AS creche_id,
        cr.name AS creche_idx,
        DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS 'creche_opening_date',
        {", ".join(daily_columns)}
    FROM `tabCreche` cr
    LEFT JOIN (
        SELECT creche_id, {", ".join(daily_columns_pc)}
        FROM `tabChild Attendance` tca
        WHERE YEAR(date_of_attendance) = {year} 
        AND MONTH(date_of_attendance) = {month} 
        AND {conditions_att_str}
        GROUP BY creche_id
    ) AS catt ON catt.creche_id = cr.name
    JOIN `tabState` s ON cr.state_id = s.name
    JOIN `tabDistrict` d ON cr.district_id = d.name
    JOIN `tabBlock` b ON cr.block_id = b.name
    JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
    JOIN `tabVillage` v ON cr.village_id = v.name
    JOIN `tabPartner` p ON cr.partner_id = p.name
    WHERE {condition_str}
    GROUP BY p.name, s.name, d.name, b.name, g.name, v.name, cr.name
    ORDER BY p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, cr.creche_name
    """

    data = frappe.db.sql(sql_query, filters_dict, as_dict=True)
    for row in data:
        submitted_count = sum(1 for day in range(1, last_day + 1) if row.get(f"day_{day}") == "Open" or row.get(f"day_{day}") == "Closed") 
        not_submitted_count = sum(1 for day in range(1, last_day + 1) if row.get(f"day_{day}") == "Not Submitted")
        row["submitted"] = submitted_count
        row["not_submitted"] = not_submitted_count

    daily_totals = {}
    for day in range(1, last_day + 1):
        daily_totals[f"day_{day}"] = sum(1 for row in data if row.get(f"day_{day}") in ["Open", "Closed"])

    summary_row = {
        "creche_name": "<b style='color:black;'>Total</b>",
        "submitted": sum(row.get("submitted", 0) for row in data),
        "not_submitted": sum(row.get("not_submitted", 0) for row in data),
    }
    for day in range(1, last_day + 1):
        summary_row[f"day_{day}"] = daily_totals[f"day_{day}"]
    data.append(summary_row)
    return data

