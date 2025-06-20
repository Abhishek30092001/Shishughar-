from datetime import date
import frappe
import calendar



@frappe.whitelist(allow_guest=True)
def dashboard_section_one(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, village_id=None,creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None):
    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
    year = int(year)
    month = int(month)
    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

    # current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    # partner_id = partner_id or current_user_partner
    # state_query = """ 
    #     SELECT state_id, district_id, block_id, gp_id
    #     FROM `tabUser Geography Mapping`
    #     WHERE parent = %s
    #     ORDER BY state_id, district_id, block_id, gp_id
    # """
    # current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    # state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    # district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    # block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    # gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]

    # user = frappe.session.user
    # user_type = frappe.db.get_value("User", user, "type")
    # if user_type == "Creche Supervisor":
    #     supervisor_id = user
    # return supervisor_id

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
        
    if creche_id:
        supervisor_id = None

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": None,
        "district_id": district_id,
        "district_ids":  None,
        "block_id": block_id,
        "block_ids":None,
        "gp_id": gp_id,
        "gp_ids": None,
        "creche_id": creche_id,
        "village_id": village_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, 
        "cend_date": cend_date
    }

    # Main query with NULL handling
    query = """
    SELECT 
        IFNULL(FR.creche_no, 0) AS "No. of creches", 
        CASE 
            WHEN FR.creche_no = 0 OR FR.creche_no IS NULL THEN 0 
            ELSE CEIL(IFNULL(FR.no_days_creche_opened, 0) / FR.creche_no) 
        END AS "Avg. no. of days creche opened",
        CASE 
            WHEN FR.no_days_creche_opened = 0 OR FR.no_days_creche_opened IS NULL THEN 0 
            ELSE ROUND(IFNULL(FR.no_children_present_creche_opened, 0) / FR.no_days_creche_opened, 1) 
        END AS "Avg. attendance per day",
        IFNULL(FR.no_children_curr_active, 0) AS "Current active children",
        IFNULL(FR.no_creche_attendance_submitted, 0) AS "No. of creches submitted attendance (All Days)",
        FR.measurement_data_submitted AS "No. of Children mesurement taken",
        FR.Max_Attendance_in_a_Day AS "Maximum attendance in a day",
        CASE WHEN FR.creche_no = 0 THEN 0 ELSE CEIL(FR.No_of_days_creche_attendance_submitted / FR.creche_no) 
        END AS "Avg. no. of days attendance submitted",
        FR.Total_Anthro_data_submitted AS "Anthro data submitted",
        FR.current_enrolled_children AS "Children enrolled this month",
        FR.cur_eligible_children AS "Current eligible children",
        FR.Total_Current_exit_children AS "Children exited this month",
        FR.cumm_enrolled_children AS "Cumulative enrolled children",
        FR.Total_Cumulative_exit_children AS "Cumulative exit children",
        FR.Total_Underweight_children AS "Moderately underweight",
        FR.Total_MAM_children AS "Moderately wasted",
        FR.Total_Stunted_children AS "Moderately stunted",
        FR.Total_Severely_underweight_children AS "Severely underweight",
        FR.Total_SAM_children AS "Severely wasted",
        FR.Total_Severely_stunted_children AS "Severely stunted",
        FR.Total_GF1 AS "Growth faltering 1",
        FR.Total_GF2 AS "Growth faltering 2"
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
            AND (%(village_id)s IS NULL OR tc.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
            AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))             
            ) AS creche_no,

            -- Count of creches whose attendance submitted for all days
            (SELECT COUNT(DISTINCT ca.creche_id) 
            FROM `tabChild Attendance` AS ca
            INNER JOIN `tabCreche` AS cr ON ca.creche_id = cr.name
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
            AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            
            AND ca.creche_id IN (
                SELECT ca2.creche_id
                FROM `tabChild Attendance` AS ca2
                WHERE YEAR(ca2.date_of_attendance) = %(year)s
                AND MONTH(ca2.date_of_attendance) = %(month)s
                GROUP BY ca2.creche_id
                HAVING COUNT(DISTINCT ca2.date_of_attendance) = 
                    CASE 
                        WHEN %(year)s = YEAR(CURDATE()) AND %(month)s = MONTH(CURDATE()) 
                            THEN DAY(CURDATE())
                        ELSE DAY(LAST_DAY(CONCAT(%(year)s, '-', %(month)s, '-01')))
                    END
            )
            ) AS no_creche_attendance_submitted,

            -- Count of Days Creche Opened
            (SELECT IFNULL(COUNT(*), 0)
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
            AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS no_days_creche_opened,

            -- Total Attendance when Creche Opened
            (SELECT IFNULL(COUNT(cal.name), 0)
            FROM `tabChild Attendance List` cal
            JOIN `tabChild Attendance` ca ON ca.name = cal.parent
            JOIN `tabCreche` cr ON cr.name = ca.creche_id
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
            AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS no_children_present_creche_opened,

            -- Currently active children
            (SELECT COUNT(*)
            FROM `tabChild Enrollment and Exit` cee
            INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
            WHERE (cee.date_of_enrollment <= %(end_date)s 
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(end_date)s))
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
            AND (%(village_id)s IS NULL OR cee.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS no_children_curr_active,
            
            -- Maximum Attendance in a Day @time p2 start
            IFNULL((
                SELECT MAX(daily_attendance) 
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
                    AND (%(state_id)s IS NULL OR ca.state_id = %(state_id)s)
                    AND (%(district_id)s IS NULL OR ca.district_id = %(district_id)s)
                    AND (%(block_id)s IS NULL OR ca.block_id = %(block_id)s)
                    AND (%(gp_id)s IS NULL OR ca.gp_id = %(gp_id)s)
                    AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
                    AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
                    AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                    
                    AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
                    GROUP BY ca.date_of_attendance
                ) AS daily_data
            ), 0) AS Max_Attendance_in_a_Day,


            -- Count of Days Attendance Submitted
            (SELECT COUNT(*)
            FROM `tabChild Attendance` ca
            JOIN `tabCreche` cr on cr.name = ca.creche_id
            WHERE YEAR(ca.date_of_attendance) = %(year)s
            AND MONTH(ca.date_of_attendance) = %(month)s
            AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
            AND (%(state_id)s IS NULL OR ca.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR ca.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR ca.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR ca.gp_id = %(gp_id)s)
            AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS No_of_days_creche_attendance_submitted,

            -- Total Anthropometric Data Submitted
            (SELECT COUNT(*)
            FROM `tabChild Growth Monitoring` cgm
            JOIN `tabCreche` cr on cr.name = cgm.creche_id
            WHERE YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_Anthro_data_submitted,

            (SELECT COUNT(*) 
            FROM `tabChild Enrollment and Exit` AS cees
            JOIN `tabCreche` AS cr ON cr.name = cees.creche_id
            WHERE YEAR(cees.date_of_enrollment) = %(year)s  
            AND MONTH(cees.date_of_enrollment) = %(month)s 
            AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
            AND (%(state_id)s IS NULL OR cees.state_id = %(state_id)s)       
            AND (%(district_id)s IS NULL OR cees.district_id = %(district_id)s) 
            AND (%(block_id)s IS NULL OR cees.block_id = %(block_id)s)        
            AND (%(gp_id)s IS NULL OR cees.gp_id = %(gp_id)s) 
            AND (%(village_id)s IS NULL OR cees.village_id = %(village_id)s)               
            AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS current_enrolled_children,

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
            AND (%(state_id)s IS NULL OR hf.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR hf.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR hf.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR hf.gp_id = %(gp_id)s)
            AND (%(village_id)s IS NULL OR hf.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR hf.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS cur_eligible_children,

            (SELECT COUNT(*) 
            FROM `tabChild Enrollment and Exit` cec 
            JOIN `tabCreche` AS cr ON cr.name = cec.creche_id
            WHERE YEAR(date_of_exit) = %(year)s  
            AND MONTH(date_of_exit) = %(month)s  
            AND (%(partner_id)s IS NULL OR cec.partner_id = %(partner_id)s)  
            AND (%(state_id)s IS NULL OR cec.state_id = %(state_id)s)  
            AND (%(district_id)s IS NULL OR cec.district_id = %(district_id)s)  
            AND (%(block_id)s IS NULL OR cec.block_id = %(block_id)s)  
            AND (%(gp_id)s IS NULL OR cec.gp_id = %(gp_id)s) 
            AND (%(village_id)s IS NULL OR cec.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cec.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_Current_exit_children,

            (SELECT COUNT(*) 
            FROM `tabChild Enrollment and Exit` AS cee
            JOIN `tabCreche` AS cr ON cr.name = cee.creche_id
            WHERE cee.date_of_enrollment <= %(end_date)s
            AND (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s) 
            AND (%(state_id)s IS NULL OR cee.state_id = %(state_id)s)       
            AND (%(district_id)s IS NULL OR cee.district_id = %(district_id)s) 
            AND (%(block_id)s IS NULL OR cee.block_id = %(block_id)s)       
            AND (%(gp_id)s IS NULL OR cee.gp_id = %(gp_id)s)               
            AND (%(village_id)s IS NULL OR cee.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS cumm_enrolled_children,

            (SELECT COUNT(*) 
            FROM `tabChild Enrollment and Exit` cmec  
            JOIN `tabCreche` AS cr ON cr.name = cmec.creche_id
            WHERE date_of_exit <= %(end_date)s  
            AND (%(partner_id)s IS NULL OR cmec.partner_id = %(partner_id)s)  
            AND (%(state_id)s IS NULL OR cmec.state_id = %(state_id)s)  
            AND (%(district_id)s IS NULL OR cmec.district_id = %(district_id)s)  
            AND (%(block_id)s IS NULL OR cmec.block_id = %(block_id)s)  
            AND (%(gp_id)s IS NULL OR cmec.gp_id = %(gp_id)s)  
            AND (%(village_id)s IS NULL OR cmec.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cmec.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_Cumulative_exit_children,

            (SELECT COUNT(ad.name)
            FROM `tabAnthropromatic Data` AS ad
            JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            WHERE YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND ad.do_you_have_height_weight = 1
            AND ad.weight_for_age = 2
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
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
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
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
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
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
                AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                
                AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
                AND ad_pyear.name IS NULL
        ) AS Total_GF1,

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
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
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
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
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
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
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
                AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                
                AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        ) AS Total_GF2,


        (SELECT COUNT(*)
            FROM `tabAnthropromatic Data` AS ad
            LEFT JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            LEFT JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id 
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
                AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
                AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
                AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
                AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
                AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                
                AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        ) AS measurement_data_submitted

    ) FR;
        """
    
    transformed_data = frappe.db.sql(query, params, as_dict=True)

    query_status_mapping = {
        "Current active children": "active_children",
        "Children enrolled this month": "enrolled_children_this_month",
        "Current eligible children": "current_eligible_children",
        "Children exited this month": "exited_children_this_month",
        "Moderately underweight": "moderately_underweight",
        "Moderately wasted": "moderately_wasted",
        "Moderately stunted": "moderately_stunted",
        "Growth faltering 1": "gf1",
        "Severely underweight": "severly_underweight",
        "Severely wasted": "severly_wasted",
        "Severely stunted": "severly_stunted",
        "Growth faltering 2": "gf2",
        "No. of creches submitted attendance (All Days)": "no_creche_attendance_submitted",
        "Anthro data submitted" : "anthro_data_submitted",
        "No. of Children mesurement taken" : "measurement_data_submitted",
        "No. of creches" : "no_of_creches",
    }

    if transformed_data:
        flat_data = transformed_data[0]
        formatted_data = []

        for idx, key in enumerate(flat_data):
            item = {
                "ID": idx + 1,
                "title": key,
                "value": flat_data[key]
            }
            if key in query_status_mapping:
                item["query_status"] = query_status_mapping[key]
            formatted_data.append(item)

        frappe.response["data"] = formatted_data
    else:
        frappe.response["data"] = {"data": []}



