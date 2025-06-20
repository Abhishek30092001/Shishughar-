import frappe
from frappe import _
from datetime import date
import calendar

def execute(filters=None):
    selected_level = filters.get("level", "5")
    variable_columns = []

    if selected_level >= "1":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
    if selected_level >= "2":
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
    if selected_level >= "3":
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
    if selected_level >= "4":
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
    if selected_level >= "5":
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})

    fixed_columns = [
        {"label": "weight_for_age_normal", "fieldname": "weight_for_age_normal", "fieldtype": "Data", "width": 300},
        {"label": "weight_for_age_moderate", "fieldname": "weight_for_age_moderate", "fieldtype": "Data", "width": 300},
        {"label": "height_for_age_severe", "fieldname": "height_for_age_severe", "fieldtype": "Data", "width": 300},
        
        {"label": "height_for_age_normal", "fieldname": "height_for_age_normal", "fieldtype": "Data", "width": 300},
        {"label": "height_for_age_moderate", "fieldname": "height_for_age_moderate", "fieldtype": "Data", "width": 300},
        {"label": "height_for_age_severe", "fieldname": "height_for_age_severe", "fieldtype": "Data", "width": 300},
        
        
        {"label": "weight_for_height_normal", "fieldname": "weight_for_height_normal", "fieldtype": "Data", "width": 300},
        {"label": "weight_for_height_moderate", "fieldname": "weight_for_height_moderate", "fieldtype": "Data", "width": 300},
        {"label": "weight_for_height_severe", "fieldname": "weight_for_height_severe", "fieldtype": "Data", "width": 300},

        {"label": _("Enrolled Children"), "fieldname": "e_children", "fieldtype": "Int", "width": 150},
        {"label": _("No. of Children whose Growth Monitoring has been done"), "fieldname": "g_children", "fieldtype": "Int", "width": 400},
        {"label": _("% of Children identified as Growth Falter 2"), "fieldname": "gf2", "fieldtype": "Int", "width": 400},
        {"label": _("% of Children identified as Growth Falter 1"), "fieldname": "gf1", "fieldtype": "Int", "width": 400},
        {"label": _("% of Children identified as Moderately Underweight (MUW)"), "fieldname": "muw", "fieldtype": "Int", "width": 500},
        {"label": _("% of Children identified as Severely Underweight (SUW)"), "fieldname": "suw", "fieldtype": "Int", "width": 500},
        {"label": _("% of Children identified as Moderately Wasted (MAM)"), "fieldname": "mam", "fieldtype": "Int", "width": 500},
        {"label": _("% of Children identified as Severely Wasted (SAM)"), "fieldname": "sam", "fieldtype": "Int", "width": 500},        
        {"label": _("No. of Red flagged Children"), "fieldname": "red_flag", "fieldtype": "Int", "width": 250},
        {"label": _("No. of Red flagged Children Followed up"), "fieldname": "red_flag_f", "fieldtype": "Int", "width": 300},
        {"label": _("No. of Children referred to Health Facility"), "fieldname": "hf", "fieldtype": "Int", "width": 300},
        {"label": _("No. of Children referred to NRC"), "fieldname": "nrc", "fieldtype": "Int", "width": 250},
        {"label": _("No. of Children followup visits done"), "fieldname": "cfu", "fieldtype": "Int", "width": 350},
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
    conditions = ["1=1"]
    params = {"start_date": start_date, "end_date": end_date, "year": year, "month": month}
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
    date_range = filters.get("date_range") if filters else None
    cstart_date, cend_date = (date_range if date_range else (None, None))


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
    if cstart_date or cend_date:
        conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
        params["cstart_date"] = cstart_date if cstart_date else None  
        params["cend_date"] = cend_date if cend_date else None  


    level_mapping = {
        "1": ["s.state_name"],
        "2": ["s.state_name", "d.district_name"],
        "3": ["s.state_name", "d.district_name", "b.block_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name", "c.creche_name"],
    }


    selected_level = filters.get("level", "5")
    group_by_fields = level_mapping.get(selected_level, level_mapping["5"])
    group_by_field = ", ".join(group_by_fields)


    select_fields = [
        "tf.partner AS partner", 
        "tf.state AS state", 
        "tf.district AS district", 
        "tf.block AS block", 
        "tf.gp AS gp", 
        "tf.creche AS creche"
    ]

    selected_fields = []
    for field in select_fields:
        if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
            selected_fields.append(field)

    where_clause = " AND ".join(conditions)


    query = f"""
        SELECT
            {", ".join(selected_fields)},

    tf.e_children AS e_children,
    tf.g_children AS g_children,
    CASE WHEN tf.muw = 0 THEN 0 ELSE FORMAT((tf.muw / tf.e_children)*100.0, 2) END AS muw,
    CASE WHEN tf.suw = 0 THEN 0 ELSE FORMAT((tf.suw / tf.e_children)*100.0, 2) END AS suw,
    CASE WHEN tf.mam = 0 THEN 0 ELSE FORMAT((tf.mam / tf.e_children)*100.0, 2) END AS mam,
    CASE WHEN tf.sam = 0 THEN 0 ELSE FORMAT((tf.sam / tf.e_children)*100.0, 2) END AS sam,
    tf.red_flag AS red_flag,
    tf.red_flag_f AS red_flag_f,
    tf.hf AS hf,
    tf.nrc AS nrc,
    CASE WHEN tf.gf2 = 0 THEN 0 ELSE FORMAT((tf.gf2 / tf.e_children)*100.0, 2) END AS gf2,
    CASE WHEN tf.gf1 = 0 THEN 0 ELSE FORMAT((tf.gf1 / tf.e_children)*100.0, 2) END AS gf1,
    tf.cfu AS cfu,
    tf.weight_for_age_normal,
    tf.weight_for_age_moderate,
    tf.height_for_age_severe,
    
    tf.height_for_age_normal,
    tf.height_for_age_moderate,
    tf.height_for_age_severe,
    
    tf.weight_for_height_normal,
    tf.weight_for_height_moderate,
    tf.weight_for_height_severe
    
FROM (
    SELECT 
        p.partner_name AS partner,
        s.state_name AS state,
        d.district_name AS district,
        b.block_name AS block,
        g.gp_name AS gp,
        v.village_name AS village,
        c.creche_name AS creche,
        c.creche_id as creche_id,
        IFNULL(ec.e_children, 0) AS e_children,
        IFNULL(gc.g_children, 0) AS g_children,
        IFNULL(m.muw, 0) AS muw,
        IFNULL(s.suw, 0) AS suw,
        IFNULL(mm.mam, 0) AS mam,
        IFNULL(ss.sam, 0) AS sam,
        IFNULL(rf.red_flag, 0) AS red_flag,
        IFNULL(rff.red_flag_f, 0) AS red_flag_f,
        IFNULL(h.hf, 0) AS hf,
        IFNULL(nr.nrc, 0) AS nrc,
        IFNULL(gf2c.gf2, 0) AS gf2,
        IFNULL(gf1c.gf1, 0) AS gf1,
        IFNULL(cfu.cfu, 0) AS cfu,
				IFNULL(gmd.weight_for_age_normal, 0) AS weight_for_age_normal,
				IFNULL(gmd.weight_for_age_moderate, 0) AS weight_for_age_moderate,
				IFNULL(gmd.weight_for_age_severe, 0) AS weight_for_age_severe,
				IFNULL(gmd.height_for_age_normal, 0) AS height_for_age_normal,
				IFNULL(gmd.height_for_age_moderate, 0) AS height_for_age_moderate,
				IFNULL(gmd.height_for_age_severe, 0) AS height_for_age_severe,
				IFNULL(gmd.weight_for_height_normal, 0) AS weight_for_height_normal,
				IFNULL(gmd.weight_for_height_moderate, 0) AS weight_for_height_moderate,
				IFNULL(gmd.weight_for_height_severe, 0) AS weight_for_height_severe
    
    FROM 
        tabCreche AS c 
    LEFT JOIN (
        SELECT creche_id, COUNT(*) AS e_children
        FROM `tabChild Enrollment and Exit` AS cep
        WHERE is_active = 1  AND date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit >=  %(start_date)s)
        GROUP BY creche_id
    ) AS ec ON c.name = ec.creche_id

    LEFT JOIN (
          SELECT cgm.creche_id, COUNT(*) AS g_children
        FROM `tabAnthropromatic Data` as ad
        LEFT JOIN `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
        WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) =  %(year)s AND MONTH(cgm.measurement_date) = %(month)s
        GROUP BY cgm.creche_id
    ) AS gc ON c.name = gc.creche_id

LEFT JOIN (SELECT creche_id, COUNT(ad.name) AS gf2
    FROM `tabAnthropromatic Data` AS ad
    JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) = %(year)s AND MONTH(cgm.measurement_date) = %(month)s
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
            AND ad.weight <= ad_same.weight) GROUP by creche_id) AS gf2c
             ON c.name = gf2c.creche_id

LEFT JOIN (SELECT creche_id, COUNT(ad.name) AS gf1  FROM `tabAnthropromatic Data` AS ad
  JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) = %(year)s AND MONTH(cgm.measurement_date) = %(month)s
        AND EXISTS (
            SELECT 1
            FROM `tabAnthropromatic Data` AS ad_same
            WHERE ad_same.childenrollguid = ad.childenrollguid AND ad_same.do_you_have_height_weight = 1 
            AND YEAR(ad_same.measurement_taken_date) = %(lyear)s AND MONTH(ad_same.measurement_taken_date) = %(lmonth)s
            AND ad.weight <= ad_same.weight) GROUP by creche_id) AS gf1c
             ON c.name = gf1c.creche_id

    LEFT JOIN (
        SELECT cgm.creche_id, COUNT(*) AS muw
        FROM `tabAnthropromatic Data` as ad
        JOIN
            `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
        WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) = %(year)s AND MONTH(cgm.measurement_date) = %(month)s
            and ad.weight_for_age = 2
        GROUP BY cgm.creche_id
    ) AS m ON c.name = m.creche_id

    LEFT JOIN (
        SELECT cgm.creche_id, COUNT(*) AS suw
        FROM `tabAnthropromatic Data` as ad
        JOIN
            `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
        WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) = %(year)s AND MONTH(cgm.measurement_date) = %(month)s
            and ad.weight_for_age = 1
        GROUP BY cgm.creche_id
    ) AS s ON c.name = s.creche_id

 LEFT JOIN (
         SELECT cgm.creche_id, COUNT(*) AS mam
        FROM `tabAnthropromatic Data` as ad
        JOIN
            `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
        WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) = %(year)s AND MONTH(cgm.measurement_date) = %(month)s
            and ad.weight_for_height = 2
         GROUP BY cgm.creche_id
    ) AS mm ON c.name = mm.creche_id

    LEFT JOIN (
        SELECT cgm.creche_id, COUNT(*)  AS sam
        FROM `tabAnthropromatic Data` as ad
        JOIN
            `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
        WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) = %(year)s AND MONTH(cgm.measurement_date) = %(month)s
            and ad.weight_for_height = 1
       GROUP BY cgm.creche_id
    ) AS ss ON c.name = ss.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT cep.hhcguid) AS red_flag
        FROM `tabChild Referral` as cr
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
        WHERE is_active = 1  AND date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit >=  %(start_date)s)
        GROUP BY  cep.creche_id
    ) AS rf ON c.name = rf.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT cep.hhcguid) AS red_flag_f
        FROM `tabChild Follow up` as cr
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
        WHERE is_active = 1  AND date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit >=  %(start_date)s)
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
        WHERE is_active = 1  AND date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit >=  %(start_date)s)
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
        WHERE is_active = 1  AND date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit >=  %(start_date)s)
            and cr.referred_to_nrc = 1
        GROUP BY 
            cep.creche_id
    ) AS nr ON c.name = nr.creche_id

    LEFT JOIN (
        SELECT 
            cep.creche_id, 
            COUNT(DISTINCT cep.hhcguid) AS cfu
        FROM `tabChild Follow up` as cr
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
        WHERE is_active = 1  AND date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit >=  %(start_date)s)
            and cr.followup_visit_date <= %(end_date)s
        GROUP BY 
            cep.creche_id
    ) AS cfu ON c.name = cfu.creche_id
    
    LEFT JOIN(
        SELECT 
            cgm.creche_id,
    
            -- Weight for Age
            COUNT(CASE WHEN ad.weight_for_age = 3 THEN 1 END) AS weight_for_age_normal,
            COUNT(CASE WHEN ad.weight_for_age = 2 THEN 1 END) AS weight_for_age_moderate,
            COUNT(CASE WHEN ad.weight_for_age = 1 THEN 1 END) AS weight_for_age_severe,
    
            -- Height for Age
            COUNT(CASE WHEN ad.height_for_age = 3 THEN 1 END) AS height_for_age_normal,
            COUNT(CASE WHEN ad.height_for_age = 2 THEN 1 END) AS height_for_age_moderate,
            COUNT(CASE WHEN ad.height_for_age = 1 THEN 1 END) AS height_for_age_severe,
    
            -- Weight for Height
            COUNT(CASE WHEN ad.weight_for_height = 3 THEN 1 END) AS weight_for_height_normal,
            COUNT(CASE WHEN ad.weight_for_height = 2 THEN 1 END) AS weight_for_height_moderate,
            COUNT(CASE WHEN ad.weight_for_height = 1 THEN 1 END) AS weight_for_height_severe
    
    
        FROM 
            `tabAnthropromatic Data` ad
        LEFT JOIN 
            `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
        WHERE {where_clause}
        GROUP BY {group_by_field}
        ORDER BY {group_by_field}
    """
    data = frappe.db.sql(query, params, as_dict=True)
    return data
