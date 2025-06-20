import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    # Determine the selected level
    selected_level = filters.get("level", "7")
    variable_columns = []

    if selected_level == "1":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
    if selected_level == "2":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
    if selected_level == "3":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
    if selected_level == "4":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
    if selected_level == "5":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180})
    if selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
    if selected_level == "7":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180})

    fixed_columns = [
        {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180},
        {"label": "Cummulative enrolled this month", "fieldname": "cumm_enrolled_children", "fieldtype": "Data", "width": 246},
        {"label": "Enrolled Children in this month", "fieldname": "current_enrolled_children", "fieldtype": "Data", "width": 255},
        {"label": "Measurements taken", "fieldname": "measurements_taken", "fieldtype": "Int", "width": 175},
        {"label": "Severe to Moderate", "fieldname": "sv_md_cnt", "fieldtype": "Int", "width": 175},
        {"label": "Moderate to Normal", "fieldname": "md_nr_cnt", "fieldtype": "Int", "width": 175},
        {"label": "Normal to Moderate ", "fieldname": "nr_md_cnt", "fieldtype": "Int", "width": 175},
        {"label": "Moderate to Severe ", "fieldname": "md_sv_cnt", "fieldtype": "Int", "width": 175},
        {"label": "Retained in the Severe category in this month", "fieldname": "cq_sv_2_cnt", "fieldtype": "Int", "width": 430},
        {"label": "Retained in the Severe category for consecutive 2 months", "fieldname": "cq_sv_3_cnt", "fieldtype": "Int", "width": 430},
        {"label": "Retained in the Severe category for consecutive  3 months", "fieldname": "cq_sv_4_cnt", "fieldtype": "Int", "width": 430},

    ]

    columns = variable_columns + fixed_columns
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
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    conditions = ["1=1"]
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

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "cstart_date": None,
        "cend_date": None,
        "partner": None,
        "state": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
        "supervisor_id": None,
    }


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
    if cstart_date or cend_date:
        conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
        params["cstart_date"] = cstart_date if cstart_date else None  
        params["cend_date"] = cend_date if cend_date else None  


    level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name","u.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "7": ["p.partner_name","s.state_name", "d.district_name", "b.block_name", "g.gp_name", "u.full_name","c.creche_name","c.creche_id"],
    }

    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)

    select_fields = [
        "p.partner_name AS partner",
        "s.state_name AS state",
        "d.district_name AS district",
        "b.block_name AS block",
        "g.gp_name AS gp",
        "u.full_name AS supervisor_id",
        "c.creche_name AS creche",
        "c.creche_id AS creche_id",
    ]

    selected_fields = []
    for field in select_fields:
        if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
            selected_fields.append(field)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            {", ".join(selected_fields)},
             
            IFNULL(sv_md.sv_md_cnt, 0) AS sv_md_cnt,
            IFNULL(md_nr.md_nr_cnt, 0) AS md_nr_cnt,
            IFNULL(nr_md.nr_md_cnt, 0) AS nr_md_cnt,
            IFNULL(md_sv.md_sv_cnt, 0) AS md_sv_cnt,
            IFNULL(cq_sv_2.cq_sv_2_cnt, 0) AS cq_sv_2_cnt,
            IFNULL(cq_sv_3.cq_sv_3_cnt, 0) AS cq_sv_3_cnt,
            IFNULL(cq_sv_4.cq_sv_4_cnt, 0) AS cq_sv_4_cnt,
            IFNULL(crelc.current_enrolled_children, 0) AS current_enrolled_children, 
            COUNT(c.name) AS operational_creches,
            IFNULL(mt.measurements_taken, 0) AS measurements_taken,
            IFNULL(cec.cumm_enrolled_children, 0) AS cumm_enrolled_children
        FROM `tabCreche` c
        JOIN `tabState` s ON c.state_id = s.name
        JOIN `tabPartner` p ON c.partner_id = p.name
        JOIN `tabDistrict` d ON c.district_id = d.name 
        JOIN `tabBlock` b ON c.block_id = b.name 
        JOIN `tabGram Panchayat` g ON c.gp_id = g.name
        JOIN `tabUser` AS u ON u.name = c.supervisor_id
        
        LEFT JOIN (
            SELECT creche_id, COUNT(*) AS current_enrolled_children
            FROM `tabChild Enrollment and Exit`
            WHERE is_active = 1
            AND YEAR(date_of_enrollment) = %(year)s
            AND MONTH(date_of_enrollment) = %(month)s
            AND date_of_exit IS NULL
            AND (%(partner)s IS NULL OR partner_id = %(partner)s)
            AND (%(state)s IS NULL OR state_id = %(state)s)
            AND (%(district)s IS NULL OR district_id = %(district)s)
            AND (%(block)s IS NULL OR block_id = %(block)s)
            AND (%(creche)s IS NULL OR creche_id = %(creche)s)
            GROUP BY creche_id
        ) crelc ON c.name = crelc.creche_id
        
        LEFT JOIN (
            SELECT creche_id, COUNT(*) AS cumm_enrolled_children
            FROM `tabChild Enrollment and Exit`
            WHERE is_active = 1 AND date_of_enrollment <= %(end_date)s
            AND (%(partner)s IS NULL OR partner_id = %(partner)s)
            AND (%(state)s IS NULL OR state_id = %(state)s)
            AND (%(district)s IS NULL OR district_id = %(district)s)
            AND (%(block)s IS NULL OR block_id = %(block)s)
            AND (%(creche)s IS NULL OR creche_id = %(creche)s)
            GROUP BY creche_id
        ) cec ON c.name = cec.creche_id
        LEFT JOIN (
            SELECT 
                cgm.creche_id,
                COUNT(DISTINCT ad.chhguid) AS uc
            FROM `tabAnthropromatic Data` AS ad
            LEFT JOIN `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
            WHERE 
                do_you_have_height_weight = 1 
                AND weight_for_height < 3 
                AND weight_for_height != 0
                AND (%(partner)s IS NULL OR cgm.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR cgm.state_id = %(state)s)
                AND (%(district)s IS NULL OR cgm.district_id = %(district)s)
                AND (%(block)s IS NULL OR cgm.block_id = %(block)s)
                AND (%(creche)s IS NULL OR cgm.creche_id = %(creche)s)
            GROUP BY cgm.creche_id
        ) AS uc ON c.name = uc.creche_id
        LEFT JOIN (
            SELECT 
                creche_id,
                COUNT(ad.parent) AS measurements_taken
            FROM `tabAnthropromatic Data` AS ad
            LEFT JOIN `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
            WHERE 
                MONTH(ad.measurement_taken_date) = MONTH(%(end_date)s) 
                AND YEAR(ad.measurement_taken_date) = YEAR(%(end_date)s)
                AND (%(partner)s IS NULL OR cgm.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR cgm.state_id = %(state)s)
                AND (%(district)s IS NULL OR cgm.district_id = %(district)s)
                AND (%(block)s IS NULL OR cgm.block_id = %(block)s)
                AND (%(creche)s IS NULL OR cgm.creche_id = %(creche)s)
            GROUP BY cgm.creche_id
        ) AS mt ON c.name = mt.creche_id

        LEFT JOIN (
            SELECT 
                COUNT(*) AS sv_md_cnt, 
                tcgm.creche_id
            FROM `tabChild Growth Monitoring` tcgm 
            INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
            INNER JOIN (
                SELECT 
                    tad.chhguid, 
                    tcgm.state_id,
                    tcgm.creche_id
                FROM `tabChild Growth Monitoring` tcgm 
                INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                WHERE  
                    MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))  
                    AND weight_for_height = 1
                    AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                    AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                    AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                    AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                    AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            ) AS PM ON tad.chhguid = PM.chhguid
            WHERE  
                YEAR(tad.measurement_taken_date) = YEAR(%(end_date)s) 
                AND MONTH(tad.measurement_taken_date) = MONTH(%(end_date)s) 
                AND tad.weight_for_height = 2
                AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            GROUP BY tcgm.creche_id
        ) AS sv_md ON sv_md.creche_id = c.name


        LEFT JOIN (
            SELECT 
                COUNT(*) AS md_nr_cnt, 
                tcgm.creche_id
            FROM `tabChild Growth Monitoring` tcgm 
            INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
            INNER JOIN (
                SELECT 
                    tad.chhguid, 
                    tcgm.state_id,
                    tcgm.creche_id
                FROM `tabChild Growth Monitoring` tcgm 
                INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                WHERE  
                    MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND weight_for_height = 2
                    AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                    AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                    AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                    AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                    AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            ) AS PM ON tad.chhguid = PM.chhguid
            WHERE  
                YEAR(tad.measurement_taken_date) = YEAR(%(end_date)s) 
                AND MONTH(tad.measurement_taken_date) = MONTH(%(end_date)s) 
                AND tad.weight_for_height = 3
                AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            GROUP BY tcgm.creche_id
        ) AS md_nr ON md_nr.creche_id = c.name
        
        LEFT JOIN (
            SELECT 
                COUNT(*) AS nr_md_cnt, 
                tcgm.creche_id
            FROM `tabChild Growth Monitoring` tcgm 
            INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
            INNER JOIN (
                SELECT 
                    tad.chhguid, 
                    tcgm.state_id,
                    tcgm.creche_id
                FROM `tabChild Growth Monitoring` tcgm 
                INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                WHERE  
                MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND weight_for_height = 3
                    AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                    AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                    AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                    AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                    AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            ) AS PM ON tad.chhguid = PM.chhguid
            WHERE  
                YEAR(tad.measurement_taken_date) = YEAR(%(end_date)s) 
                AND MONTH(tad.measurement_taken_date) = MONTH(%(end_date)s) 
                AND tad.weight_for_height = 2
                AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            GROUP BY tcgm.creche_id
        ) AS nr_md ON nr_md.creche_id = c.name
        
        
        LEFT JOIN (
            SELECT 
                COUNT(*) AS md_sv_cnt, 
                tcgm.creche_id
            FROM `tabChild Growth Monitoring` tcgm 
            INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
            INNER JOIN (
                SELECT 
                    tad.chhguid, 
                    tcgm.state_id
                FROM `tabChild Growth Monitoring` tcgm 
                INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                WHERE  
                MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND weight_for_height = 2
                    AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                    AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                    AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                    AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                    AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            ) AS PM ON tad.chhguid = PM.chhguid
            WHERE  
            YEAR(tad.measurement_taken_date) = YEAR(%(end_date)s) 
                AND MONTH(tad.measurement_taken_date) = MONTH(%(end_date)s) 
                AND tad.weight_for_height = 1
                AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            GROUP BY tcgm.creche_id
        ) AS md_sv ON md_sv.creche_id = c.name
        
        LEFT JOIN (
            SELECT 
                COUNT(*) AS cq_sv_2_cnt, 
                tcgm.creche_id
            FROM `tabChild Growth Monitoring` tcgm 
            INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
            INNER JOIN (
                SELECT 
                    tad.chhguid, 
                    tcgm.state_id
                FROM `tabChild Growth Monitoring` tcgm 
                INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                WHERE  
                    MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH)) 
                    AND weight_for_height = 1
                    AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                    AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                    AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                    AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                    AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            ) AS PM ON tad.chhguid = PM.chhguid
            WHERE  
                YEAR(tad.measurement_taken_date) = YEAR(%(end_date)s) 
                AND MONTH(tad.measurement_taken_date) = MONTH(%(end_date)s) 
                AND tad.weight_for_height = 1
                AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            GROUP BY tcgm.creche_id
        ) AS cq_sv_2 ON cq_sv_2.creche_id = c.name

        LEFT JOIN (
            SELECT 
                COUNT(*) AS cq_sv_3_cnt, 
                tcgm.creche_id
            FROM `tabChild Growth Monitoring` tcgm 
            INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
            INNER JOIN (
                SELECT 
                    tad.chhguid, 
                    tcgm.state_id
                FROM `tabChild Growth Monitoring` tcgm 
                INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                INNER JOIN (
                    SELECT 
                        tad.chhguid
                    FROM `tabChild Growth Monitoring` tcgm 
                    INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                    WHERE 
                    MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 2 MONTH))
                    AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 2 MONTH))
                    AND weight_for_height = 1
                        AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                        AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                        AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                        AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                        AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
                ) AS PPM ON tad.chhguid = PPM.chhguid
                WHERE  
                MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                    AND weight_for_height = 1
                    AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                    AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                    AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                    AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                    AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            ) AS PM ON tad.chhguid = PM.chhguid
            WHERE  
            YEAR(tad.measurement_taken_date) = YEAR(%(end_date)s) 
                AND MONTH(tad.measurement_taken_date) = MONTH(%(end_date)s) 
                AND tad.weight_for_height = 1
                AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
            GROUP BY tcgm.creche_id

        ) AS cq_sv_3 ON cq_sv_3.creche_id = c.name
        LEFT JOIN (
        SELECT 
            COUNT(*) AS cq_sv_4_cnt, 
            tcgm.creche_id
        FROM `tabChild Growth Monitoring` tcgm 
        INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
        INNER JOIN (
            -- Tracking Month -3
            SELECT 
                tad.chhguid, 
                tcgm.state_id
            FROM `tabChild Growth Monitoring` tcgm 
            INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
            INNER JOIN (

                SELECT 
                    tad.chhguid 
                FROM `tabChild Growth Monitoring` tcgm 
                INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                INNER JOIN (
            
                    SELECT 
                        tad.chhguid 
                    FROM `tabChild Growth Monitoring` tcgm 
                    INNER JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent 
                    WHERE 
                        MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 3 MONTH))
                        AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 3 MONTH))
                        AND tad.weight_for_age = 1
                       AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                        AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                        AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                        AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                        AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
                    ) AS Month_1 ON tad.chhguid = Month_1.chhguid
                    WHERE  
                        MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 2 MONTH))
                        AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 2 MONTH))
                        AND tad.weight_for_age = 1
                        AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                        AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                        AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                        AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                        AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
                    ) AS Month_2 ON tad.chhguid = Month_2.chhguid
                    WHERE  
                        MONTH(tad.measurement_taken_date) = MONTH(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                        AND YEAR(tad.measurement_taken_date) = YEAR(DATE_SUB(%(end_date)s, INTERVAL 1 MONTH))
                        AND tad.weight_for_age = 1
                        AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                        AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                        AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                        AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                        AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
                ) AS Month_3 ON tad.chhguid = Month_3.chhguid
                WHERE  
                    YEAR(tad.measurement_taken_date) = YEAR(%(end_date)s) 
                    AND MONTH(tad.measurement_taken_date) = MONTH(%(end_date)s) 
                    AND tad.weight_for_age = 1
                    AND (%(partner)s IS NULL OR tcgm.partner_id = %(partner)s)
                    AND (%(state)s IS NULL OR tcgm.state_id = %(state)s)
                    AND (%(district)s IS NULL OR tcgm.district_id = %(district)s)
                    AND (%(block)s IS NULL OR tcgm.block_id = %(block)s)
                    AND (%(creche)s IS NULL OR tcgm.creche_id = %(creche)s)
                GROUP BY 
                    tcgm.creche_id
            ) AS cq_sv_4 ON cq_sv_4.creche_id = c.name
            
    WHERE {where_clause}
    GROUP BY {group_by_field}
    ORDER BY {group_by_field}
    """

    data = frappe.db.sql(query, params, as_dict=True)
    return data