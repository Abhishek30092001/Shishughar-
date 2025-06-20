import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate
import calendar
from datetime import datetime, timedelta, date


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def execute(filters=None):
    selected_level = filters.get("level", "7")
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
    if selected_level == "5":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 160})
    if selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
    if selected_level == "7":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 150})
        

    fixed_columns = [
        {"label": _("No. of Creches"), "fieldname": "no_of_creches", "fieldtype": "Data", "width": 180},
        {"label": _("No. of Checkins by Supervisor"), "fieldname": "sup_checkins", "fieldtype": "Data", "width": 250},
        {"label": _("No. of Checkins by CC"), "fieldname": "cc_checkins", "fieldtype": "Data", "width": 250},
        {"label": _("Avg. Checkins per creche by Supervisor"), "fieldname": "avg_sup", "fieldtype": "float", "width": 300},
        {"label": _("Avg. Checkins per creche by CC"), "fieldname": "avg_cc", "fieldtype": "float", "width": 250},

    ]

    columns = variable_columns + fixed_columns
    data = get_data(filters)
    return columns, data


def get_data(filters):

    conditions = get_conditions(filters)
    level_mapping = {
        "1": ["partner.partner_name"],
        "2": ["state.state_name"],
        "3": ["state.state_name", "district.district_name"],
        "4": ["state.state_name", "district.district_name", "block.block_name"],
        "5": ["state.state_name", "district.district_name", "block.block_name", "usr.full_name"],
        "6": ["state.state_name", "district.district_name", "block.block_name", "gp.gp_name"],
        "7": ["state.state_name", "district.district_name", "block.block_name", "gp.gp_name", "creche.creche_name", "creche.creche_id"]
    }
    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)


    select_fields = [
        "partner.partner_name AS partner", 
        "state.state_name AS state", 
        "district.district_name AS district", 
        "block.block_name AS block",
        "gp.gp_name AS gp", 
        "usr.full_name AS supervisor", 
        "creche.creche_name AS creche_name", 
        "creche.creche_id AS creche_id", 
    ]
    selected_fields = []
    for field in select_fields:
        if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
            selected_fields.append(field)

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

    query = f"""

        SELECT 
            {",".join(selected_fields)},
            SUM(CASE WHEN tu.type = 'Creche Supervisor' THEN 1 ELSE 0 END) AS sup_checkins,
            SUM(CASE WHEN tu.type = 'Cluster Coordinator' THEN 1 ELSE 0 END) AS cc_checkins,
            DATE_FORMAT(creche.creche_opening_date, '%d-%m-%Y') AS creche_opening_date,

            ROUND(
                CASE 
                    WHEN COUNT(creche.name) > 0 
                    THEN SUM(CASE WHEN tu.type = 'Creche Supervisor' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
                    ELSE 0 
                END, 1
            ) AS avg_sup,

            ROUND(
                CASE 
                    WHEN COUNT(creche.name) > 0 
                    THEN SUM(CASE WHEN tu.type = 'Cluster Coordinator' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
                    ELSE 0 
                END, 1
            ) AS avg_cc,

            COUNT(DISTINCT creche.name) AS no_of_creches
        FROM 
            `tabCreche` creche
        JOIN 
            `tabPartner` partner ON creche.partner_id = partner.name
        JOIN 
            `tabState` state ON creche.state_id = state.name
        JOIN 
            `tabDistrict` district ON creche.district_id = district.name
        JOIN 
            `tabBlock` block ON creche.block_id = block.name
        JOIN 
            `tabGram Panchayat` gp ON creche.gp_id = gp.name   
        JOIN 
            `tabUser` usr ON usr.name = creche.supervisor_id      
        LEFT JOIN 
            `tabCreche Check In` checkin ON creche.name = checkin.creche_id
            AND checkin.date_of_checkin BETWEEN '{start_date}' AND '{end_date}'
        LEFT JOIN 
            `tabUser` tu ON checkin.appcreated_by = tu.name 
        WHERE 
            {conditions}
        GROUP BY {group_by_field}
        ORDER BY {group_by_field}

    """

    data = frappe.db.sql(query, as_dict=True)

    total_creches = int(sum(row.get('no_of_creches', 0) for row in data))
    total_sup_checkins = int(sum(row.get('sup_checkins', 0) for row in data))
    total_cc_checkins = int(sum(row.get('cc_checkins', 0) for row in data))

    avg_sup = round((total_sup_checkins/ total_creches), 1) if total_creches else 0
    avg_cc = round((total_cc_checkins/ total_creches), 1) if total_creches else 0


    total_row = {
        "partner": "<b style='color:black;'>Total</b>",
        "state": "<b style='color:black;'>Total</b>",
        "no_of_creches": f"<b>{total_creches}</b>",
        "sup_checkins": f"<b>{total_sup_checkins}</b>",
        "cc_checkins": f"<b>{total_cc_checkins}</b>",
        "avg_sup": f"<b>{avg_sup}</b>",
        "avg_cc": f"<b>{avg_cc}</b>"
    }

    data.append(total_row)

    return data

def get_conditions(filters):
    conditions = "1 = 1"
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

    partner = frappe.db.get_value("User", frappe.session.user, "partner")
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
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
    state_id = None

    if filters.get('partner'):
        partner = filters.get('partner')
    if partner:
        conditions += f" AND partner.name = '{partner}'"
    if filters.get("partner"):
        conditions += f" AND partner.name = '{filters.get('partner')}'"

    if filters.get("state"):
        state = filters.get("state")
        conditions += f" AND state.name = '{state}'"
    elif state_ids:
        conditions += f" AND FIND_IN_SET(state.name, '{state_ids}')"

    if filters.get("district"):
        district = filters.get("district")
        conditions += f" AND district.name = '{district}'"
    elif district_ids:
        conditions += f" AND FIND_IN_SET(district.name, '{district_ids}')"
    if filters.get("block"):
        block = filters.get("block")
        conditions += f" AND block.name = '{block}'"
    elif block_ids:
        conditions += f" AND FIND_IN_SET(block.name, '{block_ids}')"
    if filters.get("gp"):
        gp = filters.get("gp")
        conditions += f" AND gp.name = '{gp}'"
    elif gp_ids:
        conditions += f" AND FIND_IN_SET(gp.name, '{gp_ids}')"
    if filters.get("creche"):
        conditions += f" AND creche.name = '{filters.get('creche')}'"
    if filters.get("supervisor_id"):
        conditions += f" AND creche.supervisor_id = '{filters.get('supervisor_id')}'"
    if cstart_date and cend_date:
        conditions += f" AND creche.creche_opening_date BETWEEN {frappe.db.escape(cstart_date)} AND {frappe.db.escape(cend_date)}"
    if filters.get("creche_status_id"):
        conditions += f" AND creche.creche_status_id = '{creche_status_id}'"
    if phases_cleaned:
        conditions += f" AND FIND_IN_SET(creche.phase, {frappe.db.escape(phases_cleaned)})"

    return conditions




