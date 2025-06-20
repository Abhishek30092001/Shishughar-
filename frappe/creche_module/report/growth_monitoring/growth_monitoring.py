import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "crecheid", "fieldtype": "Data", "width": 120},
        {"label": _("Enrolled Children"), "fieldname": "e_children", "fieldtype": "Int", "width": 250},
        {"label": _("No of children whose growth monitoring has been done"), "fieldname": "g_children", "fieldtype": "Int", "width": 400},
        {"label": _("Percentage of children identified as Growth Falter 2"), "fieldname": "gf2", "fieldtype": "Int", "width": 400},
        {"label": _("Percentage of children identified as Growth Falter 1"), "fieldname": "gf1", "fieldtype": "Int", "width": 400},
        {"label": _("Percentage of children identified as moderately underweight (MUW)"), "fieldname": "muw", "fieldtype": "Int", "width": 500},
        {"label": _("Percentage of children identified as severely underweight (SUW)"), "fieldname": "suw", "fieldtype": "Int", "width": 500},
        {"label": _("Number and Percentage of children identified as severely wasted"), "fieldname": "sw", "fieldtype": "Int", "width": 500},
        {"label": _("Percentage of children identified as moderately wasted"), "fieldname": "mw", "fieldtype": "Int", "width": 400},
        {"label": _("No of Red flagged Children"), "fieldname": "red_flag", "fieldtype": "Int", "width": 250},
        {"label": _("No of Red flagged CHildren Followed up"), "fieldname": "red_flag_f", "fieldtype": "Int", "width": 300},
        {"label": _("No of children referred to health facility"), "fieldname": "hf", "fieldtype": "Int", "width": 300},
        {"label": _("No of children referred to NRC"), "fieldname": "nrc", "fieldtype": "Int", "width": 250},
        {"label": _("No of Children Followup visits done"), "fieldname": "cfv", "fieldtype": "Int", "width": 350},
    ]

    data = get_report_data(filters)
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
    

    query = f"""
SELECT 
    tf.partner AS partner, 
    tf.state AS state, 
    tf.district AS district, 
    tf.block AS block, 
    tf.gp AS gp, 
    tf.village AS village, 
    tf.creche AS creche, 
    tf.e_children AS e_children,
    tf.g_children AS g_children,
    CASE WHEN tf.muw = 0 THEN 0 ELSE FORMAT((tf.muw / tf.e_children)*100.0, 2) END AS muw,
    CASE WHEN tf.suw = 0 THEN 0 ELSE FORMAT((tf.suw / tf.e_children)*100.0, 2) END AS suw,
    tf.red_flag AS red_flag,
    tf.red_flag_f AS red_flag_f,
    tf.hf AS hf,
    tf.nrc AS nrc,
    tf.gf2 AS gf2
FROM (
    SELECT 
        p.partner_name AS partner,
        s.state_name AS state,
        d.district_name AS district,
        b.block_name AS block,
        g.gp_name AS gp,
        v.village_name AS village,
        c.creche_name AS creche,
        IFNULL(ec.e_children, 0) AS e_children,
        IFNULL(gc.g_children, 0) AS g_children,
        IFNULL(m.muw, 0) AS muw,
        IFNULL(s.suw, 0) AS suw,
        IFNULL(rf.red_flag, 0) AS red_flag,
        IFNULL(rff.red_flag_f, 0) AS red_flag_f,
        IFNULL(h.hf, 0) AS hf,
        IFNULL(nr.nrc, 0) AS nrc,
        IFNULL(gf2.gf2, 0) AS gf2

        
    FROM 
        tabCreche AS c 
    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT cep.hhcguid) AS e_children
        FROM 
            `tabChild Enrollment and Exit` AS cep
        WHERE 
            cep.date_of_enrollment IS NOT NULL
            AND cep.date_of_enrollment <= %(end_date)s
            and cep.is_active = 1 and cep.is_exited = 0
        GROUP BY 
            cep.creche_id
    ) AS ec ON c.name = ec.creche_id
LEFT JOIN (
    SELECT 
        cep.creche_id, 
        COUNT(DISTINCT ad.chhguid) AS gf2
    FROM `tabAnthropometric Data` AS ad
    LEFT JOIN
        `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    LEFT JOIN
        `tabChild Enrollment and Exit` AS cep ON cep.childenrollguid = ad.childenrollguid
    WHERE 
        cep.date_of_enrollment IS NOT NULL
        AND cep.date_of_enrollment <= %(end_date)s
        AND cep.is_active = 1 
        AND cep.is_exited = 0
        AND ad.do_you_have_height_weight = 1
        AND EXISTS (
            SELECT 1 
            FROM `tabAnthropometric Data` AS ad_inner
            WHERE ad_inner.childenrollguid = ad.childenrollguid
              AND ad_inner.measurement_taken_date BETWEEN DATE_SUB(ad.measurement_taken_date, INTERVAL 2 MONTH) AND ad.measurement_taken_date
              AND ad_inner.weight < ad.weight
        )
    GROUP BY 
        cep.creche_id
) AS gf2 ON c.name = gf2.creche_id


    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT ad.chhguid) AS g_children
        FROM `tabAnthropromatic Data` as ad
        LEFT JOIN
            `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = ad.childenrollguid
        WHERE 
            cep.date_of_enrollment IS NOT NULL
            AND cep.date_of_enrollment <= %(end_date)s
            and cep.is_active = 1 and cep.is_exited = 0
            and ad.do_you_have_height_weight = 1
        GROUP BY 
            cep.creche_id
    ) AS gc ON c.name = gc.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT ad.chhguid) AS muw
        FROM `tabAnthropromatic Data` as ad
        LEFT JOIN
            `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = ad.childenrollguid
        WHERE 
            cep.date_of_enrollment IS NOT NULL
            AND cep.date_of_enrollment <= %(end_date)s
            and cep.is_active = 1 and cep.is_exited = 0
            and ad.do_you_have_height_weight = 1
            and ad.weight_for_age = 2
        GROUP BY 
            cep.creche_id
    ) AS m ON c.name = m.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT ad.chhguid) AS suw
        FROM `tabAnthropromatic Data` as ad
        LEFT JOIN
            `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = ad.childenrollguid
        WHERE 
            cep.date_of_enrollment IS NOT NULL
            AND cep.date_of_enrollment <= %(end_date)s
            and cep.is_active = 1 and cep.is_exited = 0
            and ad.do_you_have_height_weight = 1
            and ad.weight_for_age = 1
        GROUP BY 
            cep.creche_id
    ) AS s ON c.name = s.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT cep.hhcguid) AS red_flag
        FROM `tabChild Referral` as cr
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
        WHERE 
            cep.date_of_enrollment IS NOT NULL
            AND cep.date_of_enrollment <= %(end_date)s
            and cep.is_active = 1 and cep.is_exited = 0
        GROUP BY 
            cep.creche_id
    ) AS rf ON c.name = rf.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT cep.hhcguid) AS red_flag_f
        FROM `tabChild Follow up` as cr
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
        WHERE 
            cep.date_of_enrollment IS NOT NULL
            AND cep.date_of_enrollment <= %(end_date)s
            and cep.is_active = 1 and cep.is_exited = 0
        GROUP BY 
            cep.creche_id
    ) AS rff ON c.name = rff.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT cep.hhcguid) AS hf
        FROM `tabChild Referral` as cr
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
        WHERE 
            cep.date_of_enrollment IS NOT NULL
            AND cep.date_of_enrollment <= %(end_date)s
            and cep.is_active = 1 and cep.is_exited = 0
            and cr.child_status != 4
        GROUP BY 
            cep.creche_id
    ) AS h ON c.name = h.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT cep.hhcguid) AS nrc
        FROM `tabChild Referral` as cr
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
        WHERE 
            cep.date_of_enrollment IS NOT NULL
            AND cep.date_of_enrollment <= %(end_date)s
            and cep.is_active = 1 and cep.is_exited = 0
            and cr.referred_to_nrc = 1
        GROUP BY 
            cep.creche_id
    ) AS nr ON c.name = nr.creche_id
    
    JOIN tabState AS s ON c.state_id = s.name 
    JOIN tabDistrict AS d ON c.district_id = d.name
    JOIN tabBlock AS b ON c.block_id = b.name
    JOIN `tabGram Panchayat` AS g ON c.gp_id = g.name
    JOIN tabVillage AS v ON c.village_id = v.name
    JOIN tabPartner AS p ON c.partner_id = p.name 
    WHERE 
        (%(partner)s IS NULL OR p.name = %(partner)s) and (%(state)s IS NULL OR s.name = %(state)s) and (%(district)s IS NULL OR d.name = %(district)s) and (%(block)s IS NULL OR b.name = %(block)s)
	and (%(gp)s IS NULL OR g.name = %(gp)s) and (%(creche)s IS NULL OR c.name = %(creche)s)
    GROUP BY 
        p.partner_name, s.state_name, d.district_name, b.block_name, 
        g.gp_name, v.village_name, c.creche_name
    ORDER BY 
        p.partner_name, s.state_name, d.district_name, b.block_name, 
        g.gp_name, v.village_name, c.creche_name
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
        "creche": creche
    })
    
    data = frappe.db.sql(query, params, as_dict=True)
    return data
