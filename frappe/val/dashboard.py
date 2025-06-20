from datetime import date
import frappe
import calendar

import hashlib

def generate_id(field):
    base_id = "".join(word[:3].lower() for word in field.split() if word.isalpha() and len(word) >= 3)
    
    unique_suffix = hashlib.md5(field.encode()).hexdigest()[:4]
    return f"{base_id}-{unique_suffix}"


@frappe.whitelist(allow_guest=True)
def dashboard_section_one(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None,supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):

    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    creche_id = creche_id or None  
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None


    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id


    if month == 1:
        lmonth = 12
        plmonth = 11
        lyear = year - 1
        pyear = year - 1
    elif month == 2:
        lmonth = 1
        plmonth = 12
        lyear = year
        pyear = year - 1
    else:
        lmonth = month - 1
        plmonth = month - 2
        lyear = year
        pyear = year

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, 
        "cend_date": cend_date,
        "c_status": c_status,
        "phases":phases
    }
    
    query = """
SELECT 
    FR.creche_no AS "No. of creches", 
    CASE WHEN FR.creche_no = 0 THEN 0 ELSE CEIL(FR.no_days_creche_opened / FR.creche_no) END AS "Avg. no. of days creche opened",
    CASE WHEN FR.no_days_creche_opened = 0 THEN 0 ELSE ROUND(FR.no_children_present_creche_opened / FR.no_days_creche_opened, 1) END AS "Avg. attendance per day",
    FR.no_children_curr_active AS "Current active children",
    FR.no_creche_attendance_submitted AS "No. of creches submitted attendance (All Days)",
    FR.measurement_data_submitted AS "Children mesurement taken"
FROM (
    SELECT 
        -- Count of Active Creches
        (SELECT COUNT(*)
         FROM `tabCreche` tc
         WHERE 
           (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND tc.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(tc.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
           AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)    
           AND (%(phases)s IS NULL OR FIND_IN_SET(tc.phase, %(phases)s))  
           AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))

        ) AS creche_no,

        -- count of creche whoose attendance submitted
        (SELECT COUNT(*) 
        FROM (
            SELECT 
                tc.name, 
                tc.creche_opening_date,  
                DATEDIFF(
                    CASE 
                        WHEN DATE_FORMAT(CURRENT_DATE(), '%%Y-%%m') = DATE_FORMAT(%(start_date)s, '%%Y-%%m') 
                        THEN CURRENT_DATE() 
                        ELSE %(end_date)s 
                    END, 
                    CASE 
                        WHEN tc.creche_opening_date < %(start_date)s 
                        THEN %(start_date)s 
                        ELSE tc.creche_opening_date 
                    END
                ) + 1 AS elgdays, 
                IFNULL(att.attdays, 0) AS attdays
            FROM 
                `tabCreche` tc 
            LEFT JOIN (
                SELECT 
                    tca.creche_id, 
                    COUNT(*) AS attdays 
                FROM 
                    `tabChild Attendance` tca 
                WHERE 
                    tca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s 
                GROUP BY 
                    tca.creche_id
            ) AS att 
            ON tc.name = att.creche_id 
            WHERE 
                tc.creche_opening_date IS NOT NULL 
                AND tc.creche_opening_date <= %(end_date)s
                AND (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
                AND (
                    (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND tc.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(tc.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )
                AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
                AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(tc.phase, %(phases)s))
                AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
                AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS creche_attendance
        WHERE elgdays <= attdays
        ) AS no_creche_attendance_submitted,


        -- Count of Days Creche Opened
        (SELECT COUNT(*)
         FROM `tabChild Attendance` ca
         JOIN `tabCreche` cr ON cr.name = ca.creche_id
         WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
           AND YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND ca.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ca.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND ca.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ca.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND ca.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ca.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND ca.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(ca.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))

        ) AS no_days_creche_opened,

        -- Total Attendance when Creche Opened @time
        (SELECT COUNT(cal.name)
         FROM `tabChild Attendance List` cal
         JOIN `tabChild Attendance` ca ON ca.name = cal.parent
         JOIN `tabCreche` cr on cr.name = ca.creche_id
         WHERE cal.attendance = 1
           AND ca.is_shishu_ghar_is_closed_for_the_day = 0
           AND YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND ca.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ca.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND ca.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ca.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND ca.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ca.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND ca.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(ca.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS no_children_present_creche_opened,

        -- currently active children
        (SELECT COUNT(*)
         FROM `tabChild Enrollment and Exit` cee
         INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
         WHERE  (cee.date_of_enrollment <=  %(end_date)s and 
           (cee.date_of_exit IS null or cee.date_of_exit > %(end_date)s))
           AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND cr.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cr.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND cr.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cr.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND cr.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cr.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND cr.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cr.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS no_children_curr_active,

        (SELECT COUNT(*)
            FROM `tabAnthropromatic Data` AS ad
            LEFT JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            LEFT JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id 
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
                AND (
                    (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
                AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
                AND (
                    (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                    OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
                )
        ) AS measurement_data_submitted

) FR;
    """
    
    data = frappe.db.sql(query, params, as_dict=True)
    result = data[0] if data else {}
    sections = {

    "Col0":[
        "No. of creches",
        "Current active children",
        "No. of creches submitted attendance (All Days)",
        "Children mesurement taken"
    ],
    "Col1": [
        "Avg. no. of days creche opened",
        "Avg. attendance per day"
    ]
}

    transformed_data = {
        section: [
        { "id": generate_id(field), "title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data


@frappe.whitelist(allow_guest=True)
def dashboard_section_one2(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None,supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    creche_id = creche_id or None  
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id


    if month == 1:
        lmonth = 12
        plmonth = 11
        lyear = year - 1
        pyear = year - 1
    elif month == 2:
        lmonth = 1
        plmonth = 12
        lyear = year
        pyear = year - 1
    else:
        lmonth = month - 1
        plmonth = month - 2
        lyear = year
        pyear = year

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status,
        "phases": phases
    }
    
    query = """
SELECT 
        FR.Max_Attendance_in_a_Day AS "Maximum attendance in a day",
        CASE WHEN FR.creche_no = 0 THEN 0 ELSE CEIL(FR.No_of_days_creche_attendance_submitted / FR.creche_no) 
        END AS "Avg. no. of days attendance submitted",
        FR.Total_Anthro_data_submitted AS "Anthro data submitted"
FROM (
    SELECT 
     -- Count of Active Creches
        (SELECT COUNT(*)
         FROM `tabCreche` tc
         WHERE 
           (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND tc.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(tc.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
           AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(tc.phase, %(phases)s))
           AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))

        ) AS creche_no,
        
        -- Maximum Attendance in a Day @time p2 start
        (SELECT MAX(daily_attendance) 
         FROM (
            SELECT COUNT(cal.name) AS daily_attendance
            FROM `tabChild Attendance` ca
            JOIN `tabChild Attendance List` cal ON ca.name = cal.parent
            JOIN `tabCreche` cr on cr.name = ca.creche_id
            WHERE cal.attendance = 1
              AND ca.is_shishu_ghar_is_closed_for_the_day = 0
              AND YEAR(ca.date_of_attendance) = %(year)s
              AND MONTH(ca.date_of_attendance) = %(month)s
              AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
                AND (
                    (%(state_id)s IS NOT NULL AND ca.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ca.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND ca.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ca.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND ca.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ca.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND ca.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(ca.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )
              AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
              AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
              AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
              AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
              AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
              AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))

            GROUP BY ca.date_of_attendance
         ) AS daily_data
        ) AS Max_Attendance_in_a_Day,

        -- Count of Days Attendance Submitted
        (SELECT COUNT(*)
         FROM `tabChild Attendance` ca
         JOIN `tabCreche` cr on cr.name = ca.creche_id
         WHERE YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND ca.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ca.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND ca.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ca.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND ca.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ca.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND ca.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(ca.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS No_of_days_creche_attendance_submitted,

        -- Total Anthropometric Data Submitted
        (SELECT COUNT(*)
         FROM `tabChild Growth Monitoring` cgm
         JOIN `tabCreche` cr on cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_Anthro_data_submitted
) FR;


    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {

    "Col1": [
        "Maximum attendance in a day",
        "Avg. no. of days attendance submitted",
        "Anthro data submitted",
    ]
}

    transformed_data = {
        section: [
        { "id": generate_id(field), "title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data

@frappe.whitelist(allow_guest=True)
def dashboard_section_two(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,supervisor_id=None, year=None, month=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    if not year or not month:
        frappe.throw("Year and Month are required and must be valid numbers.")
    
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    if month == 1:
        lmonth, plmonth, lyear, pyear = 12, 11, year - 1, year - 1
    elif month == 2:
        lmonth, plmonth, lyear, pyear = 1, 12, year, year - 1
    else:
        lmonth, plmonth, lyear, pyear = month - 1, month - 2, year, year

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id":supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status,
        "phases": phases
    }

    query = """
    SELECT 
        FR.current_enrolled_children AS "Children enrolled this month",
        FR.cur_eligible_children AS "Current eligible children",
        FR.Total_Current_exit_children AS "Children exited this month",
        FR.cumm_enrolled_children AS "Cumulative enrolled children",
        FR.Total_Cumulative_exit_children AS "Cumulative exit children"
    FROM (
        SELECT 
            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` AS cees
             JOIN `tabCreche` AS cr ON cr.name = cees.creche_id
             WHERE YEAR(cees.date_of_enrollment) = %(year)s  
               AND MONTH(cees.date_of_enrollment) = %(month)s 
               AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
               AND (
                    (%(state_id)s IS NOT NULL AND cees.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cees.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cees.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cees.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cees.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cees.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cees.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cees.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )                  
               AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)) 
            )  
            AS current_enrolled_children,

            (SELECT COUNT(hhc.name)
             FROM `tabHousehold Child Form` AS hhc 
             JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
             JOIN `tabCreche` AS cr ON cr.name = hf.creche_id
             WHERE hhc.is_dob_available = 1 
            AND (
                hhc.child_dob BETWEEN 
                    DATE_SUB(
                        IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
                            CURDATE(), 
                            %(end_date)s
                        ), 
                        INTERVAL 36 MONTH
                    )
                    AND 
                    DATE_SUB(
                        IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
                            CURDATE(), 
                            %(end_date)s
                        ), 
                        INTERVAL 6 MONTH
                    )
            )
               AND (%(partner_id)s IS NULL OR hf.partner_id = %(partner_id)s)
               AND (
                    (%(state_id)s IS NOT NULL AND hf.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(hf.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND hf.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(hf.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND hf.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(hf.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND hf.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(hf.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )   
               AND (%(creche_id)s IS NULL OR hf.creche_id = %(creche_id)s)
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )AS cur_eligible_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` cec 
             JOIN `tabCreche` AS cr ON cr.name = cec.creche_id
             WHERE YEAR(date_of_exit) = %(year)s  
               AND MONTH(date_of_exit) = %(month)s  
               AND (%(partner_id)s IS NULL OR cec.partner_id = %(partner_id)s)  
               AND (
                    (%(state_id)s IS NOT NULL AND cec.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cec.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cec.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cec.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cec.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cec.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cec.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cec.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )   
               AND (%(creche_id)s IS NULL OR cec.creche_id = %(creche_id)s)
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )AS Total_Current_exit_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` AS cee
             JOIN `tabCreche` AS cr ON cr.name = cee.creche_id
             WHERE cee.date_of_enrollment <= %(end_date)s
               AND (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s) 
               AND (
                    (%(state_id)s IS NOT NULL AND cee.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cee.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cee.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cee.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cee.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cee.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cee.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cee.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )                 
               AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )AS cumm_enrolled_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` cmec  
             JOIN `tabCreche` AS cr ON cr.name = cmec.creche_id
             WHERE date_of_exit <= %(end_date)s  
               AND (%(partner_id)s IS NULL OR cmec.partner_id = %(partner_id)s)  
               AND (
                    (%(state_id)s IS NOT NULL AND cmec.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cmec.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cmec.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cmec.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cmec.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cmec.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cmec.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cmec.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )   
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(creche_id)s IS NULL OR cmec.creche_id = %(creche_id)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )AS Total_Cumulative_exit_children
    ) AS FR
    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {
        "Col2": [
            "Children enrolled this month",
            "Current eligible children",
            "Children exited this month",
            "Cumulative enrolled children",
            "Cumulative exit children",
        ]
    }

    transformed_data = {
        section: [
            { "id": generate_id(field), "title": field, "value": result.get(field, "")} for field in fields
        ]
        for section, fields in sections.items()
    }

    frappe.response["data"] = transformed_data


@frappe.whitelist(allow_guest=True)
def dashboard_section_three(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None,supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    creche_id = creche_id or None  
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id


    if month == 1:
        lmonth = 12
        plmonth = 11
        lyear = year - 1
        pyear = year - 1
    elif month == 2:
        lmonth = 1
        plmonth = 12
        lyear = year
        pyear = year - 1
    else:
        lmonth = month - 1
        plmonth = month - 2
        lyear = year
        pyear = year

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "c_status": c_status,
        "phases": phases    
    }
    

    query = """
SELECT
    FR.Total_Underweight_children AS "Moderately underweight",
    FR.Total_MAM_children AS "Moderately wasted",
    FR.Total_Stunted_children AS "Moderately stunted",
    FR.Total_GF1 AS "Growth faltering 1"
FROM (
    -- "Total Underweight Children"
    SELECT 
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_age = 2
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_Underweight_children,

    -- "Total MAM Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id 
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_height = 2
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_MAM_children,

    -- "Total Stunted Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.height_for_age = 2
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_Stunted_children,

    -- "Growth Faltering 1"
        (SELECT COUNT(*) AS gf1  
            FROM 
                `tabAnthropromatic Data` AS ad
            INNER JOIN 
                `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN
                `tabAnthropromatic Data` AS ad_lyear ON 
                    ad_lyear.childenrollguid = ad.childenrollguid AND 
                    ad_lyear.do_you_have_height_weight = 1 AND
                    YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
                    MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
                    ad.weight <= ad_lyear.weight
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            LEFT JOIN
                `tabAnthropromatic Data` AS ad_pyear ON 
                    ad_pyear.childenrollguid = ad.childenrollguid AND 
                    ad_pyear.do_you_have_height_weight = 1 AND
                    YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
                    MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
                    ad_lyear.weight <= ad_pyear.weight
            WHERE 
                ad.do_you_have_height_weight = 1 AND 
                YEAR(cgm.measurement_date) = %(year)s AND 
                MONTH(cgm.measurement_date) = %(month)s
                AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
                AND (
                    (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
                AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
                AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                AND ad_pyear.name IS NULL
        ) AS Total_GF1

) AS FR;

"""

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {
    "Col3": [
        "Moderately underweight",
        "Moderately wasted",
        "Moderately stunted",
        "Growth faltering 1",
    ]
}

    transformed_data = {
        section: [
        {"id": generate_id(field), "title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data

@frappe.whitelist(allow_guest=True)
def dashboard_section_four(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None,supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    creche_id = creche_id or None  
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id


    if month == 1:
        lmonth = 12
        plmonth = 11
        lyear = year - 1
        pyear = year - 1
    elif month == 2:
        lmonth = 1
        plmonth = 12
        lyear = year
        pyear = year - 1
    else:
        lmonth = month - 1
        plmonth = month - 2
        lyear = year
        pyear = year

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, 
        "cend_date": cend_date,
        "c_status": c_status,
        "phases": phases
    }
    

    query = """
SELECT 
    FR.Total_Severely_underweight_children AS "Severely underweight",
    FR.Total_SAM_children AS "Severely wasted",
    FR.Total_Severely_stunted_children AS "Severely stunted",
    FR.Total_GF2 AS "Growth faltering 2"
FROM (
    SELECT 
        -- "Total Severely Underweight Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_age = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_Severely_underweight_children,

        -- "Total SAM Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_height = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_SAM_children,

        -- "Total Severely Stunted Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.height_for_age = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_Severely_stunted_children,

        -- "Growth Faltering 2"
        (SELECT COUNT(*) AS gf2
            FROM 
                `tabAnthropromatic Data` AS ad
            INNER JOIN 
                `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            INNER JOIN
                `tabAnthropromatic Data` AS ad_lyear ON 
                    ad_lyear.childenrollguid = ad.childenrollguid AND 
                    ad_lyear.do_you_have_height_weight = 1 AND
                    YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
                    MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
                    ad.weight <= ad_lyear.weight
            INNER JOIN
                `tabAnthropromatic Data` AS ad_pyear ON 
                    ad_pyear.childenrollguid = ad.childenrollguid AND 
                    ad_pyear.do_you_have_height_weight = 1 AND
                    YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
                    MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
                    ad_lyear.weight <= ad_pyear.weight
            WHERE 
                ad.do_you_have_height_weight = 1 AND 
                YEAR(cgm.measurement_date) = %(year)s AND 
                MONTH(cgm.measurement_date) = %(month)s
                AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
                AND (
                    (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
                AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
                AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_GF2
) AS FR;

    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {


    "Col4": [
        "Severely underweight",
        "Severely wasted",
        "Severely stunted",
        "Growth faltering 2",
    ]
}

    transformed_data = {
        section: [
            {
                "id": generate_id(field),
                "title": field, 
                "value": result.get(field, "")
            } 
            for field in fields
        ]
        for section, fields in sections.items()
    }


    frappe.response["data"] = transformed_data




