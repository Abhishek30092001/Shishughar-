import frappe
from frappe import _
from datetime import date
import calendar

def execute(filters=None):
    # Define columns based on the selected level
    selected_level = filters.get("level", "4")
    variable_columns = []

    if selected_level == "1":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 160})
    if selected_level == "2":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
    if selected_level == "3":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
    if selected_level == "4":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})

    fixed_columns = [
        {"label": "No. of Creches Planned", "fieldname": "planned", "fieldtype": "Int", "width": 230},
        {"label": "No. of Operational Creches", "fieldname": "no_operational_creches", "fieldtype": "Int", "width": 250},
        {"label": "No. of Creches yet to be Operationalized", "fieldname": "yet_to_operationalised", "fieldtype": "Int", "width": 300},
    ]
    columns = variable_columns + fixed_columns
    data = get_summary_data(filters)

     
    
    # Calculate totals
    total_planned = sum(row.get("planned", 0) for row in data)
    total_operational = sum(row.get("no_operational_creches", 0) for row in data)
    total_yet_to_operationalize = total_planned - total_operational

    # Add total row (only if there's data)
    if data:
        total_row = {
            "partner": "Total",
            "state": "Total",
            "district": "",
            "block": "",
            "planned": total_planned,
            "no_operational_creches": total_operational,
            "yet_to_operationalised": total_yet_to_operationalize,
        }
        data.append(total_row)
    
    return columns, data


def get_summary_data(filters):
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))

    conditions = ["1=1"]
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "partner": partner_id,
        "state": state_ids,
        "district": district_ids,
        "block": block_ids,
        "partner": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
    }

    if partner_id:
        conditions.append("tcp.partner_id = %(partner)s")
        params["partner"] = partner_id

    if filters.get("state"):
        conditions.append("tcp.state_id = %(state)s")
        params["state"] = filters.get("state")
        params["state_ids"] = None
    else:
        if state_ids:
            conditions.append("FIND_IN_SET(tcp.state_id, %(state_ids)s)")
            params["state_ids"] = state_ids
            params["state"] = None

    if filters.get("district"):
        conditions.append("tcp.district_id = %(district)s")
        params["district"] = filters.get("district")
        params["district_ids"] = None
    else:
        if district_ids:
            conditions.append("FIND_IN_SET(tcp.district_id, %(district_ids)s)")
            params["district_ids"] = district_ids
            params["district"] = None

    if filters.get("block"):
        conditions.append("tcp.block_id = %(block)s")
        params["block"] = filters.get("block")
        params["block_ids"] = None
    else:
        if block_ids:
            conditions.append("FIND_IN_SET(tcp.block_id, %(block_ids)s)")
            params["block_ids"] = block_ids
            params["block"] = None

    if filters.get("creche"):
        conditions.append("tcp.name = %(creche)s")
        params["creche"] = filters.get("creche")

    date_range = filters.get("date_range") if filters else None
    cstart_date, cend_date = (date_range if date_range else (None, None))

    if cstart_date and cend_date:
        conditions.append("(cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
        params["cstart_date"] = cstart_date
        params["cend_date"] = cend_date

    level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
    }

    selected_level = filters.get("level", "4")
    group_by_fields = level_mapping.get(selected_level, level_mapping["4"])
    group_by_field = ", ".join(group_by_fields)

    select_fields = [
        "p.partner_name AS partner",
        "s.state_name AS state",
        "d.district_name AS district",
        "b.block_name AS block",
    ]

    selected_fields = []
    for field in select_fields:
        field_name = field.split(" AS ")[0].split(".")[1]
        if field_name in [group_by_field.split(".")[1] for group_by_field in group_by_fields]:
            selected_fields.append(field)

    where_clause = " AND ".join(conditions)

    # Dynamic GROUP BY for subquery based on selected level
    subquery_group_by_mapping = {
        "1": ["tc.partner_id"],
        "2": ["tc.state_id"],
        "3": ["tc.state_id", "tc.district_id"],
        "4": ["tc.state_id", "tc.district_id", "tc.block_id"],
    }
    subquery_group_by_fields = subquery_group_by_mapping.get(selected_level, subquery_group_by_mapping["4"])
    subquery_group_by_clause = ", ".join(subquery_group_by_fields)

    query = f"""
        SELECT
            {", ".join(selected_fields)},
            SUM(tcp.planned) AS planned,
            IFNULL(opr_cr.opr_creche, 0) AS no_operational_creches,
            GREATEST(0, IFNULL(SUM(tcp.planned), 0) - IFNULL(opr_cr.opr_creche, 0)) AS yet_to_operationalised
        FROM
            `tabCreche Planned` tcp
        INNER JOIN
            tabYear ty ON tcp.year = ty.name
        INNER JOIN
            `tabPartner` AS p ON tcp.partner_id = p.name
        INNER JOIN
            `tabState` AS s ON tcp.state_id = s.name
        INNER JOIN
            `tabDistrict` AS d ON tcp.district_id = d.name
        INNER JOIN
            `tabBlock` AS b ON tcp.block_id = b.name
        LEFT JOIN (
            SELECT
                tc.partner_id,
                tc.state_id,
                tc.district_id,
                tc.block_id,
                COUNT(*) AS opr_creche
            FROM
                `tabCreche` AS tc
            WHERE   
                (tc.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s))
                AND (%(partner)s IS NULL OR tc.partner_id = %(partner)s)
                AND tc.creche_status_id = 3
                AND (%(state)s IS NULL OR tc.state_id = %(state)s)
                AND (%(district)s IS NULL OR tc.district_id = %(district)s)
                AND (%(block)s IS NULL OR tc.block_id = %(block)s)
            GROUP BY
                {subquery_group_by_clause}
        ) opr_cr ON opr_cr.block_id = tcp.block_id AND opr_cr.partner_id = tcp.partner_id
        WHERE
            {where_clause} AND ty.year * 1000 + tcp.month * 10 <= %(year)s * 1000 + %(month)s * 10
        GROUP BY {group_by_field}
        ORDER BY {group_by_field}
    """
    data = frappe.db.sql(query, params, as_dict=True)
    return data





