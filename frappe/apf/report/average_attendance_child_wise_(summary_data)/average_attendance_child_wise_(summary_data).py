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
        variable_columns.append({"label": "Creche ID", "fieldname": "c_idx", "fieldtype": "Data", "width": 150})

    fixed_columns = [
        {"label": "Child Name", "fieldname": "name_of_child", "fieldtype": "Data", "width": 190},
        {"label": "Age (in months)", "fieldname": "age_at_enrollment_in_months", "fieldtype": "Int", "width": 190},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 190},
        {"label": "Date of Enrollment", "fieldname": "date_of_enrollment", "fieldtype": "Date", "width": 190},
        {"label": "Gender", "fieldname": "gender_id", "fieldtype": "Data", "width": 190},
        {"label": "Total Eligible Open Days", "fieldname": "Total_eligible_open_days", "fieldtype": "Int", "width": 190},
        {"label": "Total Days Attended", "fieldname": "Total_days_attended", "fieldtype": "Int", "width": 180},
        {"label": "Attendance Percentage", "fieldname": "attendance_percentage", "fieldtype": "Float", "width": 180, "precision": 2},
    ]

    return variable_columns + fixed_columns

def get_data(filters):
    conditions = get_conditions(filters)
    selected_level = filters.get("level", "7")
    
    level_mapping = {
        "1": ["partner_id", "partner_name"],
        "2": ["state_id", "state_name"],
        "3": ["state_id", "state_name", "district_id", "district_name"],
        "4": ["state_id", "state_name", "district_id", "district_name", "block_id", "block_name"],
        "5": ["state_id", "state_name", "district_id", "district_name", "block_id", "block_name", "supervisor_name"],
        "6": ["state_id", "state_name", "district_id", "district_name", "block_id", "block_name", "gp_id", "gp_name"],
        "7": ["state_id", "state_name", "district_id", "district_name", "block_id", "block_name", "gp_id", "gp_name", "c_idx", "creche_name"],
    }
    
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    select_fields = []
    
    for field in group_by_fields:
        select_fields.append(f"cas.{field} AS {field.split('_')[0]}")

    # Get month position (1-12) for extracting from pipe-separated fields
    month_pos = int(filters.get("month", "1")) if filters.get("month") else 1
    
    query = f"""
        SELECT 
            {', '.join(select_fields) if select_fields else ''},
            cas.name_of_child,
            cas.c_idx,
            cas.child_id,
            cas.date_of_enrollment,
            cas.gender_id,
            cas.age_at_enrollment_in_months,
            COALESCE(SUM(
                CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.eligible_days, '|', {month_pos}), '|', -1) AS UNSIGNED)
            ), 0) AS Total_eligible_open_days,
            COALESCE(SUM(
                CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.present_days, '|', {month_pos}), '|', -1) AS UNSIGNED)
            ), 0) AS Total_days_attended,
            CASE 
                WHEN COALESCE(SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.eligible_days, '|', {month_pos}), '|', -1) AS UNSIGNED)), 0) = 0 
                THEN 0
                ELSE ROUND(
                    COALESCE(SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.present_days, '|', {month_pos}), '|', -1) AS UNSIGNED)), 0) * 100 /
                    NULLIF(COALESCE(SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(cas.eligible_days, '|', {month_pos}), '|', -1) AS UNSIGNED)), 0), 1),
                2)
            END AS attendance_percentage
        FROM `tabChild Attendance Summary` AS cas
        WHERE {conditions}
        GROUP BY {', '.join(group_by_fields)}, cas.name_of_child, cas.child_id, cas.date_of_enrollment, cas.gender_id, cas.age_at_enrollment_in_months
        ORDER BY {', '.join(group_by_fields)}, cas.name_of_child
    """
    
    return frappe.db.sql(query, filters, as_dict=True)

def get_conditions(filters):
    conditions = ["1=1"]
    
    if filters.get("year"):
        conditions.append("cas.year = %(year)s")

    if filters.get("partner"):
        conditions.append("cas.partner_id = %(partner)s")

    if filters.get("state"):
        conditions.append("cas.state_id = %(state)s")

    if filters.get("district"):
        conditions.append("cas.district_id = %(district)s")

    if filters.get("block"):
        conditions.append("cas.block_id = %(block)s")

    if filters.get("gp"):
        conditions.append("cas.gp_id = %(gp)s")

    if filters.get("creche"):
        conditions.append("cas.creche_id = %(creche)s")

    if filters.get("supervisor_id"):
        conditions.append("cas.supervisor_id = %(supervisor_id)s")

    if filters.get("creche_status_id"):
        conditions.append("cas.creche_status_id = %(creche_status_id)s")

    if filters.get("phases"):
        phase_list = []
        for p in filters["phases"].split(","):
            p = p.strip()
            if p.isdigit():
                phase_list.append(p)
        
        if phase_list:
            phases_str = ",".join([f"'{p}'" for p in phase_list])
            conditions.append(f"cas.phase IN ({phases_str})")

    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range
            conditions.append("cas.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
            filters.update({"cstart_date": cstart_date, "cend_date": cend_date})

        elif range_type == "before" and single_date:
            conditions.append("cas.creche_opening_date <= %(single_date)s")
            filters.update({"single_date": single_date})

        elif range_type == "after" and single_date:
            conditions.append("cas.creche_opening_date >= %(single_date)s")
            filters.update({"single_date": single_date})

        elif range_type == "equal" and single_date:
            conditions.append("DATE(cas.creche_opening_date) = DATE(%(single_date)s)")
            filters.update({"single_date": single_date})
                
    return " AND ".join(conditions)

def calculate_total_row(data):
    total_row = {
        "state": "Total",
        "Total_eligible_open_days": 0,
        "Total_days_attended": 0,
        "attendance_percentage": 0,
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