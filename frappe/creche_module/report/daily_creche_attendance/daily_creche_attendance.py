import frappe
from frappe.utils import nowdate
import calendar
from datetime import date

def execute(filters=None):
    columns = get_columns(filters)
    data = get_summary_data(filters)
    return columns, data

def get_columns(filters):
    # Basic columns for the report
    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Village", "fieldname": "village", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
    ]
    
    # Add dynamic columns for each day of the month
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
        conditions.append(f"c.partner_id = '{partner_id}'")
    if state_id:
        conditions.append(f"c.state_id = '{state_id}'")
    if filters.get("district"):
        conditions.append(f"c.district_id = '{filters.get('district')}'")
    if filters.get("block"):
        conditions.append(f"c.block_id = '{filters.get('block')}'")
    if filters.get("gp"):
        conditions.append(f"c.gp_id = '{filters.get('gp')}'")
    if filters.get("creche"):
        conditions.append(f"c.creche_id = '{filters.get('creche')}'")
    if filters.get("supervisor_id"):
        conditions.append(f"c.supervisor_id = '{filters.get('supervisor_id')}'")


    #   Filtering logic for creche opening
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
        conditions.append(f"c.creche_opening_date BETWEEN '{cstart_date}' AND '{cend_date}'")
    if creche_status_id:
        conditions.append(f"c.creche_status_id = '{creche_status_id}'")
    if phases_cleaned:
        conditions.append(f"c.phase IN ({phases_cleaned})")



    condition_str = " AND ".join(conditions) if conditions else '1=1'

    # Construct SQL query to get attendance counts for each day
    daily_columns = []
    daily_columns_tc = []
    daily_columns_pc = []

    for day in range(1, last_day + 1):
        daily_columns.append(
            f"""CONCAT(CASE WHEN IFNULL(catd.tc_{day}, 0) = 0 THEN 0 ELSE FORMAT((IFNULL(catd.pc_{day}, 0) / catd.tc_{day}) * 100, 2) END, '%% (', IFNULL(catd.pc_{day}, 0), ')') AS day_{day}"""
        )
        daily_columns_tc.append(
            f"""SUM(CASE WHEN DAY(catt.date_of_attendance) = {day} THEN 1 ELSE 0 END) AS tc_{day}"""
        )
        daily_columns_pc.append(
            f"""SUM(CASE WHEN DAY(catt.date_of_attendance) = {day} THEN cal.attendance ELSE 0 END) AS pc_{day}"""
        )

    daily_columns_str = ", ".join(daily_columns)
    daily_columns_tc_str = ", ".join(daily_columns_tc)
    daily_columns_pc_str = ", ".join(daily_columns_pc)

    # Construct the final SQL query
    sql_query = f"""
        SELECT
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            v.village_name AS village,
            c.creche_name AS creche,
            c.creche_id,
            {daily_columns_str}
        FROM
            `tabCreche` AS c
        LEFT JOIN (
            SELECT catt.creche_id, {daily_columns_tc_str}, {daily_columns_pc_str}
            FROM `tabChild Attendance` catt
            INNER JOIN `tabChild Attendance List` cal ON catt.name = cal.parent
            WHERE YEAR(catt.date_of_attendance) = {year} AND MONTH(catt.date_of_attendance) = {month}
            GROUP BY catt.creche_id
        ) AS catd ON catd.creche_id = c.name
        JOIN `tabState` AS s ON c.state_id = s.name
        JOIN `tabDistrict` AS d ON c.district_id = d.name
        JOIN `tabBlock` AS b ON c.block_id = b.name
        JOIN `tabGram Panchayat` AS g ON c.gp_id = g.name
        JOIN `tabVillage` AS v ON c.village_id = v.name
        JOIN `tabPartner` AS p ON c.partner_id = p.name
        WHERE {condition_str}
        GROUP BY
            c.partner_id, c.state_id, c.district_id, c.block_id, c.gp_id, c.village_id, c.name
        ORDER BY
            p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, v.village_name, c.creche_name
    """
    
    data = frappe.db.sql(sql_query, as_dict=True)
    return data