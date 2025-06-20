import frappe
from frappe.utils import nowdate
from datetime import date
import calendar

def execute(filters=None):
    columns = get_columns(filters)
    data = get_enrollment_data(filters)
    
    # Add index numbers to each row
    for idx, row in enumerate(data, start=1):
        row['idx'] = idx
        
    return columns, data

def get_columns(filters):
    selected_year = int(filters.get("year")) if filters.get("year") else int(nowdate().split('-')[0])
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "crecheid", "fieldtype": "Data", "width": 120}
    ]

    # Add month columns
    for month in months:
        month_label = f"{month[:3]}-{selected_year}"
        columns.append({
            "label": month_label, 
            "fieldname": month.lower(), 
            "fieldtype": "Int", 
            "width": 120
        })

    return columns

@frappe.whitelist()
def get_enrollment_data(filters=None):
    if not filters:
        filters = {}
    
    conditions = []
    params = {
        "year": int(filters.get("year")) if filters.get("year") else int(nowdate().split('-')[0])
    }
    
    # Get current user's partner and state
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
    
    # Date range filter for creche opening dates
    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type") if filters else None

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

    if cstart_date is not None and cend_date is not None:
        conditions.append("""
            (
                (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                OR (creche.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
            )
        """)
        params.update({
            "cstart_date": cstart_date,
            "cend_date": cend_date
        })

    # # Age group filter
    # if filters.get("age_group"):
    #     age_group = int(filters.get('age_group'))
    #     if age_group == 1:
    #         conditions.append("TIMESTAMPDIFF(MONTH, cp.child_dob, cp.date_of_exit) BETWEEN 0 AND 12")
    #     elif age_group == 2:
    #         conditions.append("TIMESTAMPDIFF(MONTH, cp.child_dob, cp.date_of_exit) BETWEEN 13 AND 24")
    #     elif age_group == 3:
    #         conditions.append("TIMESTAMPDIFF(MONTH, cp.child_dob, cp.date_of_exit) BETWEEN 25 AND 36")
    
    # Location filters
    if partner_id:
        conditions.append("creche.partner_id = %(partner_id)s")
        params["partner_id"] = partner_id
        
    if state_id:
        conditions.append("creche.state_id = %(state_id)s")
        params["state_id"] = state_id
        
    location_fields = ["district", "block", "gp", "creche"]
    for field in location_fields:
        if filters.get(field):
            conditions.append(f"creche.{field}_id = %({field}_id)s")
            params[f"{field}_id"] = filters.get(field)

    # Other filters
    if filters.get("type"):
        conditions.append("cp.reason_for_exit = %(exit_type)s")
        params["exit_type"] = filters.get("type")
        
    if filters.get("supervisor_id"):
        conditions.append("creche.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")
        
    if filters.get("creche_status_id"):
        conditions.append("creche.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = filters.get("creche_status_id")
        
    if filters.get("phases"):
        phases_cleaned = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
        if phases_cleaned:
            conditions.append("creche.phase IN %(phases)s")
            params["phases"] = phases_cleaned

    conditions_sql = " AND ".join(conditions) if conditions else "1=1"

    sql_query = """
        SELECT
            partner.partner_name AS partner,
            state.state_name AS state,
            district.district_name AS district,
            block.block_name AS block,
            gp.gp_name AS gp,
            creche.creche_name AS creche,
            creche.creche_id AS crecheid,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 1 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS january,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 2 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS february,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 3 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS march,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 4 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS april,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 5 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS may,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 6 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS june,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 7 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS july,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 8 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS august,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 9 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS september,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 10 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS october,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 11 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS november,
            COUNT(DISTINCT IF(MONTH(cp.date_of_exit) = 12 AND YEAR(cp.date_of_exit) = %(year)s, cp.hhcguid, NULL)) AS december
        FROM
            `tabChild Enrollment and Exit` AS cp
        LEFT JOIN
            `tabCreche` AS creche ON cp.creche_id = creche.name
        LEFT JOIN
            `tabPartner` AS partner ON partner.name = creche.partner_id
        LEFT JOIN
            `tabState` AS state ON state.name = creche.state_id
        LEFT JOIN
            `tabDistrict` AS district ON district.name = creche.district_id
        LEFT JOIN
            `tabBlock` AS block ON block.name = creche.block_id
        LEFT JOIN
            `tabGram Panchayat` AS gp ON gp.name = creche.gp_id
        WHERE
            {conditions_sql} 
        GROUP BY
            partner.name, state.name, district.name, block.name, gp.name, creche.supervisor_id, creche.name
        ORDER BY
            partner.partner_name, state.state_name, district.district_name, 
            block.block_name, gp.gp_name, creche.supervisor_id ,creche.creche_name
    """.format(conditions_sql=conditions_sql)

    data = frappe.db.sql(sql_query, params, as_dict=True)
    return data