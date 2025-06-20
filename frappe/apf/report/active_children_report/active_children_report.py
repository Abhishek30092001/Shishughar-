import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    columns, data = [], []
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    selected_year = filters.get("year") or nowdate().split('-')[0]
    selected_month = filters.get("month") or nowdate().split('-')[1]

    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120}
    ]

    for month in months:
        month_label = f"{month[:3]}-{selected_year}"
        columns.append({"label": month_label, "fieldname": month.lower(), "fieldtype": "Int", "width": 110})

    data = get_report_data(filters)

    for idx, row in enumerate(data, start=1):
        row['idx'] = idx

    return columns, data


def get_report_data(filters):


    partner = frappe.db.get_value("User", frappe.session.user, "partner")
    

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
    if partner or filters.get('partner'):
        partner = filters.get('partner')
    if filters.get("state"):
        state = filters.get('state')
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
    

    query = f"""
    SELECT 
        tf.partner AS partner, 
        tf.state AS state, 
        tf.district AS district, 
        tf.block AS block, 
        tf.gp AS gp, 
        tf.village AS village, 
        tf.creche AS creche, tf.creche_id,
        tf.january, tf.february, tf.march, tf.april, tf.may, tf.june, 
        tf.july, tf.august, tf.september, tf.october, tf.november, tf.december
    FROM (
        SELECT 
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            v.village_name AS village,
            c.creche_name AS creche,
            c.creche_id,
            ROUND(IFNULL(CASE WHEN jan_days = 0 THEN 0 ELSE mattc.jan_count / jan_days END, 0),0) AS january,
            ROUND(IFNULL(CASE WHEN feb_days = 0 THEN 0 ELSE mattc.feb_count / feb_days END, 0),0) AS february,
            ROUND(IFNULL(CASE WHEN mar_days = 0 THEN 0 ELSE mattc.mar_count / mar_days END, 0),0) AS march,
            ROUND(IFNULL(CASE WHEN apr_days = 0 THEN 0 ELSE mattc.apr_count / apr_days END, 0),0) AS april,
            ROUND(IFNULL(CASE WHEN may_days = 0 THEN 0 ELSE mattc.may_count / may_days END, 0),0) AS may,
            ROUND(IFNULL(CASE WHEN jun_days = 0 THEN 0 ELSE mattc.jun_count / jun_days END, 0),0) AS june,
            ROUND(IFNULL(CASE WHEN jul_days = 0 THEN 0 ELSE mattc.jul_count / jul_days END, 0),0) AS july,
            ROUND(IFNULL(CASE WHEN aug_days = 0 THEN 0 ELSE mattc.aug_count / aug_days END, 0),0) AS august,
            ROUND(IFNULL(CASE WHEN sep_days = 0 THEN 0 ELSE mattc.sep_count / sep_days END, 0),0) AS september,
            ROUND(IFNULL(CASE WHEN oct_days = 0 THEN 0 ELSE mattc.oct_count / oct_days END, 0),0) AS october,
            ROUND(IFNULL(CASE WHEN nov_days = 0 THEN 0 ELSE mattc.nov_count / nov_days END, 0),0) AS november,
            ROUND(IFNULL(CASE WHEN dec_days = 0 THEN 0 ELSE mattc.dec_count / dec_days END, 0),0) AS december

        FROM 
            tabCreche AS c 

        LEFT JOIN ( SELECT ca.creche_id,
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 1 THEN 1 ELSE 0 END) AS jan_count, 
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 2 THEN 1 ELSE 0 END) AS feb_count, 
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 3 THEN 1 ELSE 0 END) AS mar_count,
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 4 THEN 1 ELSE 0 END) AS apr_count,
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 5 THEN 1 ELSE 0 END) AS may_count,
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 6 THEN 1 ELSE 0 END) AS jun_count, 
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 7 THEN 1 ELSE 0 END) AS jul_count,
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 8 THEN 1 ELSE 0 END) AS aug_count,
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 9 THEN 1 ELSE 0 END) AS sep_count, 
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 10 THEN 1 ELSE 0 END) AS oct_count,
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 11 THEN 1 ELSE 0 END) AS nov_count,
            SUM(CASE WHEN MONTH(cal.date_of_attendance) = 12 THEN 1 ELSE 0 END) AS dec_count
            FROM `tabChild Attendance List` AS cal
            JOIN `tabChild Attendance` AS ca ON ca.name = cal.parent
            WHERE cal.attendance = 1 AND ca.is_shishu_ghar_is_closed_for_the_day = 0 AND YEAR(cal.date_of_attendance) = %(year)s
            GROUP BY ca.creche_id) AS mattc ON mattc.creche_id = c.name

        LEFT JOIN (SELECT 
        ca.creche_id,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 1 THEN 1 ELSE 0 END) AS jan_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 2 THEN 1 ELSE 0 END) AS feb_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 3 THEN 1 ELSE 0 END) AS mar_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 4 THEN 1 ELSE 0 END) AS apr_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 5 THEN 1 ELSE 0 END) AS may_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 6 THEN 1 ELSE 0 END) AS jun_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 7 THEN 1 ELSE 0 END) AS jul_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 8 THEN 1 ELSE 0 END) AS aug_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 9 THEN 1 ELSE 0 END) AS sep_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 10 THEN 1 ELSE 0 END) AS oct_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 11 THEN 1 ELSE 0 END) AS nov_days,
        SUM(CASE WHEN MONTH(ca.date_of_attendance) = 12 THEN 1 ELSE 0 END) AS dec_days
        FROM 
            `tabChild Attendance` AS ca
        WHERE 
            ca.is_shishu_ghar_is_closed_for_the_day = 0 
            AND YEAR(ca.date_of_attendance) = %(year)s
        GROUP BY 
            ca.creche_id
        ) AS mcdp ON mcdp.creche_id = c.name
        JOIN tabState AS s ON c.state_id = s.name 
        JOIN tabDistrict AS d ON c.district_id = d.name
        JOIN tabBlock AS b ON c.block_id = b.name
        JOIN `tabGram Panchayat` AS g ON c.gp_id = g.name
        JOIN tabVillage AS v ON c.village_id = v.name
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

    ) AS tf


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
    
    data = frappe.db.sql(query, params, as_dict=True)
    return data
