import frappe
from frappe import _
from datetime import date
import calendar

def execute(filters=None):
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
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
    if selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
    if selected_level == "7":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})

    fixed_columns = [
        {"label": _("Operational Creches"), "fieldname": "op_creches", "fieldtype": "Int", "width": 250,},
        {"label": _("Eligible Children"), "fieldname": "e_children", "fieldtype": "Int", "width": 250},
        {"label": _("Cumulative Enrollment"), "fieldname": "cumulative_enrollment", "fieldtype": "Int", "width": 250},
        {"label": _("New Enrollment"), "fieldname": "new_enrollment", "fieldtype": "Int", "width": 250},
        {"label": _("Currently Active"), "fieldname": "currently_active", "fieldtype": "Int", "width": 150},
        {"label": _("Total Cumulative Exit"), "fieldname": "total_cumulative_exit", "fieldtype": "Int", "width": 250},
        {"label": _("Total Cumulative Migrated"), "fieldname": "total_cumulative_mig", "fieldtype": "Int", "width": 250},
        {"label": _("Total Cumulative Graduated"), "fieldname": "total_cumulative_grad", "fieldtype": "Int", "width": 250},
        {"label": _("Total Cumulative Not Willing to Stay"), "fieldname": "total_cumulative_nwts", "fieldtype": "Int", "width": 250},
        {"label": _("Total Cumulative Death"), "fieldname": "total_cumulative_death", "fieldtype": "Int", "width": 250},
        {"label": _("Total Cumulative Other"), "fieldname": "total_cumulative_othr", "fieldtype": "Int", "width": 250},
        {"label": _("Total Exit (This Period)"), "fieldname": "new_exit", "fieldtype": "Int", "width": 250},
        {"label": _("Migrated"), "fieldname": "reason_1", "fieldtype": "Int", "width": 150},
        {"label": _("Graduated"), "fieldname": "reason_2", "fieldtype": "Int", "width": 150},
        {"label": _("Not Willing to Stay"), "fieldname": "reason_3", "fieldtype": "Int", "width": 150},
        {"label": _("Death"), "fieldname": "reason_4", "fieldtype": "Int", "width": 150},
        {"label": _("Other"), "fieldname": "reason_5", "fieldtype": "Int", "width": 150},
    ]

    columns = variable_columns + fixed_columns
    data = get_report_data(filters)
    return columns, data

def get_report_data(filters):

     # date range logic starts here
    start_date, end_date = None, None

    if(filters.get("time_range")):
        time_range = filters.get("time_range") if filters else None
        start_date, end_date = (time_range if time_range else (None, None))
    
    elif(filters.get("year") and filters.get("month")):
        current_date = date.today()
        month = int(filters.get("month")) if filters.get("month") else current_date.month
        year = int(filters.get("year")) if filters.get("year") else current_date.year
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

    # date range logic ends here

    conditions = ["1=1"]
    params = {
        "start_date": start_date,
        "end_date": end_date, 
        "partner": None,
        "state":  None,
        "district":  None,
        "block": None,
        "gp": None,
        "creche": None
    }
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
    if filters.get("creche_status_id"):
        conditions.append("(c.creche_status_id = %(creche_status_id)s)")
        params["creche_status_id"] = filters.get("creche_status_id")
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
        if phases_cleaned:  
            conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
            params["phases"] = phases_cleaned

    level_mapping = {
        "1": ["tp.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "tu.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "7": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name", "c.creche_name","c.creche_id"],
    }


    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)

    select_fields = [
        "tp.partner_name AS partner",
        "s.state_name AS state",
        "d.district_name AS district",
        "b.block_name AS block",
        "tu.full_name AS supervisor",
        "g.gp_name AS gp",
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
            IFNULL(SUM(cuenroll.cumulative_enrollment), 0) AS cumulative_enrollment,
            IFNULL(SUM(nwcuenroll.new_enrollment), 0) AS new_enrollment,
            IFNULL(SUM(cuenroll.currently_active), 0) AS currently_active,
            IFNULL(SUM(cuenroll.total_cumulative_exit), 0) AS total_cumulative_exit,
            IFNULL(SUM(cuenroll.total_cumulative_mig), 0) AS total_cumulative_mig,
            IFNULL(SUM(cuenroll.total_cumulative_grad), 0) AS total_cumulative_grad,
            IFNULL(SUM(cuenroll.total_cumulative_nwts), 0) AS total_cumulative_nwts,
            IFNULL(SUM(cuenroll.total_cumulative_death), 0) AS total_cumulative_death,
            IFNULL(SUM(cuenroll.total_cumulative_othr), 0) AS total_cumulative_othr,
            IFNULL(SUM(nwexit.new_exit), 0) AS new_exit,
            IFNULL(SUM(rext.reason_1), 0) AS reason_1,
            IFNULL(SUM(rext.reason_2), 0) AS reason_2,
            IFNULL(SUM(rext.reason_3), 0) AS reason_3,
            IFNULL(SUM(rext.reason_4), 0) AS reason_4,
            IFNULL(SUM(rext.reason_5), 0) AS reason_5,
            IFNULL(SUM(ec.e_children), 0) AS e_children,
            IFNULL(COUNT(*), 0) AS op_creches
        FROM
            `tabCreche` c
        INNER JOIN `tabState` s ON c.state_id = s.name
        INNER JOIN `tabDistrict` d ON c.district_id = d.name
        INNER JOIN `tabBlock` b ON c.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
        INNER JOIN tabPartner tp ON c.partner_id = tp.name 
        INNER JOIN  tabUser tu ON c.supervisor_id = tu.name
        LEFT JOIN (
            SELECT creche_id, COUNT(*) AS cumulative_enrollment,
                   SUM(CASE WHEN date_of_exit IS null or date_of_exit >  %(end_date)s THEN 1 ELSE 0 END) AS currently_active,
                   SUM(CASE WHEN date_of_exit <=  %(end_date)s THEN 1 ELSE 0 END) AS total_cumulative_exit,
                   SUM(CASE WHEN date_of_exit <=  %(end_date)s AND reason_for_exit = 1 THEN 1 ELSE 0 END) AS total_cumulative_mig,
                   SUM(CASE WHEN date_of_exit <=  %(end_date)s AND reason_for_exit = 2 THEN 1 ELSE 0 END) AS total_cumulative_grad,
                   SUM(CASE WHEN date_of_exit <=  %(end_date)s AND reason_for_exit = 3 THEN 1 ELSE 0 END) AS total_cumulative_nwts,
                   SUM(CASE WHEN date_of_exit <=  %(end_date)s AND reason_for_exit = 4 THEN 1 ELSE 0 END) AS total_cumulative_death,
                   SUM(CASE WHEN date_of_exit <=  %(end_date)s AND reason_for_exit = 5 THEN 1 ELSE 0 END) AS total_cumulative_othr
            FROM `tabChild Enrollment and Exit` as ceex
            WHERE ceex.date_of_enrollment <= %(end_date)s
            AND (%(partner)s IS NULL OR ceex.partner_id = %(partner)s) 
            AND (%(state)s IS NULL OR ceex.state_id = %(state)s) 
            AND (%(district)s IS NULL OR ceex.district_id = %(district)s)
            AND (%(block)s IS NULL OR ceex.block_id = %(block)s)
            AND (%(gp)s IS NULL OR ceex.gp_id = %(gp)s)
            AND (%(creche)s IS NULL OR ceex.creche_id = %(creche)s)
            GROUP BY creche_id
        ) AS cuenroll ON cuenroll.creche_id = c.name
        LEFT JOIN (
            SELECT creche_id, COUNT(*) AS new_enrollment
            FROM `tabChild Enrollment and Exit` as ceex
            WHERE ceex.date_of_enrollment BETWEEN %(start_date)s AND %(end_date)s
            AND (%(partner)s IS NULL OR ceex.partner_id = %(partner)s) 
            AND (%(state)s IS NULL OR ceex.state_id = %(state)s) 
            AND (%(district)s IS NULL OR ceex.district_id = %(district)s)
            AND (%(block)s IS NULL OR ceex.block_id = %(block)s)
            AND (%(gp)s IS NULL OR ceex.gp_id = %(gp)s)
            AND (%(creche)s IS NULL OR ceex.creche_id = %(creche)s)
            GROUP BY creche_id
        ) AS nwcuenroll ON nwcuenroll.creche_id = c.name
        LEFT JOIN (
            SELECT creche_id,
                   SUM(CASE WHEN date_of_exit IS NOT NULL THEN 1 ELSE 0 END) AS new_exit
            FROM `tabChild Enrollment and Exit` as ceex
            WHERE ceex.date_of_exit BETWEEN %(start_date)s AND %(end_date)s
            AND (%(partner)s IS NULL OR ceex.partner_id = %(partner)s) 
            AND (%(state)s IS NULL OR ceex.state_id = %(state)s) 
            AND (%(district)s IS NULL OR ceex.district_id = %(district)s)
            AND (%(block)s IS NULL OR ceex.block_id = %(block)s)
            AND (%(gp)s IS NULL OR ceex.gp_id = %(gp)s)
            AND (%(creche)s IS NULL OR ceex.creche_id = %(creche)s)
            GROUP BY creche_id
        ) AS nwexit ON nwexit.creche_id = c.name
        LEFT JOIN (
            SELECT creche_id,
                   SUM(CASE WHEN reason_for_exit = 1 THEN 1 ELSE 0 END) AS reason_1,
                   SUM(CASE WHEN reason_for_exit = 2 THEN 1 ELSE 0 END) AS reason_2,
                   SUM(CASE WHEN reason_for_exit = 3 THEN 1 ELSE 0 END) AS reason_3,
                   SUM(CASE WHEN reason_for_exit = 4 THEN 1 ELSE 0 END) AS reason_4,
                   SUM(CASE WHEN reason_for_exit = 5 THEN 1 ELSE 0 END) AS reason_5
            FROM `tabChild Enrollment and Exit` as ceex
            WHERE ceex.date_of_exit BETWEEN %(start_date)s AND %(end_date)s
            AND (%(partner)s IS NULL OR ceex.partner_id = %(partner)s) 
            AND (%(state)s IS NULL OR ceex.state_id = %(state)s) 
            AND (%(district)s IS NULL OR ceex.district_id = %(district)s)
            AND (%(block)s IS NULL OR ceex.block_id = %(block)s)
            AND (%(gp)s IS NULL OR ceex.gp_id = %(gp)s)
            AND (%(creche)s IS NULL OR ceex.creche_id = %(creche)s)
            GROUP BY creche_id
        ) AS rext ON rext.creche_id = c.name
         LEFT JOIN (
                SELECT hf.creche_id, COUNT(hhc.hhcguid) AS e_children
                FROM `tabHousehold Child Form` AS hhc 
                JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
                WHERE hhc.creation <= %(end_date)s AND hhc.is_dob_available = 1 AND TIMESTAMPDIFF(MONTH, hhc.child_dob, %(end_date)s) BETWEEN 6 AND 36
                AND (%(partner)s IS NULL OR hf.partner_id = %(partner)s) 
                AND (%(state)s IS NULL OR hf.state_id = %(state)s) 
                AND (%(district)s IS NULL OR hf.district_id = %(district)s)
                AND (%(block)s IS NULL OR hf.block_id = %(block)s)
                AND (%(gp)s IS NULL OR hf.gp_id = %(gp)s)
                AND (%(creche)s IS NULL OR hf.creche_id = %(creche)s)
                GROUP BY hf.creche_id
            ) AS ec ON ec.creche_id = c.name
        WHERE {where_clause}
        GROUP BY {group_by_field}
        ORDER BY {group_by_field}
    """
    data = frappe.db.sql(query, params, as_dict=True)
    return data
