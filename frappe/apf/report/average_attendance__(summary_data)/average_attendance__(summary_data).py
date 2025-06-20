# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    # Calculate totals if there's data
    if data:
        total_row = calculate_total_row(data)
        data.append(total_row)
    return columns, data

def get_columns(filters):
    selected_level = filters.get("level", "7")
    
    variable_columns = []
    if selected_level == "1":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Link", "options": "Partner", "width": 160})
    if selected_level == "2":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Link", "options": "State", "width": 160})
    if selected_level == "3":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Link", "options": "State", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Link", "options": "District", "width": 160})
    if selected_level == "4":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Link", "options": "State", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Link", "options": "District", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Link", "options": "Block", "width": 160})
    if selected_level == "5":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Link", "options": "State", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Link", "options": "District", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Link", "options": "Block", "width": 160})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Link", "options": "User", "width": 160})
    if selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Link", "options": "State", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Link", "options": "District", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Link", "options": "Block", "width": 160})
        variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Link", "options": "Gram Panchayat", "width": 160})
    if selected_level == "7":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Link", "options": "State", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Link", "options": "District", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Link", "options": "Block", "width": 160})
        variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Link", "options": "Gram Panchayat", "width": 160})
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Link", "options": "Creche", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})


    fixed_columns = [
        {"label": "Active Creche", "fieldname": "active_creche", "fieldtype": "data", "width": 140},
        {"label": "Eligible Children", "fieldname": "eligible_children", "fieldtype": "Int", "width": 140},
        {"label": "Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Int", "width": 140},
        {"label": "Enrolled Children (%)", "fieldname": "avgpereli", "fieldtype": "float", "width": 200},
        {"label": "Children Attended at least one day", "fieldname": "children_attendance_atleast_one_day", "fieldtype": "Int", "width": 280},
        {"label": "Children Attended (%)", "fieldname": "avgperenroll", "fieldtype": "float", "width": 200},
        {"label": "Total Eligible Open Days", "fieldname": "Total_eligible_open_days", "fieldtype": "Int", "width": 190},
        {"label": "Total Days Attended", "fieldname": "Total_days_attended", "fieldtype": "Int", "width": 180},
        {"label": "Attendance Percentage", "fieldname": "attendance_percentage", "fieldtype": "Float", "width": 180, "precision": 2},
        {"label": "Avg Attendance Per Day", "fieldname": "avg_attd_per_day", "fieldtype": "Float", "width": 190, "precision": 2},

        {"label": "Min Attendance", "fieldname": "min_attd", "fieldtype": "Int", "width": 160},
        {"label": "Mean Attendance", "fieldname": "mean_attd", "fieldtype": "Int", "width": 160},
        {"label": "Max Attendance", "fieldname": "max_attd", "fieldtype": "Int", "width": 160},
        
        # {"label": "0% Attendance", "fieldname": "E0", "fieldtype": "Int", "width": 160},
        # {"label": ">0% to <25%", "fieldname": "G0toL25", "fieldtype": "Int", "width": 160},
        # {"label": "25% to <50%", "fieldname": "25toL50", "fieldtype": "Int", "width": 160},
        # {"label": "50% to <75%", "fieldname": "50toL75", "fieldtype": "Int", "width": 160},
        # {"label": "75% to <100%", "fieldname": "75toL100", "fieldtype": "Int", "width": 170},
        # {"label": "100% Attendance", "fieldname": "E100", "fieldtype": "Int", "width": 180},

        {"label": "Attendance (0%)", "fieldname": "E0", "fieldtype": "Int", "width": 250},
        {"label": "Attendance (> 0% to < 25%)", "fieldname": "G0toL25", "fieldtype": "Int", "width": 280},
        {"label": "Attendance (25% to < 50%)", "fieldname": "25toL50", "fieldtype": "Int", "width": 250}, 
        
        {"label": "Attendance (50% to < 75%)", "fieldname": "50toL75", "fieldtype": "Int", "width": 250},
        {"label": "Attendance (75% to < 100%)", "fieldname": "75toL100", "fieldtype": "Int", "width": 280},
        {"label": "Attendance (100%)", "fieldname": "E100", "fieldtype": "Int", "width": 250}   
    ]

    return variable_columns + fixed_columns

def get_data(filters):
    conditions = get_conditions(filters)
    selected_level = filters.get("level", "7")
    
    level_mapping = {
        "1": ["partner"],
        "2": ["state"],
        "3": ["state", "district"],
        "4": ["state", "district", "block"],
        "5": ["state", "district", "block", "supervisor"],
        "6": ["state", "district", "block", "gp"],
        "7": ["state", "district", "block", "gp", "creche", "creche_id"],
    }
    
    group_by_fields = level_mapping.get(selected_level, ["7"])
    group_by_clause = ", ".join(group_by_fields) if group_by_fields else ""
    
    select_fields = []
    for field in group_by_fields:
        select_fields.append(f"FT.{field} AS {field}")
    
    # Get month position (1-12) for extracting from pipe-separated fields
    month_pos = int(filters.get("month", "1")) if filters.get("month") else 1
    
    query = f"""
        SELECT 
            {', '.join(select_fields) if select_fields else ''},
            SUM(active_creche) AS active_creche,
            SUM(eligible_children) AS eligible_children,
            SUM(enrolled_children) AS enrolled_children,
            CASE WHEN SUM(eligible_children) = 0 THEN 0 ELSE FORMAT(( SUM(enrolled_children) / SUM(eligible_children))*100.0, 2) END AS avgpereli,
            SUM(min_attd) AS min_attd,
            SUM(max_attd) AS max_attd,
            SUM(Total_eligible_open_days) AS Total_eligible_open_days,
            SUM(Total_days_attended) AS Total_days_attended,
            CASE WHEN SUM(enrolled_children) = 0 THEN 0 ELSE FORMAT(( SUM(children_attendance_atleast_one_day) /  SUM(enrolled_children))*100.0, 2) END AS avgperenroll,
            SUM(E0) AS E0,
            SUM(G0toL25) AS G0toL25,
            SUM(`25toL50`) AS `25toL50`,
            SUM(`50toL75`) AS `50toL75`,
            SUM(`75toL100`) AS `75toL100`,
            SUM(E100) AS E100,
            ROUND(SUM(mean_attd), 2) AS mean_attd,
            ROUND(SUM(avg_attd_per_day), 2) AS avg_attd_per_day,
            ROUND(SUM(children_attendance_atleast_one_day), 2) AS children_attendance_atleast_one_day,
            CASE 
                WHEN SUM(Total_eligible_open_days) = 0 THEN 0 
                ELSE ROUND(SUM(Total_days_attended) * 100.0 / SUM(Total_eligible_open_days), 2)
            END AS attendance_percentage
        FROM (
            SELECT 
                CASE WHEN cs.name IS NOT NULL THEN 1 ELSE 0 END AS active_creche, 
                cs.partner_name AS partner,
                cs.state_name AS state,
                cs.district_name AS district,
                cs.block_name AS block,
                cs.gp_name AS gp,
                cs.c_idx AS creche_id,
                cs.creche_name AS creche,
                cs.supervisor_name AS supervisor,
                COALESCE(casd.Total_eligible_open_days, 0) AS Total_eligible_open_days,
                COALESCE(casd.Total_days_attended, 0) AS Total_days_attended,
                COALESCE(casd.E0, 0) AS E0,
                COALESCE(casd.G0toL25, 0) AS G0toL25,
                COALESCE(casd.25toL50, 0) AS 25toL50,
                COALESCE(casd.50toL75, 0) AS 50toL75,
                COALESCE(casd.75toL100, 0) AS 75toL100,
                COALESCE(casd.E100, 0) AS E100,
                COALESCE(casd.attendance_percentage, 0) AS attendance_percentage,
                COALESCE(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cs.eligible_children, '|', {month_pos}), '|', -1) AS UNSIGNED), 0) AS eligible_children,
                COALESCE(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cs.enrolled_children, '|', {month_pos}), '|', -1) AS UNSIGNED), 0) AS enrolled_children,
                COALESCE(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cs.avg_attd_per_day, '|', {month_pos}), '|', -1) AS DECIMAL(10,2)), 0) AS avg_attd_per_day,
                COALESCE(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cs.children_attendance_atleast_one_day, '|', {month_pos}), '|', -1) AS DECIMAL(10,2)), 0) AS children_attendance_atleast_one_day,
                COALESCE(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cs.min_attd, '|', {month_pos}), '|', -1) AS UNSIGNED), 0) AS min_attd,
                COALESCE(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cs.mean_attd, '|', {month_pos}), '|', -1) AS DECIMAL(10,2)), 0) AS mean_attd,
                COALESCE(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cs.max_attd, '|', {month_pos}), '|', -1) AS UNSIGNED), 0) AS max_attd,
                CASE 
                    WHEN COALESCE(casd.attendance_percentage, 0) = 0 THEN 0
                    WHEN COALESCE(casd.attendance_percentage, 0) BETWEEN 0 AND 25 THEN 1
                    WHEN COALESCE(casd.attendance_percentage, 0) BETWEEN 26 AND 50 THEN 2
                    WHEN COALESCE(casd.attendance_percentage, 0) BETWEEN 51 AND 75 THEN 3
                    WHEN COALESCE(casd.attendance_percentage, 0) BETWEEN 76 AND 100 THEN 4
                    ELSE 0 
                END AS band
            FROM `tabCreche Summary` cs
            LEFT JOIN (
                SELECT 
                    cas.creche_id,
                    COALESCE(SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.eligible_days, '|', {month_pos}), '|', -1) AS UNSIGNED)), 0) AS Total_eligible_open_days,
                    COALESCE(SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.present_days, '|', {month_pos}), '|', -1) AS UNSIGNED)), 0) AS Total_days_attended,
                    SUM(CASE WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(cas.attend_slot, '|', {month_pos}), '|', -1) = '0' THEN 1 ELSE 0 END) AS E0,
                    SUM(CASE WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(cas.attend_slot, '|', {month_pos}), '|', -1) = '1' THEN 1 ELSE 0 END) AS G0toL25,
                    SUM(CASE WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(cas.attend_slot, '|', {month_pos}), '|', -1) = '2' THEN 1 ELSE 0 END) AS 25toL50,
                    SUM(CASE WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(cas.attend_slot, '|', {month_pos}), '|', -1) = '3' THEN 1 ELSE 0 END) AS 50toL75,
                    SUM(CASE WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(cas.attend_slot, '|', {month_pos}), '|', -1) = '4' THEN 1 ELSE 0 END) AS 75toL100,
                    SUM(CASE WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(cas.attend_slot, '|', {month_pos}), '|', -1) = '5' THEN 1 ELSE 0 END) AS E100,
                    CASE 
                        WHEN COALESCE(SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.eligible_days, '|', {month_pos}), '|', -1) AS UNSIGNED)), 0) = 0 THEN 0
                        ELSE ROUND(
                            COALESCE(SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.present_days, '|', {month_pos}), '|', -1) AS UNSIGNED)), 0) * 100 / 
                            COALESCE(SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.eligible_days, '|', {month_pos}), '|', -1) AS UNSIGNED)), 1),
                            2
                        )
                    END AS attendance_percentage
                FROM `tabChild Attendance Summary` cas
                WHERE cas.year = %(year)s
                GROUP BY cas.creche_id
            ) as casd ON casd.creche_id = cs.c_name
            WHERE {conditions}
        ) AS FT
        {f"GROUP BY {group_by_clause}" if group_by_clause else ""}
        {f"ORDER BY {group_by_clause}" if group_by_clause else ""}
    """
    return frappe.db.sql(query, filters, as_dict=True)

def get_conditions(filters):
    conditions = ["1=1"]
    
    if filters.get("year"):
        conditions.append("cs.year = %(year)s")

    if filters.get("partner"):
        conditions.append("cs.partner_id = %(partner)s")

    if filters.get("state"):
        conditions.append("cs.state_id = %(state)s")

    if filters.get("district"):
        conditions.append("cs.district_id = %(district)s")

    if filters.get("block"):
        conditions.append("cs.block_id = %(block)s")

    if filters.get("gp"):
        conditions.append("cs.gp_id = %(gp)s")

    if filters.get("creche"):
        conditions.append("cs.c_name = %(creche)s")

    if filters.get("supervisor_id"):
        conditions.append("cs.supervisor_id = %(supervisor_id)s")

    if filters.get("creche_status_id"):
        conditions.append("cs.creche_status_id = %(creche_status_id)s")

    if filters.get("phases"):
        phase_list = []
        for p in filters["phases"].split(","):
            p = p.strip()
            if p.isdigit():
                phase_list.append(p)
        
        if phase_list:
            phases_str = ",".join([f"'{p}'" for p in phase_list])
            conditions.append(f"cs.phase IN ({phases_str})")
            
    if filters.get("band"):
        band_value = int(filters.get("band"))
        conditions.append("""
            CASE 
                WHEN COALESCE(casd.attendance_percentage, 0) = 0 THEN 0
                WHEN COALESCE(casd.attendance_percentage, 0) BETWEEN 0 AND 25 THEN 1
                WHEN COALESCE(casd.attendance_percentage, 0) BETWEEN 26 AND 50 THEN 2
                WHEN COALESCE(casd.attendance_percentage, 0) BETWEEN 51 AND 75 THEN 3
                WHEN COALESCE(casd.attendance_percentage, 0) BETWEEN 76 AND 100 THEN 4
                ELSE 0 
            END = %(band)s
        """)
        filters.update({"band": band_value})

    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range
            conditions.append("cs.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
            filters.update({"cstart_date": cstart_date, "cend_date": cend_date})

        elif range_type == "before" and single_date:
            conditions.append("cs.creche_opening_date <= %(single_date)s")
            filters.update({"single_date": single_date})

        elif range_type == "after" and single_date:
            conditions.append("cs.creche_opening_date >= %(single_date)s")
            filters.update({"single_date": single_date})

        elif range_type == "equal" and single_date:
            conditions.append("DATE(cs.creche_opening_date) = DATE(%(single_date)s)")
            filters.update({"single_date": single_date})
                
    return " AND ".join(conditions)


def calculate_total_row(data):
    total_row = {
        "state": f"<b style='color:black;'>Total</b>",
        "active_creche": 0,
        "eligible_children": 0,
        "enrolled_children": 0,
        "children_attendance_atleast_one_day": 0,
        "Total_eligible_open_days": 0,
        "Total_days_attended": 0,
        "attendance_percentage": 0,
        "min_attd": 0,
        "mean_attd": 0,
        "max_attd": 0,
        "E0": 0,
        "G0toL25": 0,
        "25toL50": 0,
        "50toL75": 0,
        "75toL100": 0,
        "E100": 0,
    }
    
    # Sum all numeric values
    for row in data:
        for field in total_row:
            if field != "state" and row.get(field):
                total_row[field] += row[field]
    
    # Calculate average attendance percentage
    if total_row["Total_eligible_open_days"] > 0:
        total_row["attendance_percentage"] = round(
            (total_row["Total_days_attended"] * 100) / total_row["Total_eligible_open_days"], 
            2
        )
    
    return total_row