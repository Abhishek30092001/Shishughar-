import frappe
from frappe.utils import nowdate
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
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 150},  
        
    ]
    
    # Dynamic columns for each day of the month
    month = int(filters.get("month") if filters else nowdate().split('-')[1])
    year = int(filters.get("year") if filters else nowdate().split('-')[0])

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    for day in range(1, last_day + 1):
        day_str_lbl = f"{day:02d}-{month:02d}-{year}"
        day_str = f"{day:02d}_{month:02d}_{year}"
        columns.append({
            "label": f"{day_str_lbl}",
            "fieldname": f"D_{day_str}",
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
        conditions.append(f"att.partner_id = '{partner_id}'")
    if state_id:
        conditions.append(f"att.state_id = '{state_id}'")
    if filters.get("district"):
        conditions.append(f"att.district_id = '{filters.get('district')}'")
    if filters.get("block"):
        conditions.append(f"att.block_id = '{filters.get('block')}'")
    if filters.get("gp"):
        conditions.append(f"att.gp_id = '{filters.get('gp')}'")
    if filters.get("creche"):
        conditions.append(f"att.creche_id = '{filters.get('creche')}'")
    if filters.get("supervisor_id"):
        conditions.append(f"cr.supervisor_id = '{filters.get('supervisor_id')}'")


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
        conditions.append(f"cr.creche_opening_date BETWEEN '{cstart_date}' AND '{cend_date}'")
    if creche_status_id:
        conditions.append(f"cr.creche_status_id = '{creche_status_id}'")
    if phases_cleaned:
        conditions.append(f"cr.phase IN ({phases_cleaned})")


    condition_str = " AND ".join(conditions) if conditions else '1=1'


     # Construct 1
    daily_atten_cols = []
    for day in range(1, last_day + 1):
        day_str = f"{day:02d}_{month:02d}_{year}"
        daily_atten_cols.append(f"""matt.D_{day_str}""")
    daily_atten_cols_str = ", ".join(daily_atten_cols)

     # Construct 2
    daily_atten_cols_cond = []
    for day in range(1, last_day + 1):
        day_str = f"{day:02d}_{month:02d}_{year}"
        daily_atten_cols_cond.append(f"""MAX(CASE WHEN DAY(scatt.date_of_attendance) ='{day}'THEN CASE WHEN scal.attendance = 1 THEN 'P' ELSE 'A' END END) AS D_{day_str}""")
    daily_atten_cols_cond_str = ", ".join(daily_atten_cols_cond)

    sql_query = f"""
            SELECT
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            cr.creche_name AS creche,
            cr.creche_id,
            att.child_name AS child_name,
            {daily_atten_cols_str}
        FROM
            `tabChild Enrollment and Exit` AS att
         LEFT JOIN (SELECT scatt.creche_id,scal.childenrolledguid, {daily_atten_cols_cond_str} FROM `tabChild Attendance List` AS scal JOIN  `tabChild Attendance` AS scatt ON scatt.name = scal.parent 
WHERE  YEAR(scatt.date_of_attendance) = {year} AND MONTH(scatt.date_of_attendance) =  {month}
AND scatt.is_shishu_ghar_is_closed_for_the_day = 0 GROUP BY scatt.creche_id, scal.childenrolledguid
) AS matt ON matt.childenrolledguid = att.childenrollguid
        JOIN
            `tabCreche` AS cr ON att.creche_id = cr.name
        JOIN
            `tabState` AS s ON cr.state_id = s.name
        JOIN
            `tabDistrict` AS d ON cr.district_id = d.name
        JOIN
            `tabBlock` AS b ON cr.block_id = b.name
        JOIN
            `tabGram Panchayat` AS g ON cr.gp_id = g.name
        JOIN
            `tabPartner` AS p ON att.partner_id = p.name
        WHERE
            {condition_str}
            and att.is_active = 1 and att.date_of_enrollment <='{end_date}'  and (att.date_of_exit IS NULL OR att.date_of_exit >= '{start_date}')
        ORDER BY
            p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, cr.creche_name, att.child_name
    """
    data = frappe.db.sql(sql_query, as_dict=True)
    return data
