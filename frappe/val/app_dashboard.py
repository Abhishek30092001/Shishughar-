from datetime import date
import frappe
import calendar


@frappe.whitelist(allow_guest=True)
def app_dashboard():
    user = frappe.session.user
    auth = frappe.request.headers.get('Authorization')
    data_usr = frappe.get_doc("User", user)

    if data_usr.token == auth:

        data = frappe._dict(frappe.local.form_dict)

        year = data.get("year")
        month = data.get("month")

        print(f"Received Year: {year}, Month: {month}, Type: {type(year)}, {type(month)}")  # Debugging

        current_date = date.today()
        year = int(year) if year and str(year).isdigit() else current_date.year
        month = int(month) if month and str(month).isdigit() else current_date.month

        print(f"Converted Year: {year}, Month: {month}, Type: {type(year)}, {type(month)}")
        
        creche = data.get("creche") or None

        
        if not creche:
            frappe.response["http_status_code"] = 400
            return {"status": "error", "message": "Please select a creche"}
        current_date = date.today()
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        creche = creche or None  

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
            "creche": creche,
            "lyear": lyear,
            "lmonth": lmonth,
            "plmonth": plmonth,
            "pyear": pyear
        }
        
        query = """
            SELECT 
                creche_name, 
                IFNULL(ec.e_children, 0) AS eligible_children, 
                IFNULL(cuenroll.cumulative_enrollment, 0) AS cumulative_enrollment_children, 
                ROUND(IFNULL(cuenroll.cumulative_enrollment / NULLIF(ec.e_children, 0), 0) * 100, 2) AS enroll_percent,
                CASE 
                    WHEN IFNULL(opx.eligible_open_days, 0) = 0 THEN 0
                    ELSE ROUND((IFNULL(opx.days_attended, 0) / IFNULL(opx.eligible_open_days, 0)) * 100, 2)
                END AS attendance_percentage,
                IFNULL(weight_for_age_normal, 0) AS weight_for_age_normal,
                IFNULL(weight_for_age_moderate, 0) AS weight_for_age_moderate,
                IFNULL(weight_for_age_severe, 0) AS weight_for_age_severe,
                IFNULL(weight_for_height_normal, 0) AS weight_for_height_normal,
                IFNULL(weight_for_height_moderate, 0) AS weight_for_height_moderate,
                IFNULL(weight_for_height_severe, 0) AS weight_for_height_severe,
                IFNULL(major_illness_count, 0) AS major_illness_count,
                IFNULL(gf1c.gf1, 0) AS gf1,
                IFNULL(gf2c.gf2, 0) AS gf2,
                IFNULL(rf.referred, 0) AS referred_count,
                IFNULL(nr.nrc, 0) AS nrc_count,
                IFNULL(hvdd.hvd, 0) AS home_visit_done,
                IFNULL(hvpd.hvp, 0) AS home_visit_planned

            FROM `tabCreche` AS c
            LEFT JOIN (
                        SELECT hf.creche_id, COUNT(hhc.hhcguid) AS e_children
                        FROM `tabHousehold Child Form` AS hhc 
                        JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
                        WHERE hhc.is_dob_available = 1 AND TIMESTAMPDIFF(MONTH, hhc.child_dob, %(end_date)s) BETWEEN 6 AND 36
                        GROUP BY hf.creche_id
            ) AS ec ON ec.creche_id = c.name
            LEFT JOIN (
                        SELECT creche_id, COUNT(*) AS cumulative_enrollment
                        FROM `tabChild Enrollment and Exit`
                        WHERE date_of_enrollment <= %(end_date)s
                        AND creche_id = %(creche)s
                        GROUP BY creche_id
            ) AS cuenroll ON cuenroll.creche_id = c.name    
            LEFT JOIN (
                    SELECT creche_id, SUM(days_attended) AS days_attended, SUM(eligible_open_days) AS eligible_open_days
                    FROM (
                        SELECT CAT.creche_id, CAT.childenrollguid, days_attended, eligible_open_days,  
                        CASE WHEN eligible_open_days = 0 THEN 0 ELSE (days_attended / eligible_open_days) * 100.0 END AS catt_per
                                            FROM (
                        SELECT cee.creche_id, cee.childenrollguid, chatt.days_attended, chatt.eligible_open_days  FROM `tabChild Enrollment and Exit` cee
                        LEFT JOIN (
                        SELECT cal.childenrolledguid, COUNT(CASE WHEN cal.attendance = 1 THEN 1 END) AS days_attended, COUNT(ca.date_of_attendance) AS eligible_open_days
                                                FROM `tabChild Attendance` AS ca
                                                INNER JOIN `tabChild Attendance List` AS cal 
                                                    ON cal.parent = ca.name
                                                WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
                                                AND ca.date_of_attendance >= (
                                                    SELECT MIN(cee.date_of_enrollment) 
                                                    FROM `tabChild Enrollment and Exit` AS cee 
                                                    WHERE cee.childenrollguid = cal.childenrolledguid
                                                )
                                                AND YEAR(ca.date_of_attendance) = %(year)s
                                                AND MONTH(ca.date_of_attendance) = %(month)s
                                                AND ca.creche_id = %(creche)s
                                                GROUP BY cal.childenrolledguid
                        ) AS chatt ON chatt.childenrolledguid = cee.childenrollguid 
                        WHERE cee.date_of_enrollment <= %(end_date)s and (cee.date_of_exit IS null or cee.date_of_exit >= %(start_date)s)) AS CAT) AS AttendanceData
                        GROUP BY creche_id
            ) as opx  ON opx.creche_id = c.name

            LEFT JOIN (
                    SELECT 
                        cgm.creche_id,
                        COUNT(CASE WHEN ad.weight_for_age = 3 THEN 1 END) AS weight_for_age_normal,
                        COUNT(CASE WHEN ad.weight_for_age = 2 THEN 1 END) AS weight_for_age_moderate,
                        COUNT(CASE WHEN ad.weight_for_age = 1 THEN 1 END) AS weight_for_age_severe,
                        
                        COUNT(CASE WHEN ad.weight_for_height = 3 THEN 1 END) AS weight_for_height_normal,
                        COUNT(CASE WHEN ad.weight_for_height = 2 THEN 1 END) AS weight_for_height_moderate,
                        COUNT(CASE WHEN ad.weight_for_height = 1 THEN 1 END) AS weight_for_height_severe,
                        
                        COUNT(CASE WHEN ad.any_medical_major_illness = 1 THEN 1 END) AS major_illness_count
                        
                    FROM 
                        `tabAnthropromatic Data` ad
                    LEFT JOIN 
                        `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
                    WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) = %(year)s AND MONTH(cgm.measurement_date) = %(month)s
                    AND cgm.creche_id = %(creche)s
                    GROUP BY cgm.creche_id
            ) AS gmd ON c.name = gmd.creche_id
            LEFT JOIN (
                    SELECT 
                        cr.creche_id, 
                        COUNT(*) AS nrc
                    FROM `tabChild Referral` as cr
                    WHERE cr.referred_to = 4  
                        AND cr.referred_to_nrc = 1
                        AND YEAR(cr.date_of_referral) = %(year)s 
                        AND MONTH(cr.date_of_referral) = %(month)s
                        AND cr.creche_id = %(creche)s
                    GROUP BY cr.creche_id
            ) AS nr ON c.name = nr.creche_id
            
            LEFT JOIN (
                    SELECT creche_id, COUNT(ad.name) AS gf2
                    FROM `tabAnthropromatic Data` AS ad
                    JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
                    WHERE ad.do_you_have_height_weight = 1 AND YEAR(ad.measurement_taken_date) = %(year)s
                        AND MONTH(ad.measurement_taken_date) = %(month)s
                        AND (%(creche)s IS NULL OR cgm.creche_id = %(creche)s)
                        AND EXISTS (
                            SELECT 1
                            FROM `tabAnthropromatic Data` AS ad_same
                            WHERE ad_same.childenrollguid = ad.childenrollguid AND ad_same.do_you_have_height_weight = 1 
                            AND YEAR(ad_same.measurement_taken_date) = %(lyear)s AND MONTH(ad_same.measurement_taken_date) = %(lmonth)s
                            AND ad.weight <= ad_same.weight)
                        AND EXISTS (
                            SELECT 1
                            FROM `tabAnthropromatic Data` AS ad_same
                            WHERE ad_same.childenrollguid = ad.childenrollguid AND ad_same.do_you_have_height_weight = 1 
                            AND YEAR(ad_same.measurement_taken_date) = %(pyear)s AND MONTH(ad_same.measurement_taken_date) = %(plmonth)s
                            AND ad.weight < ad_same.weight) 
            ) AS gf2c ON c.name = gf2c.creche_id

            LEFT JOIN (
                    SELECT cgm.creche_id, COUNT(ad.name) AS gf1  
                    FROM `tabAnthropromatic Data` AS ad
                    JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
                    WHERE ad.do_you_have_height_weight = 1 AND YEAR(ad.measurement_taken_date) = %(year)s AND MONTH(ad.measurement_taken_date) = %(month)s 
                    AND (%(creche)s IS NULL OR cgm.creche_id = %(creche)s)
                        AND EXISTS (
                            SELECT 1
                            FROM `tabAnthropromatic Data` AS ad_same
                            WHERE ad_same.childenrollguid = ad.childenrollguid AND ad_same.do_you_have_height_weight = 1 
                            AND YEAR(ad_same.measurement_taken_date) = %(lyear)s AND MONTH(ad_same.measurement_taken_date) = %(lmonth)s
                            AND ad.weight < ad_same.weight) 
            ) AS gf1c ON c.name = gf1c.creche_id
            
            LEFT JOIN (
                SELECT
                    crf.creche_id,
                    COUNT(DISTINCT crf.childenrolledguid) AS referred
                FROM
                    `tabChild Referral` AS crf
                WHERE
                    YEAR(crf.date_of_referral) = %(year)s
                    AND MONTH(crf.date_of_referral) = %(month)s
                    AND crf.creche_id = %(creche)s
            ) AS rf ON c.name = rf.creche_id

            LEFT JOIN (
                    SELECT  tcgm.creche_id, COUNT(ad.name) AS hvp
                    FROM  `tabAnthropromatic Data` AS ad
                    INNER JOIN `tabChild Growth Monitoring` tcgm ON ad.parent = tcgm.name 
                    WHERE YEAR(ad.measurement_taken_date) =  %(year)s AND MONTH(ad.measurement_taken_date) = %(month)s
                    AND tcgm.creche_id = %(creche)s
                    AND (ad.weight_for_age = 1 
                    OR ad.weight_for_height = 1
                    OR ad.any_medical_major_illness = 1)
                    GROUP BY tcgm.creche_id
            ) AS hvpd ON c.name = hvpd.creche_id
            LEFT JOIN (
                    SELECT cr.creche_id, COUNT(cr.name) AS hvd
                    FROM `tabChild Referral` as cr
                    INNER JOIN `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
                    WHERE date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit  >=  %(start_date)s)
                    AND YEAR(cr.date_of_referral) = %(year)s AND MONTH(cr.date_of_referral) = %(month)s
                    AND cr.creche_id = %(creche)s
                    GROUP BY cr.creche_id
            ) AS hvdd ON c.name = hvdd.creche_id
                
            WHERE %(creche)s IS NULL OR c.name = %(creche)s
        """
        data = frappe.db.sql(query, params, as_dict=True)

        if data:
            result = data[0] 
            
            formatted_data = [
                {"title": "Creche", "value": result.get("creche_name", "")},
                {"title": "Current Eligible Children", "value": result.get("eligible_children", 0)},
                {"title": "Cumulative Enrolled Children", "value": result.get("cumulative_enrollment_children", 0)},
                {"title": "Enrollment Percentage", "value": result.get("enroll_percent", 0)},
                {"title": "Attendance Percentage", "value": result.get("attendance_percentage", 0)},
                {"title": "Weight for Age Normal", "value": result.get("weight_for_age_normal", 0)},
                {"title": "Weight for Age Moderate", "value": result.get("weight_for_age_moderate", 0)},
                {"title": "Weight for Age Severe", "value": result.get("weight_for_age_severe", 0)},
                {"title": "Weight for Height Normal", "value": result.get("weight_for_height_normal", 0)},
                {"title": "Weight for Height Moderate", "value": result.get("weight_for_height_moderate", 0)},
                {"title": "Weight for Height Severe", "value": result.get("weight_for_height_severe", 0)},
                {"title": "Major Illness", "value": result.get("major_illness_count", 0)},
                {"title": "Growth Faltering 1", "value": result.get("gf1", 0)},
                {"title": "Growth Faltering 2", "value": result.get("gf2", 0)},
                {"title": "Referred", "value": result.get("referred_count", 0)},
                {"title": "NRC", "value": result.get("nrc_count", 0)},
                {"title": "Home Visits Done", "value": result.get("home_visit_done", 0)},
                {"title": "Home Visits Planned", "value": result.get("home_visit_planned", 0)},
            ]
            frappe.response["data"] = formatted_data
        else:
            frappe.response["data"] = []

    else:
        frappe.response["Error"] = "Invalid API"
        # raise frappe.AuthenticationError
