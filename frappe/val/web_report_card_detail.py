from datetime import date
import frappe
import calendar
def format_query(query, params):
    for k, v in params.items():
        if v is None:
            v = "NULL"
        elif isinstance(v, str):
            v = f"'{v}'"
        elif hasattr(v, 'strftime'):
            v = f"'{v.strftime('%%Y-%%m-%%d')}'"
        query = query.replace(f"%({k})s", str(v))
    return query
@frappe.whitelist(allow_guest=True)
def fetch_card_data(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None, query_type="active_children"):
    year = int(year) if year and year.isdigit() else date.today().year
    month = int(month) if month and month.isdigit() else date.today().month

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

    if phases:
        try:
            phases = [p.strip() for p in phases.split(",") if p.strip().isdigit()]
        except:
            phases = None

    lmonth, plmonth, lyear, pyear = None, None, None, None
    if month == 1:
        lmonth, plmonth, lyear, pyear = 12, 11, year - 1, year - 1
    elif month == 2:
        lmonth, plmonth, lyear, pyear = 1, 12, year, year - 1
    else:
        lmonth, plmonth, lyear, pyear = month - 1, month - 2, year, year

    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

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
        "phases": ",".join(phases) if phases else None
    }


    active_children = """
        -- Active Children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN `tabHousehold Form` hf ON hf.hhguid = cee.hhguid
        WHERE cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(end_date)s)
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
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
            OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """

    enrolled_children_this_month = """
        -- Enrolled Children This Month --
        SELECT 
            cees.child_id as "Child ID",
            cees.child_name as "Child Name",
            DATE_FORMAT(cees.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cees.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cees.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche ",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        
        FROM `tabChild Enrollment and Exit` cees
        JOIN `tabCreche` cr ON cr.name = cees.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN `tabHousehold Form` hf ON hf.hhguid = cees.hhguid
        WHERE YEAR(cees.date_of_enrollment) = %(year)s  
        AND MONTH(cees.date_of_enrollment) = %(month)s 
        AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cees.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cr.state_id, %(state_ids)s))
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
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cr.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )               
        AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)) 
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cees.child_name USING utf8mb4))
    """

    current_eligible_children = """
        -- current eligible children  --
        SELECT
            hhc.child_name as "Child Name",
            DATE_FORMAT(hhc.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN hhc.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
             
           
        FROM `tabHousehold Child Form` AS hhc 
        JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
        JOIN `tabCreche` AS cr ON cr.name = hf.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
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
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(hhc.child_name USING utf8mb4))
    """
    
    exited_children_this_month = """
    -- exited children this month --
    SELECT 
        cee.child_id as "Child ID",
        cee.child_name as "Child Name",
        DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
        CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
        DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
        cr.creche_id as "Creche ID", 
        cr.creche_name as "Creche",
        g.gp_name as "GP",
        b.block_name as "Block",
        d.district_name as "District",
        s.state_name as "State",
        p.partner_name as "Partner"
    FROM `tabChild Enrollment and Exit` cee 
    LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
    JOIN `tabCreche` AS cr ON cr.name = cee.creche_id
    INNER JOIN `tabPartner` p ON p.name = cr.partner_id
    INNER JOIN `tabState` s ON s.name = cr.state_id
    INNER JOIN `tabDistrict` d ON d.name = cr.district_id
    INNER JOIN `tabBlock` b ON b.name = cr.block_id
    INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
    WHERE YEAR(date_of_exit) = %(year)s  
    AND MONTH(date_of_exit) = %(month)s  
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
    ORDER BY 
        TRIM(CONVERT(p.partner_name USING utf8mb4)),
        TRIM(CONVERT(s.state_name USING utf8mb4)),
        TRIM(CONVERT(d.district_name USING utf8mb4)),
        TRIM(CONVERT(b.block_name USING utf8mb4)),
        TRIM(CONVERT(g.gp_name USING utf8mb4)),
        TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
        TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    moderately_underweight = """
    -- moderly underweight children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id

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
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    moderately_wasted = """

    -- moderly wasted --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
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
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    moderately_stunted = """
    -- moderly stunted --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
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
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    gf1 = """
    -- GF1 --
        SELECT 
                cee.child_id as "Child ID",
                cee.child_name as "Child Name",
                DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
                CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
                DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
                cr.creche_id as "Creche ID", 
                cr.creche_name as "Creche",
                g.gp_name as "GP",
                b.block_name as "Block",
                d.district_name as "District",
                s.state_name as "State",
                p.partner_name as "Partner"
         FROM 
            `tabAnthropromatic Data` AS ad
        INNER JOIN 
            `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN 
            `tabCreche` AS cr ON cr.name = cgm.creche_id
        LEFT JOIN 
            `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN 
            `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        INNER JOIN 
            `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN 
            `tabState` s ON s.name = cr.state_id
        INNER JOIN 
            `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN 
            `tabBlock` b ON b.name = cr.block_id
        INNER JOIN 
            `tabGram Panchayat` g ON g.name = cr.gp_id    
        INNER JOIN
            `tabAnthropromatic Data` AS ad_lyear ON 
                ad_lyear.childenrollguid = ad.childenrollguid AND 
                ad_lyear.do_you_have_height_weight = 1 AND
                YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
                MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
                ad.weight <= ad_lyear.weight
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
            AND (%(creche_id)s IS NULL OR cr.name = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            AND ad_pyear.name IS NULL
            ORDER BY 
                TRIM(CONVERT(p.partner_name USING utf8mb4)),
                TRIM(CONVERT(s.state_name USING utf8mb4)),
                TRIM(CONVERT(d.district_name USING utf8mb4)),
                TRIM(CONVERT(b.block_name USING utf8mb4)),
                TRIM(CONVERT(g.gp_name USING utf8mb4)),
                TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
                TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    
    severly_underweight = """

    -- Total Severely Underweight Children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
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
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))    
    """
    severly_wasted = """
    -- Total_SAM_children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
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
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    severly_stunted = """
    -- Severely Stunted Children --
        SELECT
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name",
            g.gp_name as "GP Name",
            b.block_name as "Block Name",
            d.district_name as "District Name",
            s.state_name as "State Name",
            p.partner_name as "Partner Name"

        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
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
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    gf2 = """
    -- GF2 --
    SELECT 
                cee.child_id as "Child ID",
                cee.child_name as "Child Name",
                DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
                CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
                DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
                cr.creche_id as "Creche ID", 
                cr.creche_name as "Creche",
                g.gp_name as "GP",
                b.block_name as "Block",
                d.district_name as "District",
                s.state_name as "State",
                p.partner_name as "Partner"
         FROM 
            `tabAnthropromatic Data` AS ad
        INNER JOIN 
            `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN 
            `tabCreche` AS cr ON cr.name = cgm.creche_id
        LEFT JOIN 
            `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN 
            `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        INNER JOIN 
            `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN 
            `tabState` s ON s.name = cr.state_id
        INNER JOIN 
            `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN 
            `tabBlock` b ON b.name = cr.block_id
        INNER JOIN 
            `tabGram Panchayat` g ON g.name = cr.gp_id    
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
            AND (%(creche_id)s IS NULL OR cr.name = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            ORDER BY 
                TRIM(CONVERT(p.partner_name USING utf8mb4)),
                TRIM(CONVERT(s.state_name USING utf8mb4)),
                TRIM(CONVERT(d.district_name USING utf8mb4)),
                TRIM(CONVERT(b.block_name USING utf8mb4)),
                TRIM(CONVERT(g.gp_name USING utf8mb4)),
                TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
                TRIM(CONVERT(cee.child_name USING utf8mb4))
    """

    anthro_data_submitted = """
        SELECT 
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            CASE 
                WHEN cr.creche_status_id = 1 THEN 'Planned'
                WHEN cr.creche_status_id = 2 THEN 'Plan dropped'
                WHEN cr.creche_status_id = 3 THEN 'Active/ Operational'
                WHEN cr.creche_status_id = 4 THEN 'Closed'
                ELSE 'Unknown'
            END AS "Creche Status",
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabChild Growth Monitoring` cgm
        JOIN `tabCreche` cr on cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
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
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4))
        """
    no_of_creches = """


        SELECT 
            tc.creche_id as "Creche ID",
            tc.creche_name as "Creche",
            CASE 
                WHEN tc.creche_status_id = 1 THEN 'Planned'
                WHEN tc.creche_status_id = 2 THEN 'Plan dropped'
                WHEN tc.creche_status_id = 3 THEN 'Active/ Operational'
                WHEN tc.creche_status_id = 4 THEN 'Closed'
                ELSE 'Unknown'
            END AS "Creche Status",
            DATE_FORMAT(tc.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabCreche` tc
            LEFT JOIN `tabPartner` p ON p.name = tc.partner_id
            LEFT JOIN `tabState` s ON s.name = tc.state_id
            LEFT JOIN `tabDistrict` d ON d.name = tc.district_id
            LEFT JOIN `tabBlock` b ON b.name = tc.block_id
            LEFT JOIN `tabGram Panchayat` g ON g.name = tc.gp_id
            WHERE (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
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
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(tc.creche_name USING utf8mb4))

    """

    no_creche_attendance_submitted = """

    -- no_creche_attendance_submitted --

    SELECT 
        cr.creche_id AS "Creche ID", 
        cr.creche_name AS "Creche Name",
        CASE 
            WHEN cr.creche_status_id = 1 THEN 'Planned'
            WHEN cr.creche_status_id = 2 THEN 'Plan dropped'
            WHEN cr.creche_status_id = 3 THEN 'Active/ Operational'
            WHEN cr.creche_status_id = 4 THEN 'Closed'
            ELSE 'Unknown'
        END AS "Creche Status",
        DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
        g.gp_name AS "GP",
        b.block_name AS "Block",
        d.district_name AS "District",
        s.state_name AS "State",
        p.partner_name AS "Partner"
    FROM (
        SELECT 
            tc.name, 
            DATEDIFF(
                CASE 
                    WHEN DATE_FORMAT(CURRENT_DATE(), '%%Y-%%m') = DATE_FORMAT(%(end_date)s, '%%Y-%%m')
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
    ) AS FT
    JOIN `tabCreche` cr ON cr.name = FT.name
    INNER JOIN `tabPartner` p ON cr.partner_id = p.name
    INNER JOIN `tabState` s ON cr.state_id = s.name
    INNER JOIN `tabDistrict` d ON cr.district_id = d.name
    INNER JOIN `tabBlock` b ON cr.block_id = b.name
    INNER JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
    WHERE FT.elgdays <= FT.attdays
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
    AND (%(creche_id)s IS NULL OR cr.name = %(creche_id)s)
    AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
    AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
    AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
    AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4))
    """

    measurement_data_submitted = """


    SELECT
        cee.child_id AS "Child ID",
        cee.child_name AS "Child Name",
        DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
        CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
        DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
        cr.creche_id AS "Creche ID", 
        cr.creche_name AS "Creche",
        g.gp_name AS "GP",
        b.block_name AS "Block",
        d.district_name AS "District",
        s.state_name AS "State",
        p.partner_name AS "Partner"
        FROM `tabAnthropromatic Data` AS ad
        LEFT JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        LEFT JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabGram Panchayat` AS g ON g.name = cgm.gp_id
        INNER JOIN `tabBlock` AS b ON b.name = cgm.block_id
        INNER JOIN `tabDistrict` AS d ON d.name = cgm.district_id
        INNER JOIN `tabState` AS s ON s.name = cgm.state_id
        INNER JOIN `tabPartner` AS p ON p.name = cgm.partner_id
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
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))



    """




    # Choose query based on type
    if str(query_type) == "active_children":
         final_query = active_children
    elif str(query_type) == "enrolled_children_this_month":
        final_query = enrolled_children_this_month
    elif str(query_type) == "current_eligible_children":
        final_query = current_eligible_children
    elif str(query_type) == "exited_children_this_month":
        final_query = exited_children_this_month
    elif str(query_type) == "moderately_underweight":
        final_query = moderately_underweight
    elif str(query_type) == "moderately_wasted":
        final_query = moderately_wasted
    elif str(query_type) == "moderately_stunted":
        final_query = moderately_stunted
    elif str(query_type) == "gf1":
        final_query = gf1
    elif str(query_type) == "severly_underweight":
        final_query = severly_underweight
    elif str(query_type) == "severly_wasted":
        final_query = severly_wasted
    elif str(query_type) == "severly_stunted":
        final_query = severly_stunted
    elif str(query_type) == "gf2":
        final_query = gf2
    elif str(query_type) == "no_creche_attendance_submitted":
        final_query = no_creche_attendance_submitted
    elif str(query_type) == "anthro_data_submitted":
        final_query = anthro_data_submitted
    elif str(query_type) == "no_of_creches":
        final_query = no_of_creches
    elif str(query_type) == "measurement_data_submitted":
        final_query = measurement_data_submitted

    else:
        frappe.response["Error"] = "Invalid query_type parameter"
        return
    # res = format_query(final_query, params)
    # return res


    result = frappe.db.sql(final_query, params, as_dict=True)

    frappe.response["data"] = result or []

 