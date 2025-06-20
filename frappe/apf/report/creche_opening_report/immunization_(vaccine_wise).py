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
        {"label": "Village", "fieldname": "village", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "crecheid", "fieldtype": "Data", "width": 120},
        {"label": "Enrolled Children", "fieldname": "active_children", "fieldtype": "Data", "width": 250},
        {"label": "No of Children Vaccinated", "fieldname": "fv", "fieldtype": "Data", "width": 250},
        {"label": "% of Children Vaccinated", "fieldname": "percentage", "fieldtype": "Data", "width": 250},
    ]
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    partner = filters.get("partner") if filters else None
    state = filters.get("state") if filters else None
    district = filters.get("district") if filters else None
    block = filters.get("block") if filters else None
    gp = filters.get("gp") if filters else None
    village = filters.get("village") if filters else None
    creche = filters.get("creche") if filters else None
    month = int(filters.get("month")) if filters else None
    year = int(filters.get("year")) if filters else None
    vaccine = filters.get("vaccine") if filters else None

    conditions = []
    logged_in_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    
    if logged_in_user_partner:
        conditions.append(f"c.partner_id = '{logged_in_user_partner}'")
    if partner:
        conditions.append(f"att.partner_id = '{partner}'")
    if state:
        conditions.append(f"att.state_id = '{state}'")
    if district:
        conditions.append(f"att.district_id = '{district}'")
    if block:
        conditions.append(f"att.block_id = '{block}'")
    if gp:
        conditions.append(f"att.gp_id = '{gp}'")
    if village:
        conditions.append(f"att.village_id = '{village}'")
    if creche:
        conditions.append(f"att.creche_id = '{creche}'")
    if vaccine:
        conditions.append(f"vd.vaccine_id = '{vaccine}'")

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
    v.village_name AS village,
    c.creche_name AS creche,
    c.creche_id as crecheid,
    (SELECT COUNT(DISTINCT childenrollguid) 
        FROM `tabChild Enrollment and Exit` AS cp 
    
        WHERE cp.creche_id = c.name 
        AND cp.is_active = 1 
        AND cp.is_exited = 0
        AND cp.date_of_enrollment <= %(end_date)s
    ) AS active_children,
    SUM(
        CASE 
            WHEN vd.vaccination_date <= %(end_date)s THEN 1 
            ELSE 0 
        END
    ) AS fv,
    (
        Round(SUM(
            CASE 
                WHEN vd.vaccination_date < %(end_date)s THEN 1 
                ELSE 0 
            END
        ) / GREATEST(
            (SELECT COUNT(DISTINCT childenrollguid) 
                FROM `tabChild Enrollment and Exit` AS cp 
                WHERE cp.creche_id = c.name 
                AND cp.is_active = 1 
                AND cp.is_exited = 0
                AND cp.date_of_enrollment <= %(end_date)s
            ), 1)
    ) * 100,2) AS percentage
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
    `tabVillage` AS v ON c.village_id = v.name
JOIN
    `tabPartner` AS p ON c.partner_id = p.name
JOIN
    `tabVaccine Details` AS vd ON vd.parent = att.name
{where_clause}
GROUP BY
    p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, v.village_name, c.creche_name
ORDER BY
    p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, v.village_name, c.creche_name
"""
    params.update({
        "start_date": start_date,
        "end_date": end_date
    })
    
    data = frappe.db.sql(sql_query, params, as_dict=True)
    return data
