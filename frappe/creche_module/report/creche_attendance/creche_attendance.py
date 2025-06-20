import frappe
from frappe.utils import nowdate
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
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
        {"label": "Eligible Children", "fieldname": "e_children", "fieldtype": "Int", "width": 200},
        {"label": "Enrolled Children", "fieldname": "enroll_children", "fieldtype": "Int", "width": 200},
        {"label": "No. of Unique Children Attended", "fieldname": "uni_children", "fieldtype": "Int", "width": 250},
        {"label": "Avg. Attendance in Creche", "fieldname": "avg_children", "fieldtype": "Int", "width": 300},
        {"label": "% of children attending the Creche vis a vis enrolment", "fieldname": "avgperenroll", "fieldtype": "Int", "width": 500},
        {"label": "% of children attending the Creche vis a vis eligible", "fieldname": "avgpereli", "fieldtype": "Int", "width": 500},
    ]
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

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    params = {}
    partner = None
    state = None
    district = None
    block = None
    gp = None
    creche = None
    supervisor_id = None

    # filters logic for cr_opening starts here
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

    if partner_id:
        partner = partner_id
    if state_id :
        state = state_id
    if filters.get("district"):
        district = filters.get('district')
    if filters.get("block"):
        block = filters.get('block')
    if filters.get("gp"):
        gp = filters.get('gp')
    if filters.get("creche"):
        creche = filters.get('creche')
    if filters.get("supervisor_id"):
        supervisor_id = filters.get('supervisor_id')

    sql_query = f"""
        SELECT tf.partner AS partner, tf.state AS state, tf.district AS district, tf.block AS block, tf.gp AS gp, tf.creche AS creche, tf.creche_id,
        tf.e_children AS e_children, 
        tf.enroll_children AS enroll_children,
        tf.uni_children AS uni_children,
        CASE WHEN tf.codays = 0 THEN 0 ELSE FORMAT(tf.ccprs / tf.codays, 2) END AS avg_children,
        CASE WHEN tf.enroll_children = 0 THEN 0 ELSE FORMAT((tf.uni_children / tf.enroll_children)*100.0, 2) END AS avgperenroll,
        CASE WHEN tf.e_children = 0 THEN 0 ELSE FORMAT((tf.uni_children / tf.e_children)*100.0, 2) END AS avgpereli
        FROM (
            SELECT p.partner_name AS partner,
                s.state_name AS state,
                d.district_name AS district,
                b.block_name AS block,
                g.gp_name AS gp,
                c.creche_name AS creche,
                c.creche_id,
                IFNULL(ec.e_children, 0) AS e_children,
                IFNULL(erc.enroll_children, 0) AS enroll_children,
                IFNULL(uc.uni_children, 0) AS uni_children,
                IFNULL(ccp.ccprs, 0) AS ccprs,
                IFNULL(cod.codays, 0) AS codays,
                IFNULL(ccup.ccuniprs, 0) AS ccuniprs
            FROM tabCreche AS c 
            JOIN tabState AS s ON c.state_id = s.name 
            LEFT JOIN (
                SELECT hf.creche_id, COUNT(hhc.hhcguid) AS e_children
                FROM `tabHousehold Child Form` AS hhc 
                JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
                WHERE (%(partner)s IS NULL OR partner_id = %(partner)s) AND hhc.is_dob_available = 1 
                AND TIMESTAMPDIFF(MONTH, hhc.child_dob, %(end_date)s) BETWEEN 6 AND 36
                GROUP BY hf.creche_id
            ) AS ec ON c.name = ec.creche_id
            LEFT JOIN (
                SELECT creche_id, COUNT(*) AS enroll_children
                FROM `tabChild Enrollment and Exit`
                WHERE (%(partner)s IS NULL OR partner_id = %(partner)s) AND is_active = 1
                AND date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit >=  %(start_date)s)
                GROUP BY creche_id
            ) AS erc ON c.name = erc.creche_id
            LEFT JOIN (
                SELECT tcc.creche_id, COUNT(DISTINCT tcc.hhcguid) AS uni_children
                FROM `tabChild Attendance List` AS cal
                JOIN `tabChild Attendance` AS ca ON ca.name = cal.parent
                JOIN `tabChild Enrollment and Exit` AS tcc ON tcc.childenrollguid = cal.childenrolledguid
                WHERE (%(partner)s IS NULL OR ca.partner_id = %(partner)s) AND cal.attendance = 1
                and tcc.is_active = 1 and tcc.is_exited = 0 
                AND ca.is_shishu_ghar_is_closed_for_the_day = 0 
                AND cal.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
                GROUP BY tcc.creche_id
            ) AS uc ON c.name = uc.creche_id
            LEFT JOIN (
                SELECT ca.creche_id, COUNT(cal.name) AS ccprs
                FROM `tabChild Attendance List` AS cal
                JOIN `tabChild Attendance` AS ca ON ca.name = cal.parent
                WHERE (%(partner)s IS NULL OR ca.partner_id = %(partner)s) AND cal.attendance = 1 
                AND ca.is_shishu_ghar_is_closed_for_the_day = 0 
                AND cal.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
                
                GROUP BY ca.creche_id
            ) AS ccp ON c.name = ccp.creche_id
            LEFT JOIN (
                SELECT ca.creche_id, COUNT(ca.name) AS codays
                FROM `tabChild Attendance` AS ca
                WHERE (%(partner)s IS NULL OR ca.partner_id = %(partner)s) AND ca.is_shishu_ghar_is_closed_for_the_day = 0 
                AND ca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
                
                GROUP BY ca.creche_id
            ) AS cod ON c.name = cod.creche_id
            LEFT JOIN (
                SELECT ca.creche_id, COUNT(DISTINCT tcc.hhcguid) AS ccuniprs
                FROM `tabChild Attendance List` AS cal
                JOIN `tabChild Attendance` AS ca ON ca.name = cal.parent
                JOIN `tabChild Enrollment and Exit` AS tcc ON tcc.childenrollguid = cal.childenrolledguid
                WHERE (%(partner)s IS NULL OR ca.partner_id = %(partner)s) AND cal.attendance = 1 
                AND ca.is_shishu_ghar_is_closed_for_the_day = 0 
                and tcc.is_active = 1 and tcc.is_exited = 0
                AND cal.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
                GROUP BY ca.creche_id
            ) AS ccup ON c.name = ccup.creche_id
            JOIN tabDistrict AS d ON c.district_id = d.name
            
            JOIN tabBlock AS b ON c.block_id = b.name
            JOIN `tabGram Panchayat` AS g ON c.gp_id = g.name
            JOIN tabPartner AS p ON c.partner_id = p.name 
            WHERE 
                (%(partner)s IS NULL OR p.name = %(partner)s)
                AND (%(state)s IS NULL OR s.name = %(state)s)
                AND (%(district)s IS NULL OR d.name = %(district)s)
                AND (%(block)s IS NULL OR b.name = %(block)s)
                AND (%(gp)s IS NULL OR g.name = %(gp)s)
                AND (%(creche)s IS NULL OR c.name = %(creche)s)
                AND (%(supervisor_id)s IS NULL OR c.supervisor_id = %(supervisor_id)s)
                AND (%(creche_status_id)s IS NULL OR c.creche_status_id = %(creche_status_id)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(c.phase, %(phases)s))
                AND (
                    (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                    OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
                )
            GROUP BY p.name, s.name, d.name, b.name, g.name, c.supervisor_id, c.name
    
            ORDER BY p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, c.supervisor_id, c.creche_name
        ) AS tf;


"""

    params.update({
        "start_date": start_date,
        "end_date": end_date,
        "partner": partner,
        'state': state,
        "district": district,
        "block": block,
        "gp": gp,
        "creche": creche,
        "supervisor_id":supervisor_id,
        "creche_status_id":creche_status_id,
        "phases": phases_cleaned,
        "month": month,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "year": year,

    })
    data = frappe.db.sql(sql_query, params, as_dict=True)
    return data
