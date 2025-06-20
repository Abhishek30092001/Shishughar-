import frappe
from frappe.utils import nowdate
from datetime import datetime, timedelta
import calendar
from datetime import date

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
        {"label": "Creche ID", "fieldname": "crecheid", "fieldtype": "Data", "width": 120},
        {"label": "No. of Creche Committee Meetings", "fieldname": "ccm", "fieldtype": "Int", "width": 300},
        {"label": "Avg. no. of parents attended", "fieldname": "avgpa", "fieldtype": "Int", "width": 300},
        {"label": "AWW", "fieldname": "aww", "fieldtype": "Int", "width": 120},
        {"label": "ASHA", "fieldname": "asha", "fieldtype": "Int", "width": 120},
        {"label": "ANM", "fieldname": "anm", "fieldtype": "Int", "width": 120},
        {"label": "PRI", "fieldname": "pri", "fieldtype": "Int", "width": 120},
        {"label": "Creche Supervisor", "fieldname": "cs", "fieldtype": "Int", "width": 200},
        {"label": "Organization's Senior Team", "fieldname": "ost", "fieldtype": "Int", "width": 300},
        {"label": "Others", "fieldname": "oth", "fieldtype": "Int", "width": 120},
    ]
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}

    # Initialize parameters dictionary
    params = {}

    # Get user session data
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
    
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s 
        ORDER BY ts.state_name
    """
    current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
    state_id = filters.get("state") or (current_user_state[0]['state_id'] if current_user_state else None)

    # Date handling
    month = int(filters.get("month")) if filters.get("month") else None
    year = int(filters.get("year")) if filters.get("year") else None
    
    if month and year:
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        params.update({
            "start_date": start_date,
            "end_date": end_date
        })
    else:
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        if start_date and end_date:
            params.update({
                "start_date": start_date,
                "end_date": end_date
            })

    # Creche opening date filter
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
    conditions = []
    
    # Location filters
    if partner_id:
        conditions.append("att.partner_id = %(partner_id)s")
        params["partner_id"] = partner_id
        
    if state_id:
        conditions.append("att.state_id = %(state_id)s")
        params["state_id"] = state_id
        
    location_fields = ["district", "block", "gp", "creche"]
    for field in location_fields:
        if filters.get(field):
            conditions.append(f"att.{field}_id = %({field}_id)s")
            params[f"{field}_id"] = filters.get(field)

    # Other filters
    if supervisor_id := filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = supervisor_id
        
    if month:
        conditions.append("MONTH(att.meeting_date) = %(month)s")
        params["month"] = month
        
    if year:
        conditions.append("YEAR(att.meeting_date) = %(year)s")
        params["year"] = year
        
    if phases := filters.get("phases"):
        phases_cleaned = [p.strip() for p in phases.split(",") if p.strip().isdigit()]
        if phases_cleaned:
            conditions.append("c.phase IN %(phases)s")
            params["phases"] = phases_cleaned
            
    if creche_status_id := filters.get("creche_status_id"):
        conditions.append("c.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = creche_status_id
        
    if "cstart_date" in params and "cend_date" in params:
        conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")

    condition_str = " AND ".join(conditions) if conditions else "1=1"
    where_clause = f"WHERE {condition_str}"

    # Build attendee subqueries
    attendee_columns = []
    for i, col in enumerate(['aww', 'asha', 'anm', 'pri', 'oth', 'cs', 'ost'], start=1):
        attendee_columns.append(f"""
            (SELECT COUNT(act.name) 
             FROM `tabAttendees child table` AS act 
             JOIN `tabCreche Committee Meeting` AS at ON at.name = act.parent 
             WHERE act.attendees_table = {i} 
             AND at.creche_id = att.creche_id 
             AND at.meeting_date BETWEEN %(start_date)s AND %(end_date)s
            ) AS {col}
        """)

    sql_query = f"""
        SELECT
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            c.creche_name AS creche,
            c.creche_id AS crecheid,
            COUNT(att.name) AS ccm,
            AVG(att.no_of_parents_attended) AS avgpa,
            {', '.join(attendee_columns)}
        FROM
            `tabCreche Committee Meeting` AS att
        JOIN
            `tabCreche` AS c ON att.creche_id = c.name
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
        {where_clause}
        GROUP BY
            p.partner_name, s.state_name, d.district_name, 
            b.block_name, g.gp_name, c.creche_name, c.creche_id
        ORDER BY
            p.partner_name, s.state_name, d.district_name, 
            b.block_name, g.gp_name, c.creche_name
    """

    data = frappe.db.sql(sql_query, params, as_dict=True)
    return data