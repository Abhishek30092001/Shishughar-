import frappe
from frappe.utils import nowdate
from datetime import  date

def execute(filters=None):
    columns = get_columns()
    data = get_summary_data(filters)
    return columns, data

def get_columns():
    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
        {"label": "Creche Open Days", "fieldname": "creche_open", "fieldtype": "Int", "width": 120},
        {"label": "Breakfast Days", "fieldname": "breakfast_days", "fieldtype": "Int", "width": 140},
        {"label": "Lunch Days", "fieldname": "lunch_days", "fieldtype": "Int", "width": 120},
        {"label": "Egg Days", "fieldname": "egg_days", "fieldtype": "Int", "width": 120},
        {"label": "Evening Snacks Days", "fieldname": "evening_snacks_days", "fieldtype": "Int", "width": 180},
        {"label": "Two-time Snacks and One Meal", "fieldname": "two", "fieldtype": "Data", "width": 250},
    ]
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):

    district = filters.get("district") if filters else None
    block = filters.get("block") if filters else None
    gp = filters.get("gp") if filters else None
    creche = filters.get("creche") if filters else None
    supervisor_id = filters.get("supervisor_id") if filters else None
    month = filters.get("month") if filters else None
    year = filters.get("year") if filters else None

    # Default to current month and year if not provided
    if not month:
        month = nowdate().split('-')[1]
    if not year:
        year = nowdate().split('-')[0]

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

    # filters logic for cr_opening ends here
    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None

    # Build query conditions based on filters
    conditions = []
    if partner_id:
        conditions.append(f"AND c.partner_id = '{partner_id}'")
    if state_id:
        conditions.append(f"AND c.state_id = '{state_id}'")
    if district:
        conditions.append(f"AND c.district_id = '{district}'")
    if block:
        conditions.append(f"AND c.block_id = '{block}'")
    if gp:
        conditions.append(f"AND c.gp_id = '{gp}'")
    if creche:
        conditions.append(f"AND c.name = '{creche}'")
    if supervisor_id:
        conditions.append(f"AND c.supervisor_id = '{supervisor_id}'")
    if creche_status_id:
        conditions.append(f"AND c.creche_status_id = '{creche_status_id}'")
    if phases_cleaned:
        conditions.append(f"AND c.phase = '{phases_cleaned}'")
    if cstart_date and cend_date:
        conditions.append(f"c.creche_opening_date BETWEEN '{cstart_date}' AND '{cend_date}'")
   
    condition_str = " ".join(conditions)

    # SQL query
    sql_query = f"""
        SELECT
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            c.creche_name AS creche,
            c.creche_id,
            IFNULL(att.creche_open,0) AS creche_open,
            IFNULL(att.breakfast_days,0) AS breakfast_days,
            IFNULL(att.lunch_days,0) AS lunch_days,
            IFNULL(att.egg_days,0) AS egg_days,
            IFNULL(att.evening_snacks_days,0) AS evening_snacks_days,
            IFNULL(att.two,'No') AS two
        FROM `tabCreche` AS c 
        LEFT JOIN (SELECT creche_id, COUNT(CASE WHEN is_shishu_ghar_is_closed_for_the_day = 0 THEN att.name END) AS creche_open,
            COUNT(CASE WHEN att.breakfast > 0 THEN att.date_of_attendance END) AS breakfast_days,
            COUNT(CASE WHEN att.lunch > 0 THEN att.date_of_attendance END) AS lunch_days,
            COUNT(CASE WHEN att.egg > 0 THEN att.date_of_attendance END) AS egg_days,
            COUNT(CASE WHEN att.evening_snacks > 0 THEN att.date_of_attendance END) AS evening_snacks_days,
            CASE 
                WHEN COUNT(CASE WHEN att.breakfast > 0 THEN att.date_of_attendance END) > 0
                     AND COUNT(CASE WHEN att.lunch > 0 THEN att.date_of_attendance END) > 0
                     AND COUNT(CASE WHEN att.evening_snacks > 0 THEN att.date_of_attendance END) > 0
                THEN 'Yes' 
                ELSE 'No' 
            END AS two
        FROM
            `tabChild Attendance` AS att WHERE YEAR(att.date_of_attendance)={year} AND MONTH(att.date_of_attendance)= {month}
            GROUP BY creche_id ) AS att ON att.creche_id = c.name
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
            1=1
            {condition_str}
        GROUP BY
            p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, c.creche_name
        ORDER BY
            p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, c.creche_name
    """

    data = frappe.db.sql(sql_query, as_dict=True)
    return data
