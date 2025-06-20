import frappe
from frappe.utils import nowdate
import calendar
from datetime import datetime, timedelta, date

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
        {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 200},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 200},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
        {"label": "Date of Birth", "fieldname": "child_dob", "fieldtype": "Data", "width": 150},
        {"label": "Age (At enrollment)", "fieldname": "age", "fieldtype": "Data", "width": 180},
        {"label": "Current Age", "fieldname": "current_age", "fieldtype": "Data", "width": 150},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
        {"label": "Height (cm)", "fieldname": "height", "fieldtype": "Data", "width": 130},
        {"label": "Weight (kg)", "fieldname": "weight", "fieldtype": "Data", "width": 130},
        {"label": "Measurement Date", "fieldname": "measurements_taken_date", "fieldtype": "Data", "width": 200},
        {"label": "Measurement Taken", "fieldname": "measurements_taken", "fieldtype": "Data", "width": 180},

        {"label": "Weight for Age", "fieldname": "weight_for_age_status", "fieldtype": "Data", "width": 150},
        {"label": "Weight for Height", "fieldname": "weight_for_height_status", "fieldtype": "Data", "width": 150},
        {"label": "Height for Age", "fieldname": "height_for_age_status", "fieldtype": "Data", "width": 150},

        # {"label": "Attendance Percentage", "fieldname": "attendance_percentage", "fieldtype": "Data", "width": 240},
        {"label": "Growth Faltering 1", "fieldname": "growth_faltering_1", "fieldtype": "Data", "width": 160 , "align": "center"},
        {"label": "Growth Faltering 2", "fieldname": "growth_faltering_2", "fieldtype": "Data", "width": 160, "align": "center"},
        {"label": "Medical Complication ", "fieldname": "any_medical_major_illness", "fieldtype": "Data", "width": 170, "align": "center"},

        {"label": "Red Flag", "fieldname": "red_flag", "fieldtype": "Data", "width": 100, "align": "center"},
        {"label": "Home Visit", "fieldname": "red_flag_HV", "fieldtype": "Data", "width": 100, "align": "center"},
        {"label": "Followup", "fieldname": "follow_up", "fieldtype": "Data", "width": 120},
        {"label": "Taken to VHND", "fieldname": "vhsnd", "fieldtype": "Data", "width": 140},
        {"label": "Taken to PHC", "fieldname": "phc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to CHC", "fieldname": "chc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to other Health Facility", "fieldname": "othr", "fieldtype": "Data", "width": 250}
        
    ]
    
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    month = int(filters.get("month") if filters else nowdate().split('-')[1])
    year = int(filters.get("year") if filters else nowdate().split('-')[0])
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner = filters.get("partner") or current_user_partner
    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
   
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s 
        ORDER BY ts.state_name
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state = filters.get("state") or (current_user_state[0]['state_id'] if current_user_state else None)
    district = filters.get("district") if filters else None
    block = filters.get("block") if filters else None
    gp = filters.get("gp") if filters else None
    creche = filters.get("creche") if filters else None
    supervisor_id = filters.get("supervisor_id") if filters else None

    partner = None if not partner else partner
    state = None if not state else state

    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None

    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range

        elif range_type == "before" and single_date:
            cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)

        elif range_type == "after" and single_date:
            cstart_date, cend_date = single_date + timedelta(days=1), date.today()

        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

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
        "start_date": start_date,
        "end_date": end_date,
        "partner": partner,
        "state": state,
        "district": district,
        "block": block,
        "gp": gp,
        "creche": creche,
        "supervisor_id": supervisor_id,
        "year": year,
        "month": month,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "phases": phases_cleaned,
        "creche_status_id": creche_status_id
    }

    sql_query = """
            SELECT DISTINCT
                cr.creche_name AS 'creche_name',
                usr.full_name AS 'supervisor',
                cee.child_id AS 'child_id',
                cr.creche_id AS 'creche_id',
                cee.child_name AS 'child_name',
                cee.age_at_enrollment_in_months AS 'age',
                DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS 'child_dob',
                TIMESTAMPDIFF(MONTH, cee.child_dob, CURDATE()) AS current_age,
                (CASE 
                    WHEN cee.gender_id = '1' THEN 'M' 
                    WHEN cee.gender_id = '2' THEN 'F' 
                    ELSE cee.gender_id 
                END) AS gender,
                ad.height AS 'height',
                ad.weight AS 'weight',
                IF(ad.do_you_have_height_weight = 1, 'Y', 'N') AS 'measurements_taken',
                IFNULL(DATE_FORMAT(ad.measurement_taken_date, '%%d-%%m-%%Y'), '-') AS 'measurements_taken_date',
                
                CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
                    CASE WHEN ad.childenrollguid IN (
                            SELECT 
                                ad_current.childenrollguid 
                            FROM 
                                `tabAnthropromatic Data` AS ad_current
                            INNER JOIN 
                                `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
                            INNER JOIN
                                `tabAnthropromatic Data` AS ad_lyear ON 
                                    ad_lyear.childenrollguid = ad_current.childenrollguid AND 
                                    ad_lyear.do_you_have_height_weight = 1 AND
                                    YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
                                    MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
                                    ad_current.weight <= ad_lyear.weight
                            LEFT JOIN
                                `tabAnthropromatic Data` AS ad_pyear ON 
                                    ad_pyear.childenrollguid = ad_current.childenrollguid AND 
                                    ad_pyear.do_you_have_height_weight = 1 AND
                                    YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
                                    MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
                                    ad_lyear.weight <= ad_pyear.weight
                            WHERE 
                                ad_current.do_you_have_height_weight = 1 AND 
                                YEAR(cgm.measurement_date) = %(year)s AND 
                                MONTH(cgm.measurement_date) = %(month)s AND
                                ad_pyear.name IS NULL
                        ) THEN 'Y'
                        ELSE 'N' 
                    END 
                END AS 'growth_faltering_1',

                CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
                    CASE WHEN ad.childenrollguid IN (
                            SELECT 
                                ad_current.childenrollguid 
                            FROM 
                                `tabAnthropromatic Data` AS ad_current
                            INNER JOIN 
                                `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
                            INNER JOIN
                                `tabAnthropromatic Data` AS ad_lyear ON 
                                    ad_lyear.childenrollguid = ad_current.childenrollguid AND 
                                    ad_lyear.do_you_have_height_weight = 1 AND
                                    YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
                                    MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
                                    ad_current.weight <= ad_lyear.weight
                            INNER JOIN
                                `tabAnthropromatic Data` AS ad_pyear ON 
                                    ad_pyear.childenrollguid = ad_current.childenrollguid AND 
                                    ad_pyear.do_you_have_height_weight = 1 AND
                                    YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
                                    MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
                                    ad_lyear.weight <= ad_pyear.weight
                            WHERE ad_current.do_you_have_height_weight = 1  
                            AND YEAR(ad_current.measurement_taken_date) = %(year)s
                            AND MONTH(ad_current.measurement_taken_date) = %(month)s
                        ) THEN 'Y'
                        ELSE 'N'
                    END 
                END AS 'growth_faltering_2',
                p.partner_name AS partner,
                s.state_name AS state,
                d.district_name AS district,
                b.block_name AS block,
                g.gp_name AS gp,
                cfud.follow_up AS follow_up,
                ad.any_medical_major_illness AS any_medical_major_illness,
                CASE 
                    WHEN crfd.date_of_referral IS NOT NULL
                    THEN 'Y' 
                    ELSE '-' 
                END AS red_flag_HV,
                IFNULL(
                    CASE 
                        WHEN crfd.referred_to = 5
                        THEN 'Y' 
                        ELSE '-' 
                    END, '-'
                ) AS othr,
                CASE 
                    WHEN crfd.referred_to = 4 
                    THEN 'Y' 
                    ELSE '-' 
                END AS nrc, 
                CASE 
                    WHEN crfd.referred_to = 3 
                    THEN 'Y' 
                    ELSE '-' 
                END AS chc, 
                CASE 
                    WHEN crfd.referred_to = 2
                    THEN 'Y' 
                    ELSE '-' 
                END AS phc,
                CASE 
                    WHEN crfd.referred_to = 1 
                    THEN 'Y' 
                    ELSE '-' 
                END AS vhsnd, 

                CASE 
                    WHEN (ad.weight_for_age = 1 
                        OR ad.weight_for_height = 1
                        OR ad.any_medical_major_illness = 1)
                    THEN 'Y' 
                    ELSE 'N' 
                END AS red_flag,

                -- Weight for Age
                CASE 
                    WHEN ad.weight_for_age = 3 THEN 'Normal'
                    WHEN ad.weight_for_age = 2 THEN 'Moderate'
                    WHEN ad.weight_for_age = 1 THEN 'Severe'
                    ELSE '' 
                END AS weight_for_age_status,
                
                -- Height for Age
                CASE 
                    WHEN ad.height = 0 THEN '-'
                    WHEN ad.height_for_age = 3 THEN 'Normal'
                    WHEN ad.height_for_age = 2 THEN 'Moderate'
                    WHEN ad.height_for_age = 1 THEN 'Severe'
                    ELSE '' 
                END AS height_for_age_status,
                
                -- Weight for Height
                CASE 
                    WHEN ad.height = 0 THEN '-'
                    WHEN ad.weight_for_height = 3 THEN 'Normal'
                    WHEN ad.weight_for_height = 2 THEN 'Moderate'
                    WHEN ad.weight_for_height = 1 THEN 'Severe'
                    ELSE '' 
                END AS weight_for_height_status
            FROM  
                `tabAnthropromatic Data` AS ad 
            INNER JOIN 
                `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
            INNER JOIN 
                `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid 
            INNER JOIN 
                `tabCreche` AS cr ON cgm.creche_id = cr.name 
            INNER JOIN 
                `tabUser` AS usr ON cr.supervisor_id = usr.name 
            INNER JOIN 
                `tabPartner` AS p ON p.name = cr.partner_id
            INNER JOIN 
                `tabState` AS s ON s.name = cr.state_id
            INNER JOIN 
                `tabDistrict` AS d ON d.name = cr.district_id
            INNER JOIN 
                `tabBlock` AS b ON b.name = cr.block_id
            INNER JOIN 
                `tabGram Panchayat` AS g ON g.name = cr.gp_id
            LEFT JOIN (
                SELECT
                    crf.childenrolledguid,
                    crf.date_of_referral,
                    crf.referred_to
                FROM
                    `tabChild Referral` AS crf 
                    Where 
                    YEAR(crf.date_of_referral) = %(year)s
                    AND MONTH(crf.date_of_referral) = %(month)s
                    AND (%(partner)s IS NULL OR crf.partner_id = %(partner)s) 
                    AND (%(state)s IS NULL OR crf.state_id = %(state)s) 
                    AND (%(district)s IS NULL OR crf.district_id = %(district)s)
                    AND (%(block)s IS NULL OR crf.block_id = %(block)s)
                    AND (%(gp)s IS NULL OR crf.gp_id = %(gp)s) 
                    AND (%(creche)s IS NULL OR crf.name = %(creche)s)
                ) as crfd ON crfd.childenrolledguid = ad.childenrollguid
            LEFT JOIN(
                SELECT
                cfu.childenrolledguid,
                CASE WHEN cfu.followup_visit_date THEN 'Y' ELSE '-' END AS follow_up 
                FROM
                    `tabChild Follow up` AS cfu 
                    Where YEAR(cfu.followup_visit_date) = %(year)s
                    AND MONTH(cfu.followup_visit_date) = %(month)s
                    AND (%(partner)s IS NULL OR cfu.partner_id = %(partner)s) 
                    AND (%(state)s IS NULL OR cfu.state_id = %(state)s) 
                    AND (%(district)s IS NULL OR cfu.district_id = %(district)s)
                    AND (%(block)s IS NULL OR cfu.block_id = %(block)s)
                    AND (%(gp)s IS NULL OR cfu.gp_id = %(gp)s) 
                    AND (%(creche)s IS NULL OR cfu.name = %(creche)s)
                ) as cfud ON cfud.childenrolledguid = ad.childenrollguid
            WHERE 
                YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND (%(partner)s IS NULL OR cr.partner_id = %(partner)s) 
                AND (%(state)s IS NULL OR cr.state_id = %(state)s) 
                AND (%(district)s IS NULL OR cr.district_id = %(district)s)
                AND (%(block)s IS NULL OR cr.block_id = %(block)s)
                AND (%(gp)s IS NULL OR cr.gp_id = %(gp)s) 
                AND (%(creche)s IS NULL OR cr.name = %(creche)s)
                AND (%(creche_status_id)s IS NULL OR cr.creche_status_id = %(creche_status_id)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            ORDER BY
                cr.partner_id, cr.state_id, cr.district_id, cr.block_id, cr.gp_id, cr.supervisor_id, cr.name, cee.child_name;
        """
    data = frappe.db.sql(sql_query, params, as_dict=True)

    counts = {
        "child_name": 0,
        "measurements_taken": 0,
        "growth_faltering_1": 0,
        "growth_faltering_2": 0,
        "nrc": 0,
        "chc": 0,
        "vhsnd": 0,
        "follow_up": 0,
        "red_flag": 0,
        "red_flag_HV": 0,
        "phc": 0,
        "any_medical_major_illness": 0,
        "othr": 0
    }

    for row in data:
        # Initialize all expected keys with default values if they don't exist
        row.setdefault("othr", "-")
        row.setdefault("nrc", "-")
        row.setdefault("chc", "-")
        row.setdefault("vhsnd", "-")
        row.setdefault("follow_up", "-")
        row.setdefault("red_flag", "-")
        row.setdefault("red_flag_HV", "-")
        row.setdefault("phc", "-")
        row.setdefault("any_medical_major_illness", 0)

        counts["child_name"] += 1 
        if row.get("measurements_taken") == "Y":
            counts["measurements_taken"] += 1
        if row.get("growth_faltering_1") == "Y":
            counts["growth_faltering_1"] += 1
        if row.get("growth_faltering_2") == "Y":
            counts["growth_faltering_2"] += 1
        if row.get("nrc") == "Y":
            counts["nrc"] += 1
        if row.get("phc") == "Y":
            counts["phc"] += 1
        if row.get("red_flag_HV") == "Y":
            counts["red_flag_HV"] += 1
        if row.get("othr") == "Y":
            counts["othr"] += 1
        if row.get("chc") == "Y":
            counts["chc"] += 1
        if row.get("vhsnd") == "Y":
            counts["vhsnd"] += 1
        if row.get("follow_up") == "Y":
            counts["follow_up"] += 1
        if row.get("red_flag") == "Y":
            counts["red_flag"] += 1
        if row.get("any_medical_major_illness") == 1:
            counts["any_medical_major_illness"] += 1

    summary_row = {
        "partner": "<b style='color:black;'>Total</b>",
        "child_name": counts['child_name'],
        "measurements_taken": counts['measurements_taken'],
        "growth_faltering_1": counts['growth_faltering_1'],
        "growth_faltering_2": counts['growth_faltering_2'],
        "nrc": counts['nrc'],
        "chc": counts['chc'],
        "vhsnd": counts['vhsnd'],
        "follow_up": counts['follow_up'],
        "phc": counts['phc'],
        "red_flag_HV": counts['red_flag_HV'],
        "red_flag": counts['red_flag'],
        "any_medical_major_illness": counts['any_medical_major_illness'],
        "othr": counts['othr']
    }
    data.append(summary_row)

    return data