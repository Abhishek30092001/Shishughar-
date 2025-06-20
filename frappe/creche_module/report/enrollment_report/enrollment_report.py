import frappe
from frappe.utils import nowdate
from datetime import date

def execute(filters=None):
    columns, data = [], []
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    selected_year = filters.get("year") or nowdate().split('-')[0]
    selected_month = filters.get("month") or nowdate().split('-')[1]

    columns = [
        # {"label": "Seq. No", "fieldname": "idx", "fieldtype": "Int", "width": 60},
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "crecheid", "fieldtype": "Data", "width": 120}
    ]

    for month in months:
        month_label = f"{month[:3]}-{selected_year}"
        columns.append({"label": month_label, "fieldname": month.lower(), "fieldtype": "Int", "width": 120})

    data = get_enrollment_data(filters)

    for idx, row in enumerate(data, start=1):
        row['idx'] = idx

    return columns, data

@frappe.whitelist()
def get_enrollment_data(filters=None):
    conditions = []
    year = int(filters.get("year") if filters else nowdate().split('-')[0])
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


    # if filters.get("is_active") is not None:
    #     conditions.append(f"creche.is_active = {int(filters.get('is_active'))}")
    # if filters.get("old_creche") is not None:
    #     conditions.append(f"creche.old_creche = {int(filters.get('old_creche'))}")

    # if filters.get("gender"):
    #     conditions.append(f"cp.gender_id = {filters.get('gender')}")
    
    # Initialize age_group to a default value (None)
    # if filters.get("age_group"):
    #     age_group = int(filters.get('age_group'))
    #     if age_group == 1:
    #         # Children aged 0 to 12 months
    #         conditions.append("TIMESTAMPDIFF(MONTH, cp.child_dob, CURDATE()) BETWEEN 0 AND 12")
    #     elif age_group == 2:
    #         # Children aged 13 to 24 months
    #         conditions.append("TIMESTAMPDIFF(MONTH, cp.child_dob, CURDATE()) BETWEEN 13 AND 24")
    #     elif age_group == 3:
    #         # Children aged 25 to 36 months
    #         conditions.append("TIMESTAMPDIFF(MONTH, cp.child_dob, CURDATE()) BETWEEN 25 AND 36")
    # else:
    #     # If no age group is selected, count all children
    #     conditions.append("cp.child_dob IS NOT NULL")

    # partner = frappe.db.get_value("User", frappe.session.user, "partner")
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

    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None

    conditions.append(f"YEAR(cp.date_of_enrollment) = {int(year)}")

    if partner_id:
        conditions.append(f"creche.partner_id = '{partner_id}'")
    if state_id:
        conditions.append(f"creche.state_id = '{state_id}'")
    if filters.get("district"):
        conditions.append(f"creche.district_id = '{filters.get('district')}'")
    if filters.get("block"):
        conditions.append(f"creche.block_id = '{filters.get('block')}'")
    if filters.get("gp"):
        conditions.append(f"creche.gp_id = '{filters.get('gp')}'")
    if filters.get("creche"):
        conditions.append(f"creche.name = '{filters.get('creche')}'")
    if filters.get("supervisor_id"):
        conditions.append(f"creche.supervisor_id = '{filters.get('supervisor_id')}'")
    if creche_status_id:
        conditions.append(f"creche.creche_status_id = '{creche_status_id}'")
    if phases_cleaned:
        conditions.append(f"FIND_IN_SET(creche.phase, '{phases_cleaned}')")
    if cstart_date and cend_date:
       conditions.append(f"creche.creche_opening_date BETWEEN '{cstart_date}' AND '{cend_date}'")

    conditions_sql = " AND ".join(conditions) if conditions else "1 = 1"

    sql_query = f"""
        SELECT
            partner.partner_name AS partner,
            
            state.state_name AS state,
            district.district_name AS district,
            block.block_name AS block,
            gp.gp_name AS gp,
            creche.creche_name AS creche,
            creche.creche_id AS crecheid,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 1 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS january,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 2 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS february,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 3 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS march,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 4 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS april,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 5 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS may,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 6 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS june,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 7 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS july,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 8 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS august,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 9 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS september,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 10 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS october,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 11 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS november,
            COUNT(DISTINCT IF(MONTH(cp.date_of_enrollment) = 12 AND YEAR(cp.date_of_enrollment) = {year}, cp.hhcguid, NULL)) AS december

        FROM
            `tabChild Enrollment and Exit` AS cp
        JOIN
            `tabCreche` AS creche ON cp.creche_id = creche.name
        JOIN
            `tabPartner` AS partner ON partner.name = creche.partner_id
        JOIN
            `tabState` AS state ON state.name = creche.state_id
        JOIN
            `tabDistrict` AS district ON district.name = creche.district_id
        JOIN
            `tabBlock` AS block ON block.name = creche.block_id
        JOIN
            `tabGram Panchayat` AS gp ON gp.name = creche.gp_id
        WHERE
            {conditions_sql} AND
            cp.date_of_enrollment IS NOT NULL
        GROUP BY
            partner.partner_name, state.state_name, district.district_name, block.block_name, gp.gp_name, creche.creche_name
        ORDER BY
            partner.partner_name, state.state_name, district.district_name, block.block_name, gp.gp_name, creche.creche_name
    """

    data = frappe.db.sql(sql_query, as_dict=True)
    return data
