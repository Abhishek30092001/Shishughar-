import frappe
from frappe.utils import nowdate

def execute(filters=None):
    columns, data = [], []
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    selected_year = filters.get("year") if filters else frappe.utils.nowdate().split('-')[0]

    # Define columns, including the Seq. No column and No of Days Open column
    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "No of Days Open", "fieldname": "days_open", "fieldtype": "Int", "width": 200}
    ]

    for month in months:
        month_label = f"{month[:3]}-{selected_year}"
        columns.append({"label": month_label, "fieldname": month.lower(), "fieldtype": "Data", "width": 120})

    # Fetch data
    data = get_enrollment_data(filters, months, selected_year)

    # Add sequence number to data
    for idx, row in enumerate(data, start=1):
        row['idx'] = idx

    return columns, data


@frappe.whitelist()
def get_enrollment_data(filters=None, months=None, year=None):
    conditions = []

    # Fetch the partner ID associated with the logged-in user, if any
    partner = frappe.db.get_value("User", frappe.session.user, "partner")

    # If the user is a partner, add a condition to only show their data
    if partner:
        conditions.append(f"creche.partner_id = '{partner}'")
    else:
        # Otherwise, apply the filters provided in the UI
        if filters.get("partner"):
            conditions.append(f"creche.partner_id = '{filters.get('partner')}'")
        if filters.get("state"):
            conditions.append(f"creche.state_id = '{filters.get('state')}'")
        if filters.get("district"):
            conditions.append(f"creche.district_id = '{filters.get('district')}'")
        if filters.get("block"):
            conditions.append(f"creche.block_id = '{filters.get('block')}'")
        if filters.get("gp"):
            conditions.append(f"creche.gp_id = '{filters.get('gp')}'")
        if filters.get("creche"):
            conditions.append(f"creche.name = '{filters.get('creche')}'")

    conditions_sql = " AND ".join(conditions) if conditions else "1 = 1"

    sql_query = f"""
    SELECT
        state.state_name AS state,
        partner.partner_name AS partner,
        district.district_name AS district,
        block.block_name AS block,
        gp.gp_name AS gp,
        creche.creche_name AS creche,
        COUNT(IF(cp.is_shishu_ghar_is_closed_for_the_day = 0, 1, NULL)) AS days_open,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 1 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS january,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 2 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS february,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 3 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS march,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 4 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS april,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 5 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS may,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 6 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS june,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 7 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS july,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 8 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS august,

		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 9 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS september,
		
		
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 10 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS october,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 11 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS november,
		DATE_FORMAT(SEC_TO_TIME(AVG(IF(MONTH(cp.open_time) = 12 AND YEAR(cp.open_time) = {year}, TIME_TO_SEC(TIMEDIFF(cp.close_time, cp.open_time)), NULL))), '%H:%i') AS december
    FROM
        `tabChild Attendance` AS cp
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
        {conditions_sql}
    GROUP BY
        partner.partner_name, state.state_name, district.district_name, block.block_name, gp.gp_name, creche.creche_name
    ORDER BY
        partner.partner_name, state.state_name, district.district_name, block.block_name, gp.gp_name, creche.creche_name
    """

    data = frappe.db.sql(sql_query, as_dict=True)
    return data
