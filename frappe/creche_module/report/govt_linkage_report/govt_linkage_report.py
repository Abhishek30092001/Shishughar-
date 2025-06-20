import frappe
from frappe.utils import nowdate
import calendar
from datetime import date

def execute(filters=None):
    columns, data = [], []

    selected_level = filters.get("level", "7")
    variable_columns = []
    if selected_level == "1":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 160})
    elif selected_level == "2":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
    elif selected_level == "3":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
    elif selected_level == "4":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
    elif selected_level == "5":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 160})
    elif selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
    elif selected_level == "7":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})

    fixed_columns = [
        {"label": "Enrolled Children", "fieldname": "enrolled", "fieldtype": "Data", "width": 150},
        {"label": "Children planned VHSND visit", "fieldname": "vhsnd1", "fieldtype": "Data", "width": 230},
        {"label": "Children visited VHSND", "fieldname": "vhsnd", "fieldtype": "Data", "width": 200},
        {"label": "Children received THR", "fieldname": "thr", "fieldtype": "Data", "width": 200},
        {"label": "Children weighed in AWC", "fieldname": "awc", "fieldtype": "Data", "width": 200}
    ]

    columns = variable_columns + fixed_columns
    data = get_report_data(filters)
    return columns, data

def get_report_data(filters):
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

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

    conditions = ["1=1"]
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "cstart_date": None,
        "cend_date": None,
    }

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

    if partner_id:
        conditions.append("c.partner_id = %(partner)s")
        params["partner"] = partner_id
    if state_id:
        conditions.append("c.state_id = %(state)s")
        params["state"] = state_id
    if filters.get("district"):
        conditions.append("c.district_id = %(district)s")
        params["district"] = filters.get("district")
    if filters.get("block"):
        conditions.append("c.block_id = %(block)s")
        params["block"] = filters.get("block")
    if filters.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    if filters.get("creche"):
        conditions.append("c.name = %(creche)s")
        params["creche"] = filters.get("creche")
    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")
    if filters.get("creche_status_id"):
        conditions.append("(c.creche_status_id = %(creche_status_id)s)")
        params["creche_status_id"] = filters.get("creche_status_id")
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
        if phases_cleaned:  
            conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
            params["phases"] = phases_cleaned    
    if  cstart_date and cend_date:
        conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
        params["cstart_date"] = cstart_date
        params["cend_date"] = cend_date

    # date_range = filters.get("date_range") if filters else None
    # if date_range:
    #     cstart_date, cend_date = date_range
    #     if cstart_date or cend_date:
    #         conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
    #         params["cstart_date"] = cstart_date if cstart_date else None  
    #         params["cend_date"] = cend_date if cend_date else None  

    level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "tu.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "7": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name", "c.creche_name", "c.creche_id"]
    }

    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)

    select_fields = [
        "p.partner_name AS partner",
        "s.state_name AS state",
        "d.district_name AS district",
        "b.block_name AS block",
        "tu.full_name AS supervisor",
        "g.gp_name AS gp",
        "c.creche_name AS creche",
        "c.creche_id AS creche_id"
    ]
    selected_fields = []
    for field in select_fields:
        if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
            selected_fields.append(field)

    where_clause = " AND ".join(conditions)
    group_by_field = ", ".join(group_by_fields)

    sql_query = f"""
        SELECT
            {", ".join(selected_fields)},
            SUM(IFNULL(cr.enrolled, 0)) AS enrolled,
            SUM(IFNULL(cg.vhsnd1, 0)) AS vhsnd1,
            SUM(IFNULL(ch.vhsnd, 0)) AS vhsnd,
            SUM(IFNULL(thr_awc.thr, 0)) AS thr,
            SUM(IFNULL(thr_awc.awc, 0)) AS awc
        FROM
            `tabCreche` AS c
        LEFT JOIN
            `tabState` AS s ON c.state_id = s.name
        LEFT JOIN
            `tabDistrict` AS d ON c.district_id = d.name
        LEFT JOIN
            `tabBlock` AS b ON c.block_id = b.name
        LEFT JOIN
            `tabGram Panchayat` AS g ON c.gp_id = g.name
        LEFT JOIN
            `tabPartner` AS p ON c.partner_id = p.name
        LEFT JOIN  
            `tabUser` tu ON c.supervisor_id = tu.name    
        LEFT JOIN (
            SELECT
                cee.creche_id,
                COUNT(*) AS enrolled
            FROM
                `tabChild Enrollment and Exit` AS cee
            WHERE
                cee.date_of_enrollment <= %(end_date)s 
                AND (cee.date_of_exit IS NULL OR cee.date_of_exit >=  %(start_date)s)
            GROUP BY
                cee.creche_id
        ) AS cr ON c.name = cr.creche_id
        LEFT JOIN (
            SELECT
                cgm.creche_id,
                COUNT(DISTINCT ad.chhguid) AS vhsnd1
            FROM
                `tabAnthropromatic Data` AS ad
            JOIN
                `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            JOIN
                `tabChild Enrollment and Exit` AS cee ON cee.hhcguid = ad.chhguid
            WHERE
                cee.date_of_enrollment <= %(end_date)s
                AND ad.vhsnd = 2
                AND ad.do_you_have_height_weight = 1
                AND ad.measurement_taken_date BETWEEN %(start_date)s AND %(end_date)s
            GROUP BY
                cgm.creche_id
        ) AS cg ON c.name = cg.creche_id
        LEFT JOIN (
            SELECT
                crf.creche_id,
                COUNT(CASE WHEN crf.referred_to = 1 THEN 1 END) AS vhsnd
            FROM
                `tabChild Referral` AS crf
            WHERE
                YEAR(crf.date_of_referral) = %(year)s
                AND MONTH(crf.date_of_referral) = %(month)s
            GROUP BY
                crf.creche_id
        ) AS ch ON c.name = ch.creche_id
        LEFT JOIN (
            SELECT
                cee.creche_id,
                COUNT(DISTINCT CASE WHEN ad.thr = 1 THEN ad.childenrollguid END) AS thr,
                COUNT(DISTINCT CASE WHEN ad.awc = 1 THEN ad.childenrollguid END) AS awc
            FROM
                `tabAnthropromatic Data` AS ad
            JOIN
                `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            JOIN
                `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
            WHERE
                cee.date_of_enrollment <=  %(end_date)s
                AND ad.measurement_taken_date BETWEEN %(start_date)s AND %(end_date)s
                AND ad.do_you_have_height_weight = 1
            GROUP BY
                cee.creche_id
        ) AS thr_awc ON c.name = thr_awc.creche_id
        WHERE
            {where_clause}
        GROUP BY
            {group_by_field} 
        ORDER BY
            {group_by_field}
    """

    data = frappe.db.sql(sql_query, params, as_dict=True)

    return data