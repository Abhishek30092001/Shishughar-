import frappe
from frappe.utils import nowdate
from frappe import _
from datetime import datetime, timedelta, date
import calendar

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
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": "Creche Open Time", "fieldname": "open_time", "fieldtype": "Time", "width": 200},
        {"label": "Creche Close Time", "fieldname": "close_time", "fieldtype": "Time", "width": 200},
        {"label": "ECD Activity Done", "fieldname": "ecd_activity_done", "fieldtype": "Data", "width": 200},
        {"label": "Enrolled Children", "fieldname": "ce_children", "fieldtype": "Data", "width": 200},
        {"label": "Children Present", "fieldname": "c_present", "fieldtype": "Data", "width": 200},
        {"label": "Breakfast", "fieldname": "breakfast", "fieldtype": "Int", "width": 100},
        {"label": "Lunch", "fieldname": "lunch", "fieldtype": "Int", "width": 100},
        {"label": "Egg", "fieldname": "egg", "fieldtype": "Int", "width": 100},
        {"label": "Evening Snacks", "fieldname": "evening_snacks", "fieldtype": "Int", "width": 200},
    ]
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    month_name = filters.get("month")
    month = list(calendar.month_name).index(month_name) if month_name else None
    year = int(filters.get("year")) if filters.get("year") else None

    if not (month and year):
        frappe.throw(_("Month and Year are required"))

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
    
    # Get user's geography mapping
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    
    state_ids = [s["state_id"] for s in current_user_state if s.get("state_id")]
    district_ids = [s["district_id"] for s in current_user_state if s.get("district_id")]
    block_ids = [s["block_id"] for s in current_user_state if s.get("block_id")]
    gp_ids = [s["gp_id"] for s in current_user_state if s.get("gp_id")]

    # Date range handling
    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type")
    
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range") or []

        if single_date and isinstance(single_date, str):
            try:
                single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            except ValueError:
                single_date = None
            
        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range[0], date_range[1]

        elif range_type == "before" and single_date:
            cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)

        elif range_type == "after" and single_date:
            cstart_date, cend_date = single_date + timedelta(days=1), date.today()

        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

    creche_status_id = filters.get("creche_status_id")
    phases = filters.get("phases")
    phases_cleaned = None
    
    if phases:
        phases_cleaned = ",".join([p.strip() for p in phases.split(",") if p.strip().isdigit()])

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "partner": partner_id,
        "state": filters.get("state"),
        "district": filters.get("district"),
        "block": filters.get("block"),
        "gp": filters.get("gp"),
        "creche": filters.get("creche"),
        "supervisor_id": filters.get("supervisor_id"),
        "creche_status_id": creche_status_id,
        "phases": phases_cleaned,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
    }

    conditions = []
    conditions_lj = []

    if partner_id:
        conditions.append("c.partner_id = %(partner)s")
        conditions_lj.append("tca.partner_id = %(partner)s")
    
    # For State filter
    if filters.get("state"):
        conditions.append("c.state_id = %(state)s")
        conditions_lj.append("tca.state_id = %(state)s")
        params["state"] = filters.get("state")
        params["state_ids"] = None  # Clear the alternative parameter
    else:
        if state_ids:
            conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
            conditions_lj.append("FIND_IN_SET(tca.state_id, %(state_ids)s)")
            params["state_ids"] = ",".join(state_ids) if isinstance(state_ids, list) else state_ids
            params["state"] = None  # Clear the alternative parameter

    # For District filter
    if filters.get("district"):
        conditions.append("c.district_id = %(district)s")
        conditions_lj.append("tca.district_id = %(district)s")
        params["district"] = filters.get("district")
        params["district_ids"] = None
    else:
        if district_ids:
            conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
            conditions_lj.append("FIND_IN_SET(tca.district_id, %(district_ids)s)")
            params["district_ids"] = ",".join(district_ids) if isinstance(district_ids, list) else district_ids
            params["district"] = None

    # For Block filter
    if filters.get("block"):
        conditions.append("c.block_id = %(block)s")
        conditions_lj.append("tca.block_id = %(block)s")
        params["block"] = filters.get("block")
        params["block_ids"] = None
    else:
        if block_ids:
            conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
            conditions_lj.append("FIND_IN_SET(tca.block_id, %(block_ids)s)")
            params["block_ids"] = ",".join(block_ids) if isinstance(block_ids, list) else block_ids
            params["block"] = None

    # For GP filter
    if filters.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
        conditions_lj.append("tca.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
        params["gp_ids"] = None
    else:
        if gp_ids:
            conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
            conditions_lj.append("FIND_IN_SET(tca.gp_id, %(gp_ids)s)")
            params["gp_ids"] = ",".join(gp_ids) if isinstance(gp_ids, list) else gp_ids
            params["gp"] = None

    if filters.get("creche"):
        conditions.append("c.name = %(creche)s")
    
    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
    
    if creche_status_id:
        conditions.append("c.creche_status_id = %(creche_status_id)s")
    
    if phases_cleaned:
        conditions.append("c.phase IN (%(phases)s)")
    
    if cstart_date and cend_date:
        conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")

    if start_date and end_date:
        frappe.msgprint(start_date,end_date)
        conditions.append("att.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s")
        conditions_lj.append("tca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s")

    condition_str = " AND ".join(conditions) if conditions else "1=1"
    where_clause = f"WHERE {condition_str}"

    condition_str_lj = " AND ".join(conditions_lj) if conditions_lj else "1=1"
    where_clause_lj = f"WHERE {condition_str_lj}"

    sql_query = f"""
        SELECT 
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            c.creche_name AS creche,
            c.creche_id,
            att.date_of_attendance AS date, 
            att.open_time, 
            att.close_time, 
            CASE 
                WHEN att.isecd_activities_done_for_the_day = 1 THEN 'Yes' 
                WHEN att.isecd_activities_done_for_the_day = 0 THEN 'No' 
                ELSE NULL 
            END AS ecd_activity_done, 
            IFNULL(cee.ce_children, 0) AS ce_children,
            IFNULL(catt.c_present, 0) AS c_present,
            att.breakfast AS breakfast,    
            att.lunch AS lunch,
            att.egg AS egg,
            att.evening_snacks AS evening_snacks
        FROM
            `tabCreche` AS c
        LEFT JOIN `tabChild Attendance` AS att 
            ON att.creche_id = c.name 
        LEFT JOIN (
            SELECT creche_id, COUNT(*) AS ce_children 
            FROM `tabChild Enrollment and Exit` 
            WHERE is_active = 1 AND is_exited = 0 
            GROUP BY creche_id
        ) AS cee 
            ON cee.creche_id = c.name 
        LEFT JOIN (
            SELECT 
                tca.creche_id, 
                tca.date_of_attendance, 
                SUM(CASE WHEN tcal.attendance = 1 THEN 1 ELSE 0 END) AS c_present 
            FROM `tabChild Attendance List` tcal 
            JOIN `tabChild Attendance` tca ON tcal.parent = tca.name 
            {where_clause_lj}  
            GROUP BY tca.creche_id, tca.date_of_attendance
        ) AS catt 
            ON att.creche_id = catt.creche_id AND att.date_of_attendance = catt.date_of_attendance
        JOIN `tabState` AS s ON c.state_id = s.name
        JOIN `tabDistrict` AS d ON c.district_id = d.name
        JOIN `tabBlock` AS b ON c.block_id = b.name
        JOIN `tabGram Panchayat` AS g ON c.gp_id = g.name
        JOIN `tabPartner` AS p ON c.partner_id = p.name
        {where_clause}
        ORDER BY
            p.partner_name, s.state_name, d.district_name, b.block_name, 
            g.gp_name, c.creche_name, att.date_of_attendance
    """

    data = frappe.db.sql(sql_query, params, as_dict=True)
    
    
    return data