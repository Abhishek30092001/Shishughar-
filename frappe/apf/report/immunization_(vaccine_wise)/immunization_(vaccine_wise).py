import frappe
from frappe.utils import nowdate
from datetime import datetime, timedelta
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
        {"label": "Creche ID", "fieldname": "crecheid", "fieldtype": "Data", "width": 120},
        {"label": "Enrolled Children", "fieldname": "active_children", "fieldtype": "Data", "width": 250},
        {"label": "No of Children Vaccinated", "fieldname": "fv", "fieldtype": "Data", "width": 250},
        {"label": "% of Children Vaccinated", "fieldname": "percentage", "fieldtype": "Data", "width": 250},
    ]
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):

    district = filters.get("district") if filters else None
    supervisor_id = filters.get("supervisor_id") if filters else None
    block = filters.get("block") if filters else None
    gp = filters.get("gp") if filters else None
    creche = filters.get("creche") if filters else None
    month = int(filters.get("month")) if filters else None
    year = int(filters.get("year")) if filters else None
    vaccine = filters.get("vaccine") if filters else None

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

    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None

    conditions = []
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
    
    if partner_id:
        conditions.append(f"att.partner_id = '{partner_id}'")
    if state_id:
        conditions.append(f"att.state_id = '{state_id}'")
    if district:
        conditions.append(f"att.district_id = '{district}'")
    if block:
        conditions.append(f"att.block_id = '{block}'")
    if gp:
        conditions.append(f"att.gp_id = '{gp}'")
    if creche:
        conditions.append(f"att.creche_id = '{creche}'")
    if vaccine:
        conditions.append(f"vd.vaccine_id = '{vaccine}'")
    if supervisor_id:
        conditions.append(f"c.supervisor_id = '{filters.get('supervisor_id')}'")
    if creche_status_id:
        conditions.append(f"c.creche_status_id = '{creche_status_id}'")
    if phases_cleaned:
        conditions.append(f"FIND_IN_SET(c.phase, '{phases_cleaned}')")
    if cstart_date and cend_date:
        conditions.append(f"c.creche_opening_date BETWEEN '{cstart_date}' AND '{cend_date}'")
    

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    params = {}
    condition_str = " AND ".join(conditions)
    where_clause = f"WHERE 1=1 AND {condition_str}" if condition_str else "WHERE 1=1"

    sql_query = f"""
        SELECT
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            c.creche_name AS creche,
            c.creche_id as crecheid,
            (SELECT COUNT(DISTINCT childenrollguid) 
                FROM `tabChild Enrollment and Exit` AS cp 
                WHERE cp.creche_id = c.name 
                AND cp.date_of_enrollment <= %(end_date)s 
                AND (cp.date_of_exit IS null or cp.date_of_exit >=  %(start_date)s)
            ) AS active_children,
            SUM(
                CASE
                    WHEN vd.vaccinated = 1 THEN 1 ELSE 0 
                END
            ) AS fv,
            (
                SUM(
                    CASE 
                        WHEN vd.vaccinated = 1 THEN 1 ELSE 0 
                    END
                ) / GREATEST(
                    (SELECT COUNT(DISTINCT childenrollguid) 
                        FROM `tabChild Enrollment and Exit` AS cp 
                    WHERE cp.creche_id = c.name 
                        AND cp.date_of_enrollment <= %(end_date)s 
                        AND (cp.date_of_exit IS null or cp.date_of_exit >=  %(start_date)s)
                    ), 1)
            ) * 100 AS percentage
        FROM
            `tabChild Immunization` AS att
        JOIN
            `tabCreche` AS c ON att.creche_id = c.name
        JOIN
            `tabState` AS s ON c.state_id = s.name
        JOIN
            `tabDistrict` AS d ON c.district_id = d.name
        JOIN
            `tabBlock` AS b ON c.block_id = b.name
        JOIN
            `tabGram Panchayat` AS g ON c.gp_id = g.name
        JOIN
            `tabPartner` AS p ON c.partner_id = p.name
        JOIN
            `tabVaccine Details` AS vd ON vd.parent = att.name
        {where_clause}
        GROUP BY
            p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, c.creche_name
        ORDER BY
            p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, c.creche_name
"""
    
    params.update({
        "start_date": start_date,
        "end_date": end_date,
        "cstart_date": None,
        "cend_date": None,
    })
    
    data = frappe.db.sql(sql_query, params, as_dict=True)
    return data
