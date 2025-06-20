import frappe
from datetime import  date
def execute(filters=None):
    columns = [
        {"label": "Partner Name", "fieldname": "Partner Name", "fieldtype": "Link", "options": "Partner", "width": 200},
        {"label": "State", "fieldname": "State", "fieldtype": "Link", "options": "State", "width": 200},
        {"label": "District", "fieldname": "District","fieldtype": "Data","width": 200},
        {"label": "Block", "fieldname": "Block","fieldtype": "Data","width": 200},
        {"label": "GP", "fieldname": "GP","fieldtype": "Data","width": 200},
        {"label": "Village", "fieldname": "Village","fieldtype": "Data","width": 200},
        {"label": "Creche", "fieldname": "creche","fieldtype": "Data","width": 200},
        {"label": "Date of Visit", "fieldname": "Date of Visit","width": 120},
        {"label": "Hamlet", "fieldname": "Hamlet","fieldtype": "Data","width": 200},
        {"label": "Landmark", "fieldname": "Landmark","fieldtype": "Data","width": 200},
        {"label": "Respondent Name", "fieldname": "Respondent Name","fieldtype": "Data","width": 260},
        {"label": "Respondent Age", "fieldname": "Respondent Age","fieldtype": "Int"},
        {"label": "Respondent Gender", "fieldname": "Respondent Gender","fieldtype": "Data"},
        {"label": "Household Head Name", "fieldname": "Household Head Name","fieldtype": "Data"},
        {"label": "Social Category", "fieldname": "Social Category","fieldtype": "Data"},
        {"label": "Is the family a PVTG?", "fieldname": "Is the family a PVTG?","fieldtype": "Data"},
        {"label": "PVTG Name", "fieldname": "PVTG Name","fieldtype": "Data"},
        {"label": "Primary Occupation", "fieldname": "Primary Occupation","fieldtype": "Data"},
        {"label": "Primary Occupation Other", "fieldname": "Primary Occupation Other","fieldtype": "Data"},
        {"label": "Verification Status", "fieldname": "Verification Status","fieldtype": "Data"},
        {"label": "Number of Family Members", "fieldname": "Number of Family Members","fieldtype": "Int"},
        {"label": "Children Under 3 years", "fieldname": "Children Under 3 years","fieldtype": "Int"},
        {"label": "Children 3 to 6 years", "fieldname": "Children 3 to 6 years","fieldtype": "Int"},
        {"label": "Children 6 to 18 years", "fieldname": "Children 6 to 18 years","fieldtype": "Int"},
        {"label": "Adults above 18 years", "fieldname": "Adults above 18 years","fieldtype": "Int"},
        {"label": "Child Name", "fieldname": "Child Name","fieldtype": "Data"},
        {"label": "Child Gender", "fieldname": "Child Gender","fieldtype": "Data"},
        {"label": "Relation with Child", "fieldname": "Relation with Child","fieldtype": "Data"},
        {"label": "Child DOB", "fieldname": "Child DOB","fieldtype": "Data"},
        {"label": "Child Age in Months", "fieldname": "Child Age in Months","fieldtype": "Int"},
        {"label": "Child Is Verified?", "fieldname": "Child Is Verified?","fieldtype": "Data"},
        {"label": "Family Members Engaged as Migrant Workers", "fieldname": "Family Members Engaged as Migrant Workers","fieldtype": "Data"},
        {"label": "Number of Months the migrants were away last year", "fieldname": "Number of Months the migrants were away last year","fieldtype": "Data"},
        {"label": "Does anyone from the family migrate every year?", "fieldname": "Does anyone from the family migrate every year?","fieldtype": "Data"},
        {"label": "Who looks after the children at home?", "fieldname": "Who looks after the children at home?","fieldtype": "Data"}
    ]

    data = get_report_data(filters)
    return columns, data

@frappe.whitelist()
def get_report_data(filters=None):
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year

    district = filters.get("district") if filters else None
    block = filters.get("block") if filters else None
    gp = filters.get("gp") if filters else None
    supervisor_id = filters.get("supervisor_id") if filters else None

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

    conditions = ""
 
    if partner_id:
        conditions += f" AND P.name = '{partner_id}'"
    if state_id:
        conditions += f" AND state.name = '{state_id}'"
    if district:
        conditions += f" AND district.name = '{district}'"
    if block:
        conditions += f" AND block.name = '{block}'"
    if gp:
        conditions += f" AND gp.name = '{gp}'"
    if supervisor_id:
        conditions += f" AND c.supervisor_id = '{supervisor_id}'"
    if creche_status_id:
        conditions += f" AND c.creche_status_id = '{creche_status_id}'"
    if phases_cleaned:
        conditions += f" AND c.phases_cleaned = '{phases_cleaned}'"
    if cstart_date and cend_date:
        conditions += f" AND c.creche_opening_date BETWEEN '{cstart_date}' AND '{cend_date}'"
    

    sql_query = f"""
        SELECT
            P.partner_name AS 'Partner Name',
            hh.date_of_visit AS 'Date of Visit',
            state.state_name AS 'State',
            district.district_name AS 'District',
            block.block_name AS 'Block',
            gp.gp_name AS 'GP',
            village.village_name AS 'Village',
            c.creche_name AS 'creche',
            hh.hamlet AS 'Hamlet',
            hh.landmark AS 'Landmark',
            hh.respondent_name AS 'Respondent Name',
            hh.respondent_age AS 'Respondent Age',
            gender.gender AS 'Respondent Gender',
            hh.hosuehold_head_name AS 'Household Head Name',
            sc.social_category_name AS 'Social Category',
            CASE
                WHEN hh.is_the_family_a_pvtg = 1 THEN 'YES'
                ELSE 'NO'
            END AS 'Is the family a PVTG?',
            hh.pvtg_name AS 'PVTG Name',
            po.primary_occupation AS 'Primary Occupation',
            hh.primary_occupation_other AS 'Primary Occupation Other',
            vs.verfication_status_name AS 'Verification Status',
            hh.number_of_family_members AS 'Number of Family Members',
            hh.children__3_years AS 'Children Under 3 years',
            hh.children_3_to_6_years AS 'Children 3 to 6 years',
            hh.children_6_to_18_years AS 'Children 6 to 18 years',
            hh.adults_above_18_years AS 'Adults above 18 years',
            hhc.child_name AS 'Child Name',
            child_gender.gender AS 'Child Gender',
            relation.relation_name AS 'Relation with Child',
            hhc.child_dob AS 'Child DOB',
            hhc.child_age AS 'Child Age in Months',
            CASE
                WHEN hhc.is_verified = 1 THEN 'YES'
                ELSE 'NO'
            END AS 'Child Is Verified?',
            hh.family_members_enganged_as_migrant_workers AS 'Family Members Engaged as Migrant Workers',
            CASE
                WHEN hh.no_of_months_the_migrants_were_away_last_year = 1 THEN '>= 6 Months'
                ELSE '< 6 Months'
            END AS 'Number of Months the migrants were away last year',
            CASE
                WHEN hh.does_anyone_from_your_family_migrate_every_year = 1 THEN 'YES'
                ELSE 'NO'
            END AS 'Does anyone from the family migrate every year?',
            hh.who_looks_after_them_at_home AS 'Who looks after the children at home?'
        FROM
            `tabHousehold Form` AS hh
        JOIN
            `tabHousehold Child Form` AS hhc ON hh.name = hhc.parent
        JOIN
            `tabCreche` AS c ON c.name = hh.creche_id
        JOIN
            `tabPartner` AS P ON P.name = hh.partner_id
        JOIN
            `tabState` AS state ON state.name = hh.state_id
        JOIN
            `tabDistrict` AS district ON district.name = hh.district_id
        JOIN
            `tabBlock` AS block ON block.name = hh.block_id
        JOIN
            `tabGram Panchayat` AS gp ON gp.name = hh.gp_id
        JOIN
            `tabVillage` AS village ON village.name = hh.village_id
        JOIN
            `tabGender` AS gender ON gender.name = hh.respondent_gender_id
        JOIN
            `tabSocial Category` AS sc ON sc.name = hh.social_category_id
        JOIN
            `tabPrimary Occupation` AS po ON po.name = hh.primary_occupation_id
        JOIN
            `tabVerfication Status` AS vs ON vs.name = hh.verification_status
        JOIN
            `tabGender` AS child_gender ON child_gender.name = hhc.gender_id
        JOIN
            `tabRelation` AS relation ON relation.name = hhc.relationship_with_child
        WHERE
            1 = 1 {conditions} 
            AND MONTH( hh.creation) = {month} AND YEAR( hh.creation) = {year}  
        ORDER BY
            P.partner_name, state.state_name ASC
    """
    data = frappe.db.sql(sql_query, as_dict=True)
    return data
