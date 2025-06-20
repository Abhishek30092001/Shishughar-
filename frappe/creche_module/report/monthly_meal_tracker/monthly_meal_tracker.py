import frappe
from frappe.utils import nowdate
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
        {"label": "No. of days creche was open", "fieldname": "days_creche_open", "fieldtype": "Int", "width": 250},
        {"label": "Avg. Children Present", "fieldname": "avg_children_present", "fieldtype": "Int", "width": 250},
        {"label": "Avg. Children having Breakfast", "fieldname": "avg_breakfast", "fieldtype": "Int", "width": 300},
        {"label": "Avg. Children having Lunch", "fieldname": "avg_lunch", "fieldtype": "Int", "width": 250},
        {"label": "Avg. Children having Eggs", "fieldname": "avg_egg", "fieldtype": "Int", "width": 250},
        {"label": "Avg. Children having Evening Snacks", "fieldname": "avg_evening_snacks", "fieldtype": "Int", "width": 300},
        {"label": "Avg. No. of days ECD activity was done", "fieldname": "avg_ecd_activity", "fieldtype": "Int", "width": 350},
    ]

    data = get_report_data(filters)
    return columns, data


def get_report_data(filters):

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
    if state_id:
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
   
    

    query = f"""
        SELECT 
            tf.partner AS partner, 
            tf.state AS state, 
            tf.district AS district, 
            tf.block AS block, 
            tf.gp AS gp, 
            tf.village AS village, 
            tf.creche AS creche,
            tf.creche_id,
            tf.days_creche_open AS days_creche_open,
            ROUND(tf.avg_children_present,0) AS avg_children_present,
            ROUND(tf.avg_breakfast,0) as avg_breakfast,
            ROUND(tf.avg_lunch,0) as avg_lunch,
            ROUND(tf.avg_egg,0) as avg_egg,
            ROUND(tf.avg_evening_snacks,0) as avg_evening_snacks,
            ROUND(tf.avg_ecd_activity,0) as avg_ecd_activity
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
                IFNULL(cr.days_creche_open, 0) AS days_creche_open,
                IFNULL(ar.avg_children_present / ar.count,0) as avg_children_present,
                IFNULL(food.breakfast / ar.count,0) as avg_breakfast,
                IFNULL(food.lunch / ar.count,0) as avg_lunch,
                IFNULL(food.egg / ar.count,0) as avg_egg,
                IFNULL(food.evening_snacks / ar.count,0) as avg_evening_snacks,
                IFNULL(ecd.ecd / ar.count,0) as avg_ecd_activity

            FROM 
                `tabCreche` AS c 
            LEFT JOIN (
                SELECT 
                    ca.creche_id, 
                    COUNT(DISTINCT ca.name) AS days_creche_open
                FROM 
                    `tabChild Attendance` AS ca
                WHERE
                    is_shishu_ghar_is_closed_for_the_day = 0
                    AND ca.date_of_attendance between %(start_date)s and %(end_date)s
                    AND (ca.partner_id = %(partner)s OR %(partner)s IS NULL)
                GROUP BY 
                    ca.creche_id
            ) AS cr ON c.name = cr.creche_id

            LEFT JOIN (
                SELECT ca.creche_id, COUNT(*) as avg_children_present, count(DISTINCT ca.name) as count
                FROM `tabChild Attendance List` AS cal 
                left join
                    `tabChild Attendance` AS ca on ca.name = cal.parent
                WHERE cal.attendance = 1
                    AND is_shishu_ghar_is_closed_for_the_day = 0
                    AND ca.date_of_attendance between %(start_date)s and %(end_date)s
                    AND (ca.partner_id = %(partner)s OR %(partner)s IS NULL)
                GROUP BY 
                    ca.creche_id
            ) AS ar ON c.name = ar.creche_id

            LEFT JOIN (
                SELECT ca.creche_id, sum(breakfast) as breakfast, sum(lunch) as lunch, sum(egg) as egg, sum(evening_snacks) as evening_snacks
                FROM 
                    `tabChild Attendance` AS ca
                WHERE
                    ca.is_shishu_ghar_is_closed_for_the_day = 0
                    AND ca.date_of_attendance between %(start_date)s and %(end_date)s
                    AND (ca.partner_id = %(partner)s OR %(partner)s IS NULL)
                GROUP BY 
                    ca.creche_id
            ) AS food ON c.name = food.creche_id

            LEFT JOIN (
                SELECT ca.creche_id, count(Distinct ca.name) as ecd
                FROM
                    `tabChild Attendance` AS ca
                WHERE
                    ca.is_shishu_ghar_is_closed_for_the_day = 0
                    AND ca.isecd_activities_done_for_the_day = 1
                    AND ca.date_of_attendance between %(start_date)s and %(end_date)s
                    AND (ca.partner_id = %(partner)s OR %(partner)s IS NULL)
                GROUP BY 
                    ca.creche_id
            ) AS ecd ON c.name = ecd.creche_id

            JOIN 
                `tabState` AS s ON c.state_id = s.name 
            JOIN 
                `tabDistrict` AS d ON c.district_id = d.name
            JOIN 
                `tabBlock` AS b ON c.block_id = b.name
            JOIN 
                `tabGram Panchayat` AS g ON c.gp_id = g.name
            JOIN 
                `tabVillage` AS v ON c.village_id = v.name
            JOIN 
                `tabPartner` AS p ON c.partner_id = p.name 
            WHERE 
                (%(partner)s IS NULL OR p.name = %(partner)s) AND
                (%(state)s IS NULL OR s.name = %(state)s) AND
                (%(district)s IS NULL OR d.name = %(district)s) AND
                (%(block)s IS NULL OR b.name = %(block)s) AND
                (%(gp)s IS NULL OR g.name = %(gp)s) AND
                (%(creche)s IS NULL OR c.name = %(creche)s)
                AND (%(supervisor_id)s IS NULL OR c.supervisor_id = %(supervisor_id)s)
                AND (%(creche_status_id)s IS NULL OR c.creche_status_id = %(creche_status_id)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(c.phase, %(phases)s))
                AND (
                    (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                    OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
                )
        ) AS tf;
"""

    params.update({
        "start_date": start_date,
        "end_date": end_date,
        "partner": partner,
        'state':state,
        "district": district,
        "block": block,
        "gp": gp,
        "supervisor_id": supervisor_id,
        "creche": creche,
        "creche_status_id":creche_status_id,
        "phases":phases_cleaned,
        "cstart_date":cstart_date, 
        "cend_date":cend_date,
        "month": month,
        "year": year
    })
    
    data = frappe.db.sql(query, params, as_dict=True)
    return data
