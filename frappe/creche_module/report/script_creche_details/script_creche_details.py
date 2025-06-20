import frappe

def execute(filters=None):
    columns = [
        {"label": "Partner Name", "fieldname": "Partner Name", "fieldtype": "Link", "options": "Partner", "width": 200},
        {"label": "Supervisor", "fieldname": "Supervisor"},
        {"label": "State", "fieldname": "State"},
        {"label": "District", "fieldname": "District"},
        {"label": "Block", "fieldname": "Block"},
        {"label": "GP", "fieldname": "GP"},
        {"label": "Village", "fieldname": "Village"},
        {"label": "Creche ID", "fieldname": "Creche ID"},
        {"label": "Creche Name", "fieldname": "Creche Name"},
        {"label": "Creche Opening Time", "fieldname": "Creche Opening Time"},
        {"label": "Creche Closing Time", "fieldname": "Creche Closing Time"},
        {"label": "Weekly Holiday", "fieldname": "Weekly Holiday"},
        {"label": "Is Active ?", "fieldname": "Is Active ?"},
        {"label": "Caregiver Code", "fieldname": "Caregiver Code"},
        {"label": "Caregiver Name", "fieldname": "Caregiver Name"},
        {"label": "Mobile Number", "fieldname": "Mobile Number"},
        {"label": "Is Caregiver Active?", "fieldname": "Is Caregiver Active?"},
        {"label": "Date Of Joining", "fieldname": "Date Of Joining"},
        {"label": "Date Of Leaving", "fieldname": "Date Of Leaving"}
    ]

    data = get_report_data(filters)
    return columns, data

@frappe.whitelist()
def get_report_data(filters=None):
    partner = frappe.db.get_value("User", frappe.session.user, "partner")  # Fetch partner assigned to current user
    state = filters.get("state") if filters else None
    district = filters.get("district") if filters else None
    block = filters.get("block") if filters else None
    gp = filters.get("gp") if filters else None
    village = filters.get("village") if filters else None

    conditions = ""
    if state:
        conditions += f" AND creche.state_id = '{state}'"
    if district:
        conditions += f" AND creche.district_id = '{district}'"
    if block:
        conditions += f" AND creche.block_id = '{block}'"
    if gp:
        conditions += f" AND creche.gp_id = '{gp}'"
    if village:
        conditions += f" AND creche.village_id = '{village}'"

    sql_query = f"""
        SELECT
            P.partner_name AS 'Partner Name',
            supervisor.first_name AS 'Supervisor',
            state.state_name AS 'State',
            district.district_name AS 'District',
            block.block_name AS 'Block',
            gp.gp_name AS 'GP',
            village.village_name AS 'Village',
            creche.creche_id AS 'Creche ID',
            creche.creche_name AS 'Creche Name',
            creche.creche_openning_time AS 'Creche Opening Time',
            creche.creche_closing_time AS 'Creche Closing Time',
            weekly_holiday.day_name AS 'Weekly Holiday',
            CASE
                WHEN creche.is_active = 1 THEN 'YES'
                ELSE 'NO'
            END AS 'Is Active ?',
            cc.caregiver_code AS 'Caregiver Code',
            cc.caregiver_name AS 'Caregiver Name',
            cc.mobile_no AS 'Mobile Number',
            CASE
                WHEN cc.is_active = 1 THEN 'YES'
                ELSE 'NO'
            END AS 'Is Caregiver Active?',
            cc.date_of_joinning AS 'Date Of Joining',
            cc.date_of_leaving AS 'Date Of Leaving'
        FROM
            `tabCreche` AS creche
        JOIN
            `tabCreche Caregiver` AS cc ON creche.name = cc.parent
        JOIN
            `tabPartner` AS P ON P.name = creche.partner_id
        JOIN
            `tabState` AS state ON state.name = creche.state_id
        JOIN
            `tabDistrict` AS district ON district.name = creche.district_id
        JOIN
            `tabBlock` AS block ON block.name = creche.block_id
        JOIN
            `tabGram Panchayat` AS gp ON gp.name = creche.gp_id
        JOIN
            `tabVillage` AS village ON village.name = creche.village_id
        JOIN
            `tabUser` AS supervisor ON supervisor.name = creche.supervisor_id
        JOIN
            `tabDays Of Week` AS weekly_holiday ON weekly_holiday.name = creche.weekly_holiday_id
        WHERE
            (IFNULL(%(partner)s, '') = '' OR creche.partner_id = %(partner)s)
            {conditions}
        ORDER BY
            creche.name, P.partner_name, state.name ASC
    """

    data = frappe.db.sql(sql_query, {"partner": partner}, as_dict=True)
    return data
