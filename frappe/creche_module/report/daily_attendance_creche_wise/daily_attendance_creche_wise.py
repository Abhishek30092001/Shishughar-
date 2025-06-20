import frappe
from frappe.utils import nowdate
import calendar
from datetime import datetime
import calendar
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
        {"label": "No.of Creches", "fieldname": "crecheN", "fieldtype": "Data", "width": 120},
    ]
    
    # Dynamic columns for each day of the month
    month = int(filters.get("month") if filters else nowdate().split('-')[1])
    year = int(filters.get("year") if filters else nowdate().split('-')[0])
    last_day = calendar.monthrange(year, month)[1]
    
    for day in range(1, last_day + 1):
        day_str = f"{day:02d}-{month:02d}-{year}"
        columns.append({
            "label": f"{day_str}",
            "fieldname": f"day_{day}",
            "fieldtype": "Data",
            "width": 200
        })    
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s 
        ORDER BY ts.state_name
    """
    
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_id = filters.get("state") or (current_user_state[0]['state_id'] if current_user_state else None)

    
    month = int(filters.get("month") if filters else nowdate().split('-')[1])
    year = int(filters.get("year") if filters else nowdate().split('-')[0])
    # creche = int(filters.get("creche"))

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    conditions = []

    if partner_id:
        conditions.append(f"cr.partner_id = '{partner_id}'")
    if state_id:
        conditions.append(f"cr.state_id = '{state_id}'")
    if filters.get("district"):
        conditions.append(f"cr.district_id = '{filters.get('district')}'")
    if filters.get("block"):
        conditions.append(f"cr.block_id = '{filters.get('block')}'")
    if filters.get("gp"):
        conditions.append(f"cr.gp_id = '{filters.get('gp')}'")
    if filters.get("creche"):
        conditions.append(f"cr.creche_id = '{filters.get('creche')}'")

    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None
    
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
    
    if cstart_date and cend_date:
        conditions.append(f"cr.creche_opening_date BETWEEN '{cstart_date}' AND '{cend_date}'")
    if creche_status_id:
        conditions.append(f"cr.creche_status_id = '{creche_status_id}'")
    if phases_cleaned:
        conditions.append(f"cr.phase IN ({phases_cleaned})")


    condition_str = " AND ".join(conditions) if conditions else '1=1'

    # Generate dynamic columns for each day
    daily_columns = []
    daily_columns_count = []
    for day in range(1, last_day + 1):
        day_str = f"{year}-{month:02d}-{day:02d}"
        daily_columns.append(f"""CONCAT(CASE WHEN COUNT(*) = 0 THEN 0 ELSE FORMAT((IFNULL(batt.day_{day},0)/COUNT(*))*100,2) END,'% (', IFNULL(batt.day_{day},0),')') AS day_{day}""")
        daily_columns_count.append(f"""COUNT(CASE WHEN DAY(catt.date_of_attendance) = {day} THEN 1 END) AS day_{day}""")
        daily_columns_str = ", ".join(daily_columns)
        daily_columns_count_str = ", ".join(daily_columns_count)

    sql_query = f"""
        SELECT p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            COUNT(*) AS crecheN,
            {daily_columns_str}
         FROM
            `tabCreche` AS cr
        LEFT JOIN (SELECT catt.partner_id, catt.block_id, {daily_columns_count_str}
		FROM `tabChild Attendance` catt	
        WHERE YEAR(catt.date_of_attendance) = {year}  AND MONTH(catt.date_of_attendance) = {month}
		GROUP BY catt.partner_id, catt.block_id) AS batt ON cr.block_id = batt.block_id AND cr.partner_id = batt.partner_id
        JOIN
            `tabState` AS s ON cr.state_id = s.name
        JOIN
            `tabDistrict` AS d ON cr.district_id = d.name
        JOIN
            `tabBlock` AS b ON cr.block_id = b.name
        JOIN
            `tabGram Panchayat` AS g ON cr.gp_id = g.name
        JOIN
            `tabPartner` AS p ON cr.partner_id = p.name
        WHERE
            {condition_str}
        GROUP BY
            cr.partner_id, cr.state_id, cr.district_id, cr.block_id
        ORDER BY p.partner_name, s.state_name, d.district_name, b.block_name
    """
    
    data = frappe.db.sql(sql_query, as_dict=True)
    return data
