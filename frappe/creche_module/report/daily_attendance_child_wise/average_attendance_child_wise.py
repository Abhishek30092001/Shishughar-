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
        {"label": "Name", "fieldname": "name", "fieldtype": "Data", "width": 160},
        {"label": "Age (in months)", "fieldname": "age", "fieldtype": "Data", "width": 142},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 85},
        {"label": "Eligible Open Days", "fieldname": "eligible_open_days", "fieldtype": "Data", "width": 150},
        {"label": "Days Attended", "fieldname": "days_attended", "fieldtype": "Data", "width": 130},
        {"label": "Attendance (%)", "fieldname": "attendance_percentage", "fieldtype": "Data", "width": 130, "align": "right"}
    ]
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    partner = frappe.db.get_value("User", frappe.session.user, "partner")
    month = int(filters.get("month") if filters else nowdate().split('-')[1])
    year = int(filters.get("year") if filters else nowdate().split('-')[0])

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    date_range = filters.get("date_range") if filters else None
    cstart_date, cend_date = (date_range if date_range else (None, None))

    params = {}
    partner = None
    state = None
    district = None
    block = None
    gp = None
    creche = None
    band = None


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
    if filters.get("band"):
        band = filters.get('band')

    sql_query = f"""
        SELECT * FROM (
            SELECT *,
                CASE 
                    WHEN attendance_percentage BETWEEN 0 AND 25 THEN 1
                    WHEN attendance_percentage BETWEEN 26 AND 50 THEN 2 
                    WHEN attendance_percentage BETWEEN 51 AND 75 THEN 3
                    WHEN attendance_percentage BETWEEN 76 AND 100 THEN 4 
                    ELSE 0 
                END AS band
            FROM (
                SELECT 
                    p.partner_name AS partner,
                    s.state_name AS state,
                    d.district_name AS district,
                    b.block_name AS block,
                    g.gp_name AS gp,
                    c.creche_name AS creche,
                    c.creche_opening_date AS creche_opening_date,
                    c.creche_closing_date AS creche_closing_date,
                    cee.child_name AS name,
                    cee.age_at_enrollment_in_months AS age,
                    (CASE 
                        WHEN cee.gender_id = '1' THEN 'M' 
                        WHEN cee.gender_id = '2' THEN 'F' 
                        ELSE cee.gender_id 
                    END) AS gender,
                    att.eligible_open_days AS eligible_open_days,
                    att.days_attended AS days_attended,
                    ROUND(
                        CASE 
                            WHEN att.eligible_open_days > 0 
                            THEN (att.days_attended * 100.0 / att.eligible_open_days) 
                            ELSE 0 
                        END, 2
                    ) AS attendance_percentage
                FROM 
                    `tabChild Enrollment and Exit` AS cee
                JOIN 
                    `tabCreche` AS c ON c.name = cee.creche_id
                JOIN 
                    `tabPartner` AS p ON p.name = c.partner_id
                JOIN 
                    `tabState` AS s ON s.name = c.state_id
                JOIN 
                    `tabDistrict` AS d ON d.name = c.district_id
                JOIN 
                    `tabBlock` AS b ON b.name = c.block_id
                JOIN 
                    `tabGram Panchayat` AS g ON g.name = c.gp_id
                INNER JOIN (
                    SELECT 
                        cal.childenrolledguid,
                        COUNT(CASE WHEN cal.attendance = 1 THEN 1 END) AS days_attended,
                        COUNT(ca.date_of_attendance) AS eligible_open_days
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
                    GROUP BY cal.childenrolledguid
                ) AS att ON att.childenrolledguid = cee.childenrollguid
                WHERE 
                    (%(partner)s IS NULL OR c.partner_id = %(partner)s) 
                    AND (%(state)s IS NULL OR c.state_id = %(state)s) 
                    AND (%(district)s IS NULL OR c.district_id = %(district)s)
                    AND (%(block)s IS NULL OR c.block_id = %(block)s)
                    AND (%(gp)s IS NULL OR c.gp_id = %(gp)s) 
                    AND (%(creche)s IS NULL OR c.name = %(creche)s)
                    AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)) AS FDT
        ) AS FT  
        WHERE (%(band)s IS NULL OR band = %(band)s)

"""

    params.update({
        "start_date": start_date,
        "end_date": end_date,
        "partner": partner,
        'state':state,
        "district": district,
        "block": block,
        "gp": gp,
        "creche": creche,
        "band": band,
        "year": year,
        "month": month,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
    })
    
    data = frappe.db.sql(sql_query, params, as_dict=True)


    total_eligible_open_days = 0
    total_days_attended = 0
    total_attendance_percentage = 0


    for row in data:
        total_eligible_open_days += row.get("eligible_open_days", 0)
        total_days_attended += row.get("days_attended", 0)

    total_attendance_percentage = round((total_days_attended * 100.0 / total_eligible_open_days) if total_eligible_open_days > 0 else 0, 2)

    def get_attendance_percentage_style(percentage):
        if percentage is None:
            return "background-color: gray; color: black;"
        elif 0 <= percentage <= 25:
            return "background-color: #f85151; color: black;"
        elif 26 <= percentage <= 50:
            return "background-color: #f96235; color: black;"
        elif 51 <= percentage <= 75:
            return "background-color: #f9ed35; color: black;"
        elif 76 <= percentage <= 100:
            return "background-color: #aff935; color: black;"
        return "background-color: gray; color: black;"

    attendance_style = get_attendance_percentage_style(total_attendance_percentage)
    attendance_html = f"<b style='{attendance_style} padding: 5px; border-radius: 3px;'>{total_attendance_percentage}%</b>"
    summary_row = {
        "gender": "<b style='color:black;'>Total</b>",
        "eligible_open_days": f"<b style='color:black;'>{total_eligible_open_days}</b>",
        "days_attended": f"<b style='color:black;'>{total_days_attended}</b>",
        "attendance_percentage": attendance_html
    }

    data.append(summary_row)

    return data