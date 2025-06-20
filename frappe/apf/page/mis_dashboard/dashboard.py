from datetime import date
import frappe
import calendar



@frappe.whitelist(allow_guest=True)
def dashboard_section_one(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s ORDER BY ts.state_name """
    state_params = str(frappe.session.user)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_id = state_id or (current_user_state[0]['state_id'] if current_user_state else None)
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = creche_id or None  


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
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
    }
    
    query = """
SELECT 
    FR.creche_no AS "No. of creches", 
    CASE WHEN FR.creche_no = 0 THEN 0 ELSE CEIL(FR.no_days_creche_opened / FR.creche_no) END AS "Avg. no. of days creche opened",
    CASE WHEN FR.no_days_creche_opened = 0 THEN 0 ELSE CEIL(FR.no_children_present_creche_opened / FR.no_days_creche_opened) END AS "Avg. attendance per day"
FROM (
    SELECT 
        -- Count of Active Creches
        (SELECT COUNT(*)
         FROM `tabCreche` tc
         WHERE tc.is_active = 1
           AND creche_opening_date <=  %(end_date)s
           AND (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR tc.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR tc.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR tc.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR tc.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
        ) AS creche_no,

        -- Count of Days Creche Opened
        (SELECT COUNT(*)
         FROM `tabChild Attendance` ca
         WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
           AND YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR ca.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR ca.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR ca.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR ca.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
        ) AS no_days_creche_opened,

        -- Total Attendance when Creche Opened @time
        (SELECT COUNT(cal.name)
         FROM `tabChild Attendance List` cal
         JOIN `tabChild Attendance` ca ON ca.name = cal.parent
         WHERE cal.attendance = 1
           AND ca.is_shishu_ghar_is_closed_for_the_day = 0
           AND YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR ca.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR ca.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR ca.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR ca.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
        ) AS no_children_present_creche_opened
) FR;


    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {

    "Col0":[
        "No. of creches",
    ],
    "Col1": [
        "Avg. no. of days creche opened",
        "Avg. attendance per day",
    ]
}

    transformed_data = {
        section: [
        {"title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data

@frappe.whitelist(allow_guest=True)
def dashboard_section_one2(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s ORDER BY ts.state_name """
    state_params = str(frappe.session.user)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_id = state_id or (current_user_state[0]['state_id'] if current_user_state else None)
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = creche_id or None  


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
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
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
         WHERE tc.is_active = 1
           AND (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR tc.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR tc.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR tc.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR tc.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
        ) AS creche_no,
        
        -- Maximum Attendance in a Day @time p2 start
        (SELECT MAX(daily_attendance) 
         FROM (
            SELECT COUNT(cal.name) AS daily_attendance
            FROM `tabChild Attendance` ca
            JOIN `tabChild Attendance List` cal ON ca.name = cal.parent
            WHERE cal.attendance = 1
              AND ca.is_shishu_ghar_is_closed_for_the_day = 0
              AND YEAR(ca.date_of_attendance) = %(year)s
              AND MONTH(ca.date_of_attendance) = %(month)s
              AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
              AND (%(state_id)s IS NULL OR ca.state_id = %(state_id)s)
              AND (%(district_id)s IS NULL OR ca.district_id = %(district_id)s)
              AND (%(block_id)s IS NULL OR ca.block_id = %(block_id)s)
              AND (%(gp_id)s IS NULL OR ca.gp_id = %(gp_id)s)
              AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            GROUP BY ca.date_of_attendance
         ) AS daily_data
        ) AS Max_Attendance_in_a_Day,

        -- Count of Days Attendance Submitted
        (SELECT COUNT(*)
         FROM `tabChild Attendance` ca
         WHERE YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR ca.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR ca.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR ca.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR ca.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
        ) AS No_of_days_creche_attendance_submitted,

        -- Total Anthropometric Data Submitted
        (SELECT COUNT(*)
         FROM `tabChild Growth Monitoring` cgm
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
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
        {"title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data

@frappe.whitelist(allow_guest=True)
def dashboard_section_two(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None):
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
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s ORDER BY ts.state_name """
    state_params = str(frappe.session.user)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_id = state_id or (current_user_state[0]['state_id'] if current_user_state else None)
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None

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
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
    }

    query = """
    SELECT 
        FR.current_enrolled_children AS "Current enrolled children",
        FR.cur_eligible_children AS "Current eligible children",
        FR.Total_Current_exit_children AS "Current exit children",
        FR.cumm_enrolled_children AS "Cumulative enrolled children",
        FR.Total_Cumulative_exit_children AS "Cumulative exit children"
    FROM (
        SELECT 
            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` AS cees
             WHERE cees.is_active = 1 
               AND YEAR(cees.date_of_enrollment) = %(year)s  
               AND MONTH(cees.date_of_enrollment) = %(month)s 
               AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
               AND (%(state_id)s IS NULL OR cees.state_id = %(state_id)s)       
               AND (%(district_id)s IS NULL OR cees.district_id = %(district_id)s) 
               AND (%(block_id)s IS NULL OR cees.block_id = %(block_id)s)        
               AND (%(gp_id)s IS NULL OR cees.gp_id = %(gp_id)s)                
               AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s))   
            AS current_enrolled_children,

            (SELECT COUNT(hhc.name)
             FROM `tabHousehold Child Form` AS hhc 
             JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
             WHERE hhc.is_dob_available = 1 
               AND TIMESTAMPDIFF(MONTH, hhc.child_dob, %(end_date)s) BETWEEN 6 AND 36
               AND (%(partner_id)s IS NULL OR hf.partner_id = %(partner_id)s)
               AND (%(state_id)s IS NULL OR hf.state_id = %(state_id)s)
               AND (%(district_id)s IS NULL OR hf.district_id = %(district_id)s)
               AND (%(block_id)s IS NULL OR hf.block_id = %(block_id)s)
               AND (%(gp_id)s IS NULL OR hf.gp_id = %(gp_id)s)
               AND (%(creche_id)s IS NULL OR hf.creche_id = %(creche_id)s)) 
            AS cur_eligible_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` cec 
             WHERE is_active = 0 
               AND is_exited = 1 
               AND YEAR(date_of_exit) = %(year)s  
               AND MONTH(date_of_exit) = %(month)s  
               AND (%(partner_id)s IS NULL OR cec.partner_id = %(partner_id)s)  
               AND (%(state_id)s IS NULL OR cec.state_id = %(state_id)s)  
               AND (%(district_id)s IS NULL OR cec.district_id = %(district_id)s)  
               AND (%(block_id)s IS NULL OR cec.block_id = %(block_id)s)  
               AND (%(gp_id)s IS NULL OR cec.gp_id = %(gp_id)s) 
               AND (%(creche_id)s IS NULL OR cec.creche_id = %(creche_id)s)) 
            AS Total_Current_exit_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` AS cee
             WHERE 
               cee.date_of_enrollment <= %(end_date)s 
               AND (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s) 
               AND (%(state_id)s IS NULL OR cee.state_id = %(state_id)s)       
               AND (%(district_id)s IS NULL OR cee.district_id = %(district_id)s) 
               AND (%(block_id)s IS NULL OR cee.block_id = %(block_id)s)       
               AND (%(gp_id)s IS NULL OR cee.gp_id = %(gp_id)s)               
               AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)) 
            AS cumm_enrolled_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` cmec  
             WHERE is_active = 0
               AND is_exited = 1  
               AND date_of_exit <= %(end_date)s  
               AND (%(partner_id)s IS NULL OR cmec.partner_id = %(partner_id)s)  
               AND (%(state_id)s IS NULL OR cmec.state_id = %(state_id)s)  
               AND (%(district_id)s IS NULL OR cmec.district_id = %(district_id)s)  
               AND (%(block_id)s IS NULL OR cmec.block_id = %(block_id)s)  
               AND (%(gp_id)s IS NULL OR cmec.gp_id = %(gp_id)s)  
               AND (%(creche_id)s IS NULL OR cmec.creche_id = %(creche_id)s))
            AS Total_Cumulative_exit_children
    ) AS FR
    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {
        "Col2": [
            "Current enrolled children",
            "Current eligible children",
            "Current exit children",
            "Cumulative enrolled children",
            "Cumulative exit children",
        ]
    }

    transformed_data = {
        section: [
            {"title": field, "value": result.get(field, "")} for field in fields
        ]
        for section, fields in sections.items()
    }

    frappe.response["data"] = transformed_data


@frappe.whitelist(allow_guest=True)
def dashboard_section_three(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s ORDER BY ts.state_name """
    state_params = str(frappe.session.user)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_id = state_id or (current_user_state[0]['state_id'] if current_user_state else None)
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = creche_id or None  


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
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
    }
    

    query = """
SELECT
    FR.Total_Underweight_children AS "Underweight children",
    FR.Total_MAM_children AS "MAM children",
    FR.Total_Stunted_children AS "Stunted children",
    FR.Total_GF1 AS "Growth faltering 1"
FROM (
    -- "Total Underweight Children"
    SELECT 
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_age = 2
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        ) AS Total_Underweight_children,

    -- "Total MAM Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_height = 2
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        ) AS Total_MAM_children,

    -- "Total Stunted Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.height_for_age = 2
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        ) AS Total_Stunted_children,

    -- "Growth Faltering 1"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         WHERE ad.do_you_have_height_weight = 1
           AND YEAR(ad.measurement_taken_date) = %(year)s
           AND MONTH(ad.measurement_taken_date) = %(month)s
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND EXISTS (
               SELECT 1
               FROM `tabAnthropromatic Data` AS ad_same
               WHERE ad_same.childenrollguid = ad.childenrollguid
                 AND ad_same.do_you_have_height_weight = 1
                 AND YEAR(ad_same.measurement_taken_date) = %(lyear)s
                 AND MONTH(ad_same.measurement_taken_date) = %(lmonth)s
                 AND ad.weight <= ad_same.weight
           )
        ) AS Total_GF1
) AS FR;

"""

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {
    "Col3": [
        "Underweight children",
        "MAM children",
        "Stunted children",
        "Growth faltering 1",
    ]
}

    transformed_data = {
        section: [
        {"title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data

@frappe.whitelist(allow_guest=True)
def dashboard_section_four(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s ORDER BY ts.state_name """
    state_params = str(frappe.session.user)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_id = state_id or (current_user_state[0]['state_id'] if current_user_state else None)
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = creche_id or None  


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
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
    }
    

    query = """
SELECT 
    FR.Total_Severely_underweight_children AS "Severely underweight children",
    FR.Total_SAM_children AS "SAM children",
    FR.Total_Severely_stunted_children AS "Severely stunted children",
    FR.Total_GF2 AS "Growth faltering 2"
FROM (
    SELECT 
        -- "Total Severely Underweight Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_age = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        ) AS Total_Severely_underweight_children,

        -- "Total SAM Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_height = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        ) AS Total_SAM_children,

        -- "Total Severely Stunted Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND ad.do_you_have_height_weight = 1
           AND ad.height_for_age = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        ) AS Total_Severely_stunted_children,

        -- "Growth Faltering 2"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         LEFT JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         WHERE ad.do_you_have_height_weight = 1
           AND YEAR(ad.measurement_taken_date) = %(year)s
           AND MONTH(ad.measurement_taken_date) = %(month)s
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
           AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
           AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
           AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND EXISTS (
               SELECT 1
               FROM `tabAnthropromatic Data` AS ad_same
               WHERE ad_same.childenrollguid = ad.childenrollguid
                 AND ad_same.do_you_have_height_weight = 1
                 AND YEAR(ad_same.measurement_taken_date) = %(lyear)s
                 AND MONTH(ad_same.measurement_taken_date) = %(lmonth)s
                 AND ad.weight <= ad_same.weight
           )
           AND EXISTS (
               SELECT 1
               FROM `tabAnthropromatic Data` AS ad_same
               WHERE ad_same.childenrollguid = ad.childenrollguid
                 AND ad_same.do_you_have_height_weight = 1
                 AND YEAR(ad_same.measurement_taken_date) = %(pyear)s
                 AND MONTH(ad_same.measurement_taken_date) = %(plmonth)s
                 AND ad.weight <= ad_same.weight
           )
        ) AS Total_GF2
) AS FR;

    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {


    "Col4": [
        "Severely underweight children",
        "SAM children",
        "Severely stunted children",
        "Growth faltering 2",
    ]
}

    transformed_data = {
        section: [
        {"title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data




