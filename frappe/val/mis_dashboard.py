import frappe
import calendar
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


@frappe.whitelist(allow_guest=True)
def get_eligible_enrolled_data():
    year_param = int(frappe.form_dict.get("year", 2024))
    month_param = int(frappe.form_dict.get("month", 12))
    start_date = f"{year_param:04d}-{month_param:02d}-01"

    filters = {
        "partner_id": frappe.form_dict.get("partner_id"),
        "state_id": frappe.form_dict.get("state_id"),
        "district_id": frappe.form_dict.get("district_id"),
        "block_id": frappe.form_dict.get("block_id"),
        "gp_id": frappe.form_dict.get("gp_id"),
        "creche_id": frappe.form_dict.get("creche_id"),
    }

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    start_year, start_month = start_date.year, start_date.month

    month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    dates = []
    labels = []

    # Generate chronological dates
    for i in range(12):
        month = (start_month - i - 1) % 12 + 1
        year = start_year - (1 if start_month - i <= 0 else 0)
        date_str = f"{year}-{month:02d}-01"
        month_label = f"{month_names[month - 1]}-{year}"
        dates.insert(0, (date_str, month_label))  # Insert at the beginning for chronological order
        labels.append(month_label)

    eligible_query_parts = []
    cumulative_enrolled_query_parts = []

    for date, _ in dates:
        eli_conditions = [
            f"TIMESTAMPDIFF(MONTH, hhc.child_dob, '{date}') BETWEEN 6 AND 36",
            f"'{date}' <= CURDATE()",
            "hhc.is_dob_available = 1"
        ]
        enr_conditions = [
            "cee.is_active = 1",
            f"cee.date_of_enrollment <= LAST_DAY('{date}')"
        ]

        for key, value in filters.items():
            if value:
                eli_conditions.append(f"hf.{key} = '{value}'")
                enr_conditions.append(f"cee.{key} = '{value}'")

        eligible_query_parts.append(f"""
        (SELECT COUNT(hhc.name)
            FROM `tabHousehold Child Form` AS hhc 
            JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
            WHERE {" AND ".join(eli_conditions)}) AS `{date}`""")

        cumulative_enrolled_query_parts.append(f"""
        (SELECT COUNT(*)
            FROM `tabChild Enrollment and Exit` AS cee
            WHERE {" AND ".join(enr_conditions)}) AS `{date}`""")

    eli_query = "SELECT " + ",\n".join(eligible_query_parts) + ";"
    cumulative_enrolled_query = "SELECT " + ",\n".join(cumulative_enrolled_query_parts) + ";"

    eli_result = frappe.db.sql(eli_query, as_dict=True)
    cumulative_enrolled_result = frappe.db.sql(cumulative_enrolled_query, as_dict=True)

    # Extract values in chronological order
    eli_values = list(eli_result[0].values()) if eli_result else [0] * 12
    cumulative_enrolled_values = list(cumulative_enrolled_result[0].values()) if cumulative_enrolled_result else [0] * 12

    response = {
        "labels": labels[::-1],
        "datasets": [
            {"name": "Eligible", "values": eli_values},
            {"name": "Enrolled", "values": cumulative_enrolled_values},
        ]
    }

    frappe.response["data"] = response


@frappe.whitelist(allow_guest=True)
def avg_enroll_in_month(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    year_month = f"{year}-{month:02d}-01" if year and month else None

    query = """
    SELECT 
        DATE_FORMAT(cp.date_of_enrollment, '%%Y-%%m') AS "Year-Month",
        ROUND(AVG(cp.age_at_enrollment_in_months), 0) AS "Average Enrollment Age in Months"
    FROM 
        `tabChild Enrollment and Exit` AS cp
    WHERE 
        (is_exited = 0)
        AND (%(partner_id)s IS NULL OR cp.partner_id = %(partner_id)s)
        AND (%(year_month)s IS NULL OR cp.creation <= %(year_month)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
        AND (%(creche_id)s IS NULL OR cp.name = %(creche_id)s)
    GROUP BY 
        DATE_FORMAT(cp.date_of_enrollment, '%%Y-%%m')
    ORDER BY 
        DATE_FORMAT(cp.date_of_enrollment, '%%Y-%%m')
    """

    query_params = {
        "year_month": year_month,
        "partner_id": partner_id,  
        "state_id": state_id,
        "district_id": district_id, 
        "block_id": block_id,    
        "gp_id": gp_id,       
        "creche_id": creche_id,   
    }

    data = frappe.db.sql(query, query_params, as_dict=True)
    avg_by_month = {row["Year-Month"]: row["Average Enrollment Age in Months"] for row in data}
    labels = [
        f"{calendar.month_abbr[m]}-{str(year)[-2:]}" for m in range(1, 13)
    ]
    eligible_values = [avg_by_month.get(f"{year}-{str(m).zfill(2)}", 0) for m in range(1, 13)]

    response = {
        "labels": labels,
        "datasets": [
            {"name": "Average Enrollment Age in Months", "values": eligible_values}
        ],
    }
    frappe.response["data"] = response
    
@frappe.whitelist(allow_guest=True)
def households_in_religion(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    year_month = f"{year}-{month:02d}-01" if year and month else None

    query = """
    SELECT 
        COUNT(cp.does_child_have_any_longterm_illness_more_than_6_months) AS "Number of Children with long term illness",
        ROUND(COUNT(cp.does_child_have_any_longterm_illness_more_than_6_months) / cc.cou * 100, 2) AS "Percentage of Children with long term illness"
    FROM 
        `tabChild Profile` AS cp
    LEFT JOIN `tabChild Enrollment and Exit` AS cee 
        ON cee.hhcguid = cp.chhguid
    LEFT JOIN (
        SELECT 
            creche_id, 
            COUNT(DISTINCT hhcguid) AS cou 
        FROM 
            `tabChild Enrollment and Exit` 
        WHERE 
            is_active = 1 
            AND is_exited = 0 
        GROUP BY 
            creche_id
    ) AS cc 
        ON cc.creche_id = cee.creche_id
    JOIN 
        `tabState` AS s ON cp.state_id = s.name
    JOIN 
        `tabDistrict` AS d ON cp.district_id = d.name
    JOIN 
        `tabBlock` AS b ON cp.block_id = b.name
    JOIN 
        `tabGram Panchayat` AS g ON cp.gp_id = g.name
    JOIN 
        `tabVillage` AS v ON cp.village_id = v.name
    JOIN 
        `tabCreche` AS c ON c.name = cee.creche_id
    JOIN 
        `tabPartner` AS p ON p.name = c.partner_id
    WHERE 
        cp.does_child_have_any_longterm_illness_more_than_6_months = 1
        AND  (%(year_month)s IS NULL OR cee.creation <= %(year_month)s)
        AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
        AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
    """

    group_by = []
    if partner_id is not None:
        group_by.append("p.partner_name")
    if state_id is not None:
        group_by.append("s.state_name")
    if district_id is not None:
        group_by.append("d.district_name")
    if block_id is not None:
        group_by.append("b.block_name")
    if gp_id is not None:
        group_by.append("g.gp_name")
    if creche_id is not None:
        group_by.append("c.creche_name")

    if not group_by:
        group_by = ["p.partner_name", "s.state_name", "d.district_name", "b.block_name", "g.gp_name", "v.village_name", "c.creche_name"]


    query += "GROUP BY " + ", ".join(group_by) + " "

    query += """
    HAVING 
        COUNT(cp.does_child_have_any_longterm_illness_more_than_6_months) > 0
    ORDER BY 
        p.partner_name,
        s.state_name, 
        d.district_name, 
        b.block_name, 
        g.gp_name, 
        v.village_name, 
        c.creche_name;
    """

    query_params = {
        "year_month": year_month,
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }


    data = frappe.db.sql(query, query_params, as_dict=True)
    labels = []

    if partner_id is None:
        partners = frappe.get_all('Partner', fields=['partner_name'])
        for partner in partners:
            labels.append(partner['partner_name'])
    else:
        partner_name = frappe.db.get_value('Partner', partner_id, 'partner_name')
        labels.append(f"Partner: {partner_name}")

    if state_id:
        state_name = frappe.db.get_value('State', state_id, 'state_name')
        labels.append(f"State: {state_name}")
    if district_id:
        district_name = frappe.db.get_value('District', district_id, 'district_name')
        labels.append(f"District: {district_name}")
    if block_id:
        block_name = frappe.db.get_value('Block', block_id, 'block_name')
        labels.append(f"Block: {block_name}")
    if gp_id:
        gp_name = frappe.db.get_value('Gram Panchayat', gp_id, 'gp_name')
        labels.append(f"GP: {gp_name}")
    if creche_id:
        creche_name = frappe.db.get_value('Creche', creche_id, 'creche_name')
        labels.append(f"Creche: {creche_name}")
    if year:
        labels.append(f"Year: {year}")
    if month:
        labels.append(f"Month: {month}")


    response = {
        "labels": labels,
        "datasets": [
            {
                "name": "Number of Children with long term illness",
                "values": []
            },
            {
                "name": "Percentage of Children with long term illness",
                "values": []
            }
        ]
    }

    for entry in data:
        response["datasets"][0]["values"].append(entry["Number of Children with long term illness"])
        response["datasets"][1]["values"].append(entry["Percentage of Children with long term illness"])

    # Return the response with the required structure
    frappe.response["data"] = response

@frappe.whitelist(allow_guest=True)
def get_education_level_mother(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    year_month = f"{year}-{month:02d}-01" if year and month else None
    
    query_s = """
    SELECT IFNULL(tel.level,'Not Available') AS EducationLevelName, COUNT(*) AS Count
    FROM `tabChild Profile` cp 
    INNER JOIN `tabChild Enrollment and Exit` cex 
        ON cex.hhcguid = cp.chhguid
    LEFT JOIN `tabEducation Level` tel 
        ON cp.education_level_of_parentscaregiver = tel.name
    WHERE 
        (%(partner_id)s IS NULL OR cex.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
        AND (%(creche_id)s IS NULL OR cex.creche_id = %(creche_id)s)
    GROUP BY cp.education_level_of_parentscaregiver, tel.level
    """

    query_params = {
        "year_month": year_month,
        "month": month,
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id
    }

    data = frappe.db.sql(query_s, query_params, as_dict=True)
    
    education_levels = ['Not Literate', 'Class 5', 'Class 8', 'Class 10', 'Intermediate', 'Diploma', 'Graduate', 'PG and above', 'Not Available']
    
    values = [0] * len(education_levels)
    
    for row in data:
        education_level_name = row['EducationLevelName']
        count = row['Count']
        
        if education_level_name in education_levels:
            index = education_levels.index(education_level_name)
            values[index] = count
    
    response = {
        "labels": education_levels,
        "datasets": [{
            "values": values,
        }]
    }

    frappe.response["data"] = response


@frappe.whitelist(allow_guest=True)
def get_specially_abled_children(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None
    year_month = f"{year}-{month:02d}-30" if year and month else None

    query = """ 
    SELECT 
        COUNT(DISTINCT cees.hhcguid) AS `enrolled_children`, 
        COUNT(DISTINCT CASE WHEN cp.child_specially_abled = 1 THEN cp.chhguid END) AS `specially_abled`  
    FROM 
        `tabChild Enrollment and Exit` AS cees
    JOIN 
        `tabChild Profile` AS cp 
    ON 
        cees.hhcguid = cp.chhguid
    WHERE 
        cees.is_active = 1  
        AND cees.date_of_enrollment <= %(year_month)s
        AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cees.name = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
    """

    query_params = {
        "year_month": year_month,
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    if data and len(data) > 0:
        enrolled_children = data[0].get("enrolled_children", 0)
        specially_abled = data[0].get("specially_abled", 0)
    else:
        enrolled_children = 0
        specially_abled = 0

    response = {
        "labels": ["Enrolled Children", "Specially Abled"],
        "datasets": [
            {
                "name": "Children Count",
                "values": [enrolled_children, specially_abled],
            }
        ],
    }

    frappe.response["data"] = response


@frappe.whitelist(allow_guest=True)
def age_in_months(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    year_month = f"{year}-{month:02d}-01" if year and month else None

    query = """
    SELECT 
        COUNT(CASE WHEN cee.age_at_enrollment_in_months BETWEEN 6 AND 9 THEN 1 END) AS "6-9",
        COUNT(CASE WHEN cee.age_at_enrollment_in_months BETWEEN 9 AND 12 THEN 1 END) AS "9-12",
        COUNT(CASE WHEN cee.age_at_enrollment_in_months BETWEEN 12 AND 24 THEN 1 END) AS "12-24",
        COUNT(CASE WHEN cee.age_at_enrollment_in_months BETWEEN 24 AND 36 THEN 1 END) AS "24-36"
    FROM 
        `tabChild Enrollment and Exit` AS cee
    JOIN 
        `tabState` AS s ON cee.state_id = s.name
    JOIN 
        `tabDistrict` AS d ON cee.district_id = d.name
    JOIN 
        `tabBlock` AS b ON cee.block_id = b.name
    JOIN 
        `tabGram Panchayat` AS g ON cee.gp_id = g.name
    JOIN 
        `tabVillage` AS v ON cee.village_id = v.name
    JOIN 
        `tabCreche` AS c ON cee.creche_id = c.name
    WHERE
        (%(year_month)s IS NULL OR cee.creation <= %(year_month)s)
        AND (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR cee.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cee.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cee.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cee.gp_id = %(gp_id)s)
        AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
        AND cee.is_exited = 0;
    """

    query_params = {
        "year_month": year_month,
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)
    counts = {
        "6-9": data[0]["6-9"] if data else 0,
        "9-12": data[0]["9-12"] if data else 0,
        "12-24": data[0]["12-24"] if data else 0,
        "24-36": data[0]["24-36"] if data else 0
    }

    response = {
        "labels": ["6-9 months", "9-12 months", "12-24 months", "24-36 months"],
        "datasets": [
            {
                "values": [
                    counts["6-9"],
                    counts["9-12"],
                    counts["12-24"],
                    counts["24-36"]
                ]
            }
        ]
    }

    frappe.response["data"] = response
 
@frappe.whitelist(allow_guest=True)
def get_occupation_data(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    year_month = f"{year}-{month:02d}-01" if year and month else None
    
    query_s = """
    SELECT 
        po.primary_occupation, 
        COUNT(*) AS count
    FROM 
        `tabHousehold Form` hf 
    JOIN 
        `tabPrimary Occupation` po 
        ON hf.primary_occupation_id = po.name
    JOIN 
        `tabPartner` p
        ON p.name = hf.partner_id
    LEFT JOIN
        `tabState` AS s
        ON hf.state_id = s.name
    LEFT JOIN
        `tabDistrict` AS d
        ON hf.district_id = d.name
    LEFT JOIN
        `tabBlock` AS b
        ON hf.block_id = b.name
    LEFT JOIN
        `tabGram Panchayat` AS g
        ON hf.gp_id = g.name
    JOIN (
        SELECT 
            COUNT(*) AS total_count
        FROM 
            `tabHousehold Form` hf
        WHERE 
            (%(partner_id)s IS NULL OR hf.partner_id = %(partner_id)s)
            AND (%(state_id)s IS NULL OR hf.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR hf.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR hf.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR hf.gp_id = %(gp_id)s)
            AND (%(year_month)s IS NULL OR hf.creation <= %(year_month)s)
    ) AS total
    WHERE 
        (%(partner_id)s IS NULL OR hf.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR hf.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR hf.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR hf.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR hf.gp_id = %(gp_id)s)
        AND (%(year_month)s IS NULL OR hf.creation <= %(year_month)s)
    GROUP BY 
        po.primary_occupation
    ORDER BY 
    LENGTH(po.primary_occupation) ASC;
    """
    
    query_params = {
        "year_month": year_month,
        "state_id": state_id,
        "district_id": district_id,
        "partner_id": partner_id,
        "block_id": block_id,
        "gp_id": gp_id,
    }

    data = frappe.db.sql(query_s, query_params, as_dict=True)

    labels = [row["primary_occupation"] for row in data]
    count_values = [row["count"] for row in data]

    response = {
        "labels": labels,
        "datasets": [
            {"name": "values", "values": count_values}
        ]
    }

    frappe.response["data"] = response
    
@frappe.whitelist(allow_guest=True)
def get_caste_data(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    year_month = f"{year}-{month:02d}-01" if year and month else None
    
    query_s = """
    SELECT 
    CASE 
        WHEN hh.social_category_id = 1 THEN 'General'
        WHEN hh.social_category_id = 2 THEN 'OBC'
        WHEN hh.social_category_id = 3 THEN 'SC'
        WHEN hh.social_category_id = 4 THEN 'ST'
        WHEN hh.social_category_id = 5 THEN 'Other'
        ELSE 'Not Available'
    END AS Caste,
    COUNT(hh.name) AS Count
    FROM 
        `tabHousehold Form` AS hh
    JOIN
        `tabCreche` AS cp ON cp.name = hh.creche_id
    LEFT JOIN
        `tabSocial Category` AS sc ON sc.name = hh.social_category_id
    WHERE 
        (%(partner_id)s IS NULL OR hh.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR hh.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR hh.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR hh.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR hh.gp_id = %(gp_id)s)
        AND (%(year_month)s IS NULL OR hh.creation <= %(year_month)s)    
    GROUP BY 
        Caste
    ORDER BY 
        FIELD(Caste, 'General', 'OBC', 'SC', 'ST', 'Other', 'Not Available');
    """

    query_params = {
        "year_month": year_month,
        "state_id": state_id,
        "district_id": district_id,
        "partner_id": partner_id,
        "block_id": block_id,
        "gp_id": gp_id,
    }

    data = frappe.db.sql(query_s, query_params, as_dict=True)

    caste_labels = ['General', 'OBC', 'SC', 'ST', 'Other', 'Not Available']
    caste_counts = {label: 0 for label in caste_labels}

    for row in data:
        caste_counts[row["Caste"]] = row["Count"]

    response = {
        "labels": caste_labels,
        "datasets": [
            {
                "values": [
                    caste_counts["General"],
                    caste_counts["OBC"],
                    caste_counts["SC"],
                    caste_counts["ST"],
                    caste_counts["Other"],
                    caste_counts["Not Available"]
                ]
            }
        ]
    }

    frappe.response["data"] = response

@frappe.whitelist(allow_guest=True)
def get_religion_data(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):

    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    year_month = f"{year}-{month:02d}-01" if year and month else None
    
    query_s = f"""
        SELECT 
            COUNT(CASE WHEN hh.religion = 1 THEN hh.name END) AS Hindu,
            COUNT(CASE WHEN hh.religion = 2 THEN hh.name END) AS Muslim,
            COUNT(CASE WHEN hh.religion = 3 THEN hh.name END) AS Christian,
            COUNT(CASE WHEN hh.religion = 4 THEN hh.name END) AS Buddhism,
            COUNT(CASE WHEN hh.religion = 5 THEN hh.name END) AS Sikhism,
            COUNT(CASE WHEN hh.religion = 6 THEN hh.name END) AS Jainism,
            COUNT(CASE WHEN hh.religion = 7 THEN hh.name END) AS `Any Other`,
            COUNT(CASE WHEN hh.religion IS NULL THEN hh.name END) AS `Not Available`
        FROM 
            `tabHousehold Form` AS hh
        LEFT JOIN
            `tabCreche` AS cp ON cp.name = hh.creche_id
        LEFT JOIN
            `tabReligion` AS r ON r.name = hh.religion
        WHERE 
            (%(partner_id)s IS NULL OR hh.partner_id = %(partner_id)s)
            AND (%(state_id)s IS NULL OR hh.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR hh.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR hh.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR hh.gp_id = %(gp_id)s)
            AND (%(year_month)s IS NULL OR hh.creation <= %(year_month)s)
    """
    
    query_params = {
        "year_month": year_month,
        "state_id": state_id,
        "district_id": district_id,
        "partner_id": partner_id,
        "block_id": block_id,
        "gp_id": gp_id,
    }

    data = frappe.db.sql(query_s, query_params, as_dict=True)

    religion_labels = ['Hindu', 'Muslim', 'Christian', 'Buddhism', 'Sikhism', 'Jainism', 'Any Other', 'Not Available']
    religion_counts = {label: 0 for label in religion_labels}

    for row in data:
        religion_counts['Hindu'] = row["Hindu"]
        religion_counts['Muslim'] = row["Muslim"]
        religion_counts['Christian'] = row["Christian"]
        religion_counts['Buddhism'] = row["Buddhism"]
        religion_counts['Sikhism'] = row["Sikhism"]
        religion_counts['Jainism'] = row["Jainism"]
        religion_counts['Any Other'] = row["Any Other"]
        religion_counts['Not Available'] = row["Not Available"]

    response = {
        "labels": religion_labels,
        "datasets": [
            {
                "values": [
                    religion_counts["Hindu"],
                    religion_counts["Muslim"],
                    religion_counts["Christian"],
                    religion_counts["Buddhism"],
                    religion_counts["Sikhism"],
                    religion_counts["Jainism"],
                    religion_counts["Any Other"],
                    religion_counts["Not Available"]
                ]
            }
        ]
    }

    frappe.response["data"] = response


@frappe.whitelist(allow_guest=True)
def avg_creche_open(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(tca.date_of_attendance, '%%b-%%Y') AS "month_year",
        CEIL(COUNT(*) / (SELECT COUNT(*) FROM `tabCreche`)) AS "avg_days_open"
    FROM 
        `tabChild Attendance` AS tca
    WHERE 
        tca.is_shishu_ghar_is_closed_for_the_day = 0
        AND tca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR tca.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR tca.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR tca.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR tca.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR tca.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR tca.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(tca.date_of_attendance, '%%Y-%%m')
    ORDER BY 
        DATE_FORMAT(tca.date_of_attendance, '%%Y-%%m') DESC;
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)


    percentage_values = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            percentage_values[index] = row["avg_days_open"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Average Days Crèche Open",
                "values": percentage_values,
            }
        ]
    }



@frappe.whitelist(allow_guest=True)
def get_exit_reasons(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None

    year_month = f"{year}-{month:02d}-01" if year and month else None

    query = """
    SELECT 
        CASE 
            WHEN cp.reason_for_exit IS NULL THEN 'Not Provided'
            WHEN cp.reason_for_exit = 1 THEN 'Migrated'
            WHEN cp.reason_for_exit = 2 THEN 'Graduated'
            WHEN cp.reason_for_exit = 3 THEN 'Not Willing to stay'
            WHEN cp.reason_for_exit = 4 THEN 'Death'
            WHEN cp.reason_for_exit = 5 THEN 'Other'
        END AS Reason,
        COUNT(*) AS Count
    FROM 
        `tabChild Enrollment and Exit` AS cp
    WHERE 
        cp.is_exited = 1
        AND (%(partner_id)s IS NULL OR cp.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
        AND (%(year_month)s IS NULL OR cp.creation <= %(year_month)s)
    GROUP BY 
        Reason
    ORDER BY 
        Reason;
    """

    query_params = {
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "year_month": year_month
    }

    data = frappe.db.sql(query, query_params, as_dict=True)
    default_reasons = {
        "Not Provided": 0,
        "Migrated": 0,
        "Graduated": 0,
        "Not Willing ": 0,
        "Death": 0,
        "Other": 0,
    }
    for row in data:
        if row["Reason"] in default_reasons:
            default_reasons[row["Reason"]] = row["Count"]

    response_data = {
        "labels": list(default_reasons.keys()),
        "datasets": [
            {"values": list(default_reasons.values())}
        ]
    }

    frappe.response['data'] = response_data


@frappe.whitelist(allow_guest=True)
def avg_attendance_per_child(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None

    today = datetime.today()
    months_list = [
        (today - timedelta(days=month_offset * 30)).strftime("%Y-%m")
        for month_offset in range(11, -1, -1)
    ]
    
    query = """  
    SELECT 
        tf.creche_id AS "Creche ID",
        tf.child AS "Enrolled Children",
        tf.att AS "Attendance",
        CASE 
            WHEN tf.att > 0 THEN tf.child / tf.att 
            ELSE 0 
        END AS "Average Attendance",
        tf.month_year AS "Month"
    FROM (
        SELECT 
            c.name AS creche_id,
            SUM(uc.uc) AS child,
            SUM(ac.ac) AS att,
            DATE_FORMAT(ca.date_of_attendance, '%%Y-%%m') AS month_year
        FROM 
            `tabCreche` AS c
        LEFT JOIN (
            SELECT 
                cee.creche_id, 
                COUNT(DISTINCT cee.hhcguid) AS uc
            FROM 
                `tabChild Enrollment and Exit` AS cee
            WHERE 
                cee.is_active = 1
                AND cee.is_exited = 0
            GROUP BY 
                cee.creche_id
        ) AS uc 
        ON 
            c.name = uc.creche_id
        LEFT JOIN (
            SELECT 
                ca.creche_id, 
                COUNT(DISTINCT cal.childenrolledguid) AS ac
            FROM 
                `tabChild Attendance List` AS cal
            LEFT JOIN
                `tabChild Attendance` AS ca ON ca.name = cal.parent
            LEFT JOIN
                `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = cal.childenrolledguid
            WHERE 
                cee.is_active = 1
                AND cee.is_exited = 0
            GROUP BY 
                ca.creche_id
        ) AS ac 
        ON 
            c.name = ac.creche_id
        LEFT JOIN 
            `tabChild Attendance` AS ca ON ca.creche_id = c.name
        WHERE 
            ca.date_of_attendance >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR ca.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR ca.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR ca.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR ca.gp_id = %(gp_id)s)
        GROUP BY 
            c.name, month_year
    ) AS tf
    HAVING 
        tf.att > 0
    ORDER BY 
        tf.month_year ASC;
    """

    query_params = {
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    response_data = {
        "labels": months_list,
        "datasets": [
            {
                "name": "Enrolled Children",
                "values": [0] * len(months_list), 
            },
            {
                "name": "Attendance",
                "values": [0] * len(months_list), 
            },
            {
                "name": "Average Attendance",
                "values": [0] * len(months_list),  
            }
        ]
    }

    for row in data:
        month_index = months_list.index(row["Month"])
        response_data["datasets"][0]["values"][month_index] = row["Enrolled Children"]
        response_data["datasets"][1]["values"][month_index] = row["Attendance"]
        response_data["datasets"][2]["values"][month_index] = row["Average Attendance"]

    frappe.response["data"] = response_data


@frappe.whitelist(allow_guest=True)
def creche_house_types(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None
    year_month = f"{year}-{month:02d}-01" if year and month else None

    query = """  
        SELECT 
            COALESCE(tp.type_of_creche_house, 'Uncategorized') AS house_type,
            COUNT(cp.name) AS house_count
        FROM 
            `tabCreche` AS cp
        LEFT JOIN
            `tabType of creche house` AS tp ON tp.name = cp.type_of_creche_house
        WHERE 
            (%(partner_id)s IS NULL OR cp.partner_id = %(partner_id)s)
            AND  (%(year_month)s IS NULL OR cp.creation <= %(year_month)s)
            AND (%(creche_id)s IS NULL OR cp.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
        GROUP BY
            COALESCE(tp.type_of_creche_house, 'Uncategorized'),
            tp.type_of_creche_house
        ORDER BY 
            house_type;
    """

    query_params = {
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
        "year_month": year_month,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    fixed_labels = ["Old school building", "Community hall", "Uncategorized", "Rented house", "Uncategorized", "Any other"]
    
    response = {
        "labels": fixed_labels,
        "datasets": [
            {
                "name": "Numbers",
                "values": [0] * len(fixed_labels)
            }
        ]
    }

    if data:
        for item in data:
            if item["house_type"] in fixed_labels:
                index = fixed_labels.index(item["house_type"])
                response["datasets"][0]["values"][index] = item["house_count"]

    frappe.response['data'] = response
    
@frappe.whitelist(allow_guest=True)
def hard_to_reach_creche(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None
    year_month = f"{year}-{month:02d}-01" if year and month else None

    query = """  
        SELECT 
            COUNT(CASE WHEN cp.hard_to_reach = 1 THEN cp.name END) AS hard_to_reach_count,
            COUNT(CASE WHEN cp.hard_to_reach = 0 THEN cp.name END) AS easy_to_reach_count
        FROM 
            `tabCreche` AS cp
        WHERE 
            (%(partner_id)s IS NULL OR cp.partner_id = %(partner_id)s)
            AND (%(year_month)s IS NULL OR cp.creation <= %(year_month)s)
            AND (%(creche_id)s IS NULL OR cp.name = %(creche_id)s)
            AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
    """

    query_params = {
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
        "year_month": year_month,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    if data:
        result = data[0]
        labels = ["Hard to Reach", "Easy to Reach", "Total Creche"]
        values = [
            result.get("hard_to_reach_count", 0),
            result.get("easy_to_reach_count", 0)
        ]
    else:
        labels = ["Hard to Reach", "Easy to Reach"]
        values = [0, 0, 0]

    response = {
        "labels": labels,
        "datasets": [
            {
                "name": "Creche Data",
                "values": values,
            }
        ]
    }

    frappe.response["data"] = response

@frappe.whitelist(allow_guest=True)
def get_reg_HH(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    start_date = date(year, month, 1)
    end_date = start_date + relativedelta(months=1) - relativedelta(days=1)  # End of provided month
    start_date = end_date - relativedelta(months=11)  # Start date 12 months back

    labels = [(start_date + relativedelta(months=i)).strftime("%b-%Y").upper() for i in range(12)]

    query = """
    SELECT 
        DATE_FORMAT(hh.creation, '%%b-%%Y') AS month_year,
        COUNT(*) AS count
    FROM 
        `tabHousehold Form` AS hh
    WHERE
        (%(partner_id)s IS NULL OR hh.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR hh.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR hh.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR hh.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR hh.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR hh.gp_id = %(gp_id)s)
        AND (hh.creation BETWEEN %(start_date)s AND %(end_date)s)
    GROUP BY 
        DATE_FORMAT(hh.creation, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(hh.creation, '%%b-%%Y')
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    values = [0] * 12
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()  # Example: "JAN-2024"
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            values[index] = row["count"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Registered Household",
                "values": values,
            }
        ]
    }
@frappe.whitelist(allow_guest=True)
def get_grievance_data(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None
    year_month = f"{year}-{month:02d}-01" if year and month else None

    query = """  
        SELECT
            gs.grievance_subject AS subject,
            COUNT(gv.name) AS count
        FROM `tabGrievance` AS gv
        JOIN `tabGrievance Subject` AS gs
            ON gv.title = gs.name
        WHERE 
            (%(partner_id)s IS NULL OR gv.partner_id = %(partner_id)s)
            AND (%(year_month)s IS NULL OR gv.creation <= %(year_month)s)
            AND (%(creche_id)s IS NULL OR gv.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR gv.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR gv.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR gv.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR gv.gp_id = %(gp_id)s)
        GROUP BY subject
    """

    query_params = {
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
        "year_month": year_month,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    if data:
        labels = [row["subject"] for row in data]
        values = [row["count"] for row in data]
    else:
        labels = []
        values = []

    response = {
        "labels": labels,
        "datasets": [
            {
                "name": "Grievance Data",
                "values": values,
            }
        ]
    }

    frappe.response["data"] = response



@frappe.whitelist(allow_guest=True)
def awc_thr(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None

    if not year or not month or month < 1 or month > 12:
        frappe.throw("Invalid year or month provided.")

    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None

    end_date = datetime(year, month, 1, 23, 59, 59) + relativedelta(months=1, days=-1)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """  
    SELECT 
        DATE_FORMAT(ad.creation, '%%b-%%Y') AS `month_year`,
        CAST(SUM(CASE WHEN ad.THR = 1 THEN 1 ELSE 0 END) AS UNSIGNED) AS `No_of_Children_with_THR_from_AWC`
    FROM 
        `tabAnthropromatic Data` AS ad
    LEFT JOIN
        `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    LEFT JOIN
        `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
    WHERE
        ad.creation BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
    GROUP BY 
        `month_year`
    ORDER BY 
        DATE_FORMAT(DATE(ad.creation), '%%Y-%%m')

    """

    query_params = {
        "start_date": start_date,
        "end_date": end_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    no_of_children_values = [0] * 12

    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row.get("month_year", "").upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            no_of_children_values[index] = row.get("No_of_Children_with_THR_from_AWC", 0)


    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "THR from AWC",
                "values": no_of_children_values,
            }
        ],
    }

@frappe.whitelist(allow_guest=True)
def weight_awc(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    if not year or not (1 <= month <= 12):
        frappe.throw("Invalid year or month provided.")

    end_date = datetime(year, month, 1) + relativedelta(months=1, days=-1)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)


    query = """  
    SELECT 
        DATE_FORMAT(ad.creation, '%%b-%%Y') AS `month_year`,
        COUNT(DISTINCT ad.child_id) AS `weight_count`
    FROM 
        `tabAnthropromatic Data` AS ad
    LEFT JOIN 
        `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    WHERE 
        cgm.is_active = 1
        AND ad.awc = 1
        AND ad.do_you_have_height_weight = 1
        AND ad.creation BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(ad.creation, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(ad.creation, '%%Y-%%m');
    """


    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)


    weight_taken_awc = [0] * 12
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row.get("month_year", "").upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            weight_taken_awc[index] = row.get("weight_count", 0)

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Weight taken from AWC",
                "values": weight_taken_awc,
            }
        ],
    }


@frappe.whitelist(allow_guest=True)
def curr_eligible_vhnd(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None

    end_date = datetime(year, month, 1, 23, 59, 59) + relativedelta(months=1, days=-1)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """  
    SELECT 
        DATE_FORMAT(ac.creation, '%%b-%%Y') AS `Month`,
        SUM(COALESCE(ac.ac, 0)) AS "No_eligible_and_taken_VHND"
    FROM 
        `tabCreche` AS c
    LEFT JOIN (
        SELECT 
            cee.creche_id, 
            COUNT(DISTINCT cee.hhcguid) AS uc
        FROM 
            `tabChild Enrollment and Exit` AS cee
        WHERE 
            cee.is_active = 1
            AND cee.is_exited = 0
        GROUP BY 
            cee.creche_id
    ) AS uc 
    ON c.name = uc.creche_id
    LEFT JOIN (
        SELECT 
            cgm.creche_id, 
            COUNT(DISTINCT ad.chhguid) AS ac,
            ad.creation
        FROM 
            `tabAnthropromatic Data` AS ad
        LEFT JOIN `tabChild Growth Monitoring` AS cgm 
            ON cgm.name = ad.parent
        LEFT JOIN `tabChild Enrollment and Exit` AS cee 
            ON cee.childenrollguid = ad.childenrollguid
        WHERE 
            cee.is_active = 1
            AND cee.is_exited = 0
            AND ad.vhsnd = 1
            AND ad.do_you_have_height_weight = 1
            AND ad.creation BETWEEN %(start_date)s AND %(end_date)s 
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR cgm.name = %(creche_id)s)
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
        GROUP BY 
            cgm.creche_id, ad.creation
    ) AS ac 
    ON c.name = ac.creche_id
    GROUP BY 
        DATE_FORMAT(ac.creation, '%%Y-%%m')
    ORDER BY 
        `Month` DESC;
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    No_eligible_and_taken_VHND = [0] * 12

    month_index_map = {label: i for i, label in enumerate(labels)}


    for row in data:
        month_abbr = row.get("Month")
        if month_abbr:
            month_abbr = month_abbr.upper()  # only call .upper() if month_abbr is not None
            if month_abbr in month_index_map:
                index = month_index_map[month_abbr]              
                No_eligible_and_taken_VHND[index] = row.get("No_eligible_and_taken_VHND", 0)

            

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Eligible and taken VHND",
                "values": No_eligible_and_taken_VHND,
            }       
        ],
    }



@frappe.whitelist(allow_guest=True)
def curr_eligible_not_vhnd(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None

    end_date = datetime(year, month, 1, 23, 59, 59) + relativedelta(months=1, days=-1)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """  
    SELECT 
        DATE_FORMAT(ac.creation, '%%b-%%Y') AS `Month`,
        SUM(COALESCE(ac.ac, 0)) AS "No_eligible_and_not_taken_VHND"
    FROM 
        `tabCreche` AS c
    LEFT JOIN (
        SELECT 
            cee.creche_id, 
            COUNT(DISTINCT cee.hhcguid) AS uc
        FROM 
            `tabChild Enrollment and Exit` AS cee
        WHERE 
            cee.is_active = 1
            AND cee.is_exited = 0
        GROUP BY 
            cee.creche_id
    ) AS uc 
    ON c.name = uc.creche_id
    LEFT JOIN (
        SELECT 
            cgm.creche_id, 
            COUNT(DISTINCT ad.chhguid) AS ac,
            ad.creation
        FROM 
            `tabAnthropromatic Data` AS ad
        LEFT JOIN `tabChild Growth Monitoring` AS cgm 
            ON cgm.name = ad.parent
        LEFT JOIN `tabChild Enrollment and Exit` AS cee 
            ON cee.childenrollguid = ad.childenrollguid
        WHERE 
            cee.is_active = 1
            AND cee.is_exited = 0
            AND ad.vhsnd = 2
            AND ad.do_you_have_height_weight = 1
            AND ad.creation BETWEEN %(start_date)s AND %(end_date)s 
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR cgm.name = %(creche_id)s)
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
        GROUP BY 
            cgm.creche_id, ad.creation
    ) AS ac 
    ON c.name = ac.creche_id
    GROUP BY 
        DATE_FORMAT(ac.creation, '%%Y-%%m')
    ORDER BY 
        `Month` DESC;
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    No_eligible_and_not_taken_VHND = [0] * 12

    month_index_map = {label: i for i, label in enumerate(labels)}


    for row in data:
        month_abbr = row.get("Month")
        if month_abbr:
            month_abbr = month_abbr.upper()  
            if month_abbr in month_index_map:
                index = month_index_map[month_abbr]             
                No_eligible_and_not_taken_VHND[index] = row.get("No_eligible_and_not_taken_VHND", 0)

            

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [    
            {
                "name": "Eligible and not taken VHND",
                "values": No_eligible_and_not_taken_VHND,
            }       
        ],
    }

@frappe.whitelist(allow_guest=True)
def absent_present(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None


    end_date = datetime(year, month, 1, 23, 59, 59) + relativedelta(months=1, days=-1)
    start_date = end_date - relativedelta(months=11, day=1)


    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)


    query = """  
    SELECT 
        DATE_FORMAT(c.creation, '%%Y-%%m') AS month,
        COALESCE(SUM(ac.ac), 0) AS "Present Children",
        GREATEST(COALESCE(SUM(uc.uc), 0) - COALESCE(SUM(ac.ac), 0), 0) AS "Absent Children"
    FROM 
        `tabCreche` AS c
    LEFT JOIN (
        SELECT 
            cee.creche_id, 
            COUNT(DISTINCT cee.hhcguid) AS uc
        FROM 
            `tabChild Enrollment and Exit` AS cee
        WHERE 
            cee.is_active = 1
            AND cee.is_exited = 0
        GROUP BY 
            cee.creche_id
    ) AS uc 
    ON c.name = uc.creche_id
    LEFT JOIN (
        SELECT 
            ca.creche_id, 
            COUNT(DISTINCT cal.childenrolledguid) AS ac
        FROM 
            `tabChild Attendance List` AS cal
        LEFT JOIN
            `tabChild Attendance` AS ca ON ca.name = cal.parent
        LEFT JOIN
            `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = cal.childenrolledguid
        WHERE 
            cee.is_active = 1
            AND cee.is_exited = 0
        GROUP BY 
            ca.creche_id
    ) AS ac 
    ON c.name = ac.creche_id
    WHERE 
        c.creation BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR c.name = %(creche_id)s)
        AND (%(state_id)s IS NULL OR c.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR c.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR c.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR c.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(c.creation, '%%Y-%%m')
    ORDER BY 
        month ASC;
    """


    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }


    data = frappe.db.sql(query, query_params, as_dict=True)

    absent = [0] * 12
    # present = [0] * 12

    month_index_map = {datetime.strptime(label, "%b-%Y").strftime("%Y-%m"): i for i, label in enumerate(labels)}

    for row in data:
        sql_month = row.get("month")
        if sql_month in month_index_map:
            index = month_index_map[sql_month]
            absent[index] = int(row.get("Absent Children", 0))


    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            # {
            #     "name": "Present Children",
            #     "values": present,
            # },
            {
                "name": "Absent Children",
                "values": absent,
            },
        ],
    }


@frappe.whitelist(allow_guest=True)
def hh_migration_data(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None


    year_month = f"{year}-{month:02d}-01" if year and month else None

    today = datetime.today()
    months_list = [
        (today - timedelta(days=month_offset * 30)).strftime("%Y-%m")
        for month_offset in range(11, -1, -1)
    ]
    
    
    query = """
    SELECT 
        COUNT(CASE WHEN hh.is_anyone_of_your_family_a_migrant_worker = 1 AND hh.no_of_months_the_migrants_were_away_last_year = 1 THEN hh.name END) AS HHMGE6M,
        COUNT(CASE WHEN hh.is_anyone_of_your_family_a_migrant_worker = 1 AND hh.no_of_months_the_migrants_were_away_last_year = 2 THEN hh.name END) AS HHML6M
    FROM 
        `tabHousehold Form` AS hh
    WHERE 
        (%(partner_id)s IS NULL OR hh.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR hh.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR hh.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR hh.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR hh.gp_id = %(gp_id)s)
        AND (%(year_month)s IS NULL OR hh.creation <= %(year_month)s)
    """

    query_params = {
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "year_month": year_month
    }

    data = frappe.db.sql(query, query_params, as_dict=True)
    if data:
        result = data[0]
        labels = ["HH >= 6 months", "HH < 6 months"]
        values = [
            result.get("HHMGE6M", 0),
            result.get("HHML6M", 0)
        ]
    else:
        labels = ["HH >= 6 months", "HH < 6 months"]
        values = [0, 0]

    response = {
        "labels": labels,
        "datasets": [
            {
                "name": "Migration Data",
                "values": values,
            }
        ]
    }

    frappe.response["data"] = response
    


@frappe.whitelist(allow_guest=True)
def get_creche_checkin(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):


    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_date = date(year, month, 1) + relativedelta(day=31)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())  # Example: "jan-2024"
        current_date += relativedelta(months=1)

    query = """
        SELECT 
            DATE_FORMAT(cr.date_of_checkin, '%%b-%%Y') AS month_year,
            COUNT(DISTINCT cr.name) AS total_checkins
        FROM 
            `tabCreche Check In` AS cr
        LEFT JOIN 
            `tabCreche` AS c ON c.name = cr.creche_id
        WHERE 
            cr.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s
            AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR cr.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR c.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR c.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR c.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR c.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(cr.date_of_checkin, '%%b-%%Y')
        ORDER BY 
            DATE_FORMAT(cr.date_of_checkin, '%%Y-%%m')
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)


    values = [0] * 12
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()  # Example: "jan-2024"
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            values[index] = row["total_checkins"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Total Check-ins",
                "values": values,
            }
        ]
    }


# antro APIs --------------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def get_underweight_children(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59) 
    start_date = end_date - relativedelta(months=11)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())  # Example: "JAN-2024"
        current_date += relativedelta(months=1)

    query = """    
        SELECT 
            DATE_FORMAT(DATE(cgm.measurement_date), '%%b-%%Y') AS month_year,
            COUNT(DISTINCT ad.chhguid) AS uc
        FROM 
            `tabAnthropromatic Data` AS ad
        LEFT JOIN 
            `tabChild Growth Monitoring` AS cgm
        ON 
            ad.parent = cgm.name
        WHERE 
            do_you_have_height_weight = 1
            AND weight_for_age < 3 
            AND weight_for_age != 0
            AND (DATE(cgm.measurement_date) BETWEEN %(start_date)s AND %(end_date)s)
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(DATE(cgm.measurement_date), '%%b-%%Y')
        ORDER BY 
            DATE_FORMAT(DATE(cgm.measurement_date), '%%Y-%%m')  -- Ordering by Year-Month for proper chronological order
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    values = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}
    
    for row in data:
        month_abbr = row["month_year"].upper()  # Example: "JAN-2024"
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            values[index] = row["uc"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Underweight Children",
                "values": values,
            }
        ]
    }

@frappe.whitelist(allow_guest=True)
def get_stuned_children(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    if not year or not month:
        frappe.throw("Year and month are required.")

    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11)
    start_date = datetime(start_date.year, start_date.month, 1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """    
        SELECT 
            DATE_FORMAT(DATE(cgm.creation), '%%b-%%Y') AS month_year,
            COUNT(DISTINCT ad.chhguid) AS sc
        FROM 
            `tabAnthropromatic Data` AS ad
        LEFT JOIN 
            `tabChild Growth Monitoring` AS cgm
        ON 
            ad.parent = cgm.name
        WHERE 
            do_you_have_height_weight = 1
            AND weight_for_height < 3 
            AND weight_for_height != 0
            AND (DATE(cgm.creation) BETWEEN %(start_date)s AND %(end_date)s)
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(DATE(cgm.creation), '%%b-%%Y')
        ORDER BY 
            DATE_FORMAT(DATE(cgm.creation), '%%Y-%%m')
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    values = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            values[index] = row["sc"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Stuned Children",
                "values": values,
            }
        ]
    }


@frappe.whitelist(allow_guest=True)
def get_wasted_children(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    # Input validation
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]  
    end_date = date(year, month, end_day)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())  # Example: "JAN-2024"
        current_date += relativedelta(months=1)

    query = """    
        SELECT 
            DATE_FORMAT(cgm.measurement_date, '%%b-%%Y') AS month_year,
            COUNT(DISTINCT ad.chhguid) AS wc
        FROM 
            `tabAnthropromatic Data` AS ad
        LEFT JOIN 
            `tabChild Growth Monitoring` AS cgm
        ON 
            ad.parent = cgm.name
        WHERE 
            do_you_have_height_weight = 1
            AND height_for_age < 3 
            AND height_for_age != 0
            AND (cgm.measurement_date BETWEEN %(start_date)s AND %(end_date)s)
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(cgm.measurement_date, '%%b-%%Y')
        ORDER BY 
            DATE_FORMAT(cgm.measurement_date, '%%b-%%Y')  
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    values = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()  # Example: "JAN-2024"
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            values[index] = row["wc"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Wasted Children",
                "values": values,
            }
        ]
    }



#creche related activities----------------------------------------------------------


@frappe.whitelist(allow_guest=True)
def creche_committee_meeting(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):

    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
        SELECT 
            DATE_FORMAT(ccm.meeting_date, '%%b-%%Y') AS month_year,
            count(ccm.name) as "Number of Meetings"
        FROM 
            `tabCreche Committee Meeting` AS ccm
        JOIN 
            `tabCreche` AS c ON c.name = ccm.creche_id
        WHERE 
            (DATE(ccm.meeting_date) BETWEEN %(start_date)s AND %(end_date)s)
            AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR c.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR c.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR c.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR c.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR c.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(ccm.meeting_date, '%%b-%%Y')
        ORDER BY 
            DATE_FORMAT(DATE(ccm.meeting_date), '%%Y-%%m')

    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    values = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            values[index] = row["Number of Meetings"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Number of Meetings",
                "values": values,
            }
        ]
    }
    
    
@frappe.whitelist(allow_guest=True)
def meetings_and_participations(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
        SELECT 
            DATE_FORMAT(ccm.meeting_date, '%%b-%%Y') AS month_year,
            COUNT(ccm.name) AS Meetings,
            SUM(ccm.number_of_participants) AS Total_Participants
        FROM 
            `tabCreche Committee Meeting` AS ccm
        WHERE 
            (DATE(ccm.meeting_date) BETWEEN %(start_date)s AND %(end_date)s)
            AND (%(partner_id)s IS NULL OR ccm.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR ccm.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR ccm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR ccm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR ccm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR ccm.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(ccm.meeting_date, '%%b-%%Y')
        ORDER BY 
            DATE_FORMAT(DATE(ccm.meeting_date), '%%Y-%%m')
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    # meetings_values = [0] * len(labels)
    participants_values = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            # meetings_values[index] = row["Meetings"]
            participants_values[index] = row["Total_Participants"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            # {
            #     "name": "Meetings",
            #     "values": meetings_values,
            # },
            {
                "name": "Participants",
                "values": participants_values,
            }
        ]
    }


@frappe.whitelist(allow_guest=True)
def meetings_and_participations_aww(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):

    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)


    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
        SELECT 
            DATE_FORMAT(ccm.meeting_date, '%%b-%%Y') AS month_year,
            (COUNT(ccm.name) / 
             (SELECT COUNT(cc.name) 
              FROM `tabCreche Committee Meeting` AS cc
              WHERE DATE(cc.meeting_date) BETWEEN %(start_date)s AND %(end_date)s
              AND DATE(cc.meeting_date) BETWEEN DATE_FORMAT(ccm.meeting_date, '%%Y-%%m-01') AND LAST_DAY(ccm.meeting_date))) * 100 AS `Percentage of Meetings`
        FROM 
            `tabCreche Committee Meeting` AS ccm
        LEFT JOIN
            `tabAttendees child table` AS act 
        ON 
            act.parent = ccm.name
        WHERE
            act.attendees_table = 1
            AND DATE(ccm.meeting_date) BETWEEN %(start_date)s AND %(end_date)s
            AND (%(partner_id)s IS NULL OR ccm.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR ccm.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR ccm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR ccm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR ccm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR ccm.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(ccm.meeting_date, '%%b-%%Y')
        ORDER BY 
            DATE_FORMAT(DATE(ccm.meeting_date), '%%Y-%%m')
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }


    data = frappe.db.sql(query, query_params, as_dict=True)

    percentage_values = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            percentage_values[index] = row["Percentage of Meetings"]


    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Meetings with AWW",
                "values": percentage_values,
            }
        ]
    }


@frappe.whitelist(allow_guest=True)
def meetings_and_participations_asha(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
        SELECT 
            DATE_FORMAT(ccm.meeting_date, '%%b-%%Y') AS month_year,     
            (COUNT(ccm.name) / 
             (SELECT COUNT(cc.name) 
              FROM `tabCreche Committee Meeting` AS cc
              WHERE DATE(cc.meeting_date) BETWEEN %(start_date)s AND %(end_date)s
              AND DATE(cc.meeting_date) BETWEEN DATE_FORMAT(ccm.meeting_date, '%%Y-%%m-01') AND LAST_DAY(ccm.meeting_date))) * 100 AS `Percentage of Meetings`
        FROM 
            `tabCreche Committee Meeting` AS ccm
        LEFT JOIN
            `tabAttendees child table` AS act 
        ON 
            act.parent = ccm.name
        WHERE
            act.attendees_table = 2
            AND DATE(ccm.meeting_date) BETWEEN %(start_date)s AND %(end_date)s
            AND (%(partner_id)s IS NULL OR ccm.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR ccm.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR ccm.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR ccm.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR ccm.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR ccm.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(ccm.meeting_date, '%%b-%%Y')
        ORDER BY 
            DATE_FORMAT(DATE(ccm.meeting_date), '%%Y-%%m')
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    percentage_values = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            percentage_values[index] = row["Percentage of Meetings"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Meetings with Asha",
                "values": percentage_values,
            }
        ]
    }

# Red Flag Apis--------------------------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def red_flag_chidren(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
        SELECT 
            DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y') AS month_year,   
            COUNT(DISTINCT ad.name) AS rfc
        FROM
            `tabAnthropromatic Data` AS ad
        Left JOIN
            `tabChild Growth Monitoring` as cgm on cgm.name =ad.parent
        WHERE 
            ad.measurement_taken_date BETWEEN '2024-02-01' AND '2025-02-19'
            AND (
                ad.weight_for_age = 1 
                OR (ad.weight_for_age = 2 AND ad.weight_for_height <= 2) 
                OR ad.any_medical_major_illness = 1
            )
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
            
        GROUP BY 
            month_year
        ORDER BY 
            DATE_FORMAT(ad.measurement_taken_date, '%%Y-%%m')
        """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    red_flag_children = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            red_flag_children[index] = row["rfc"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Red flag childrens",
                "values": red_flag_children,
            }
        ]
    }



@frappe.whitelist(allow_guest=True)
def red_flag_anthro(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(cr.creation, '%%b-%%Y') AS month_year,        
        SUM(uc.uc) AS `rfca`
    FROM (
        SELECT 
            COUNT(DISTINCT ad.chhguid) AS uc,
            cgm.creche_id
        FROM 
            `tabAnthropromatic Data` AS ad
        LEFT JOIN 
            `tabChild Growth Monitoring` AS cgm
        ON 
            ad.parent = cgm.name
        WHERE 
            ad.do_you_have_height_weight = 1
            AND ad.weight_for_age = 3
        GROUP BY 
            cgm.creche_id
    ) AS uc
    JOIN 
        `tabCreche` AS cr ON cr.name = uc.creche_id
    WHERE 
        DATE(cr.creation) BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cr.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cr.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cr.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cr.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cr.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(cr.creation, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(cr.creation, '%%Y-%%m');

    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    red_flag_children = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            red_flag_children[index] = row["rfca"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Red flag (Anthro)",
                "values": red_flag_children,
            }
        ]
    }




@frappe.whitelist(allow_guest=True)
def red_flag_illness(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y') AS month_year,        
        COUNT(DISTINCT ad.name) AS rfci
    FROM 
        `tabAnthropromatic Data` AS ad
    LEFT JOIN 
        `tabChild Growth Monitoring` AS cgm
    ON 
        ad.parent = cgm.name
    WHERE 
        ad.do_you_have_height_weight = 1
        AND ad.any_medical_major_illness = 1
        AND DATE(ad.measurement_taken_date) BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(ad.measurement_taken_date, '%%Y-%%m');

    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    red_flag_children = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            red_flag_children[index] = row["rfci"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Red flag (Anthro)",
                "values": red_flag_children,
            }
        ]
    }


# time-series analysis ------------------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def weight_for_age_status(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y') AS month_year,    
        SUM(CASE WHEN ad.weight_for_age = 1 THEN 1 ELSE 0 END) AS `Weight for Age = 1`,
        SUM(CASE WHEN ad.weight_for_age = 2 THEN 1 ELSE 0 END) AS `Weight for Age = 2`,
        SUM(CASE WHEN ad.weight_for_age = 3 THEN 1 ELSE 0 END) AS `Weight for Age = 3`,
        SUM(CASE WHEN ad.weight_for_age = 0 THEN 1 ELSE 0 END) AS `Weight for Age = 0`
    FROM
        `tabChild Growth Monitoring` AS cgm 
    LEFT JOIN 
        `tabAnthropromatic Data` AS ad ON ad.parent = cgm.name
    WHERE 
        ad.do_you_have_height_weight = 1 
        AND ad.measurement_taken_date IS NOT NULL
        AND DATE(ad.measurement_taken_date) BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(ad.measurement_taken_date, '%%Y-%%m');
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    weight_for_age_data = {
        "Weight for Age = 1": [0] * len(labels),
        "Weight for Age = 2": [0] * len(labels),
        "Weight for Age = 3": [0] * len(labels),
        "Weight for Age = 0": [0] * len(labels),
    }

    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            weight_for_age_data["Weight for Age = 1"][index] = row["Weight for Age = 1"]
            weight_for_age_data["Weight for Age = 2"][index] = row["Weight for Age = 2"]
            weight_for_age_data["Weight for Age = 3"][index] = row["Weight for Age = 3"]
            weight_for_age_data["Weight for Age = 0"][index] = row["Weight for Age = 0"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Red",
                "values": weight_for_age_data["Weight for Age = 1"],
            },
            {
                "name": "Yellow",
                "values": weight_for_age_data["Weight for Age = 2"],
            },
            {
                "name": "Green",
                "values": weight_for_age_data["Weight for Age = 3"],
            }
        ]
    }


@frappe.whitelist(allow_guest=True)
def weight_for_height_status(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y') AS month_year,    
        SUM(CASE WHEN ad.weight_for_height = 1 THEN 1 ELSE 0 END) AS `Weight for Height = 1`,
        SUM(CASE WHEN ad.weight_for_height = 2 THEN 1 ELSE 0 END) AS `Weight for Height = 2`,
        SUM(CASE WHEN ad.weight_for_height = 3 THEN 1 ELSE 0 END) AS `Weight for Height = 3`,
        SUM(CASE WHEN ad.weight_for_height = 0 THEN 1 ELSE 0 END) AS `Weight for Height = 0`
    FROM
        `tabChild Growth Monitoring` AS cgm 
    LEFT JOIN 
        `tabAnthropromatic Data` AS ad ON ad.parent = cgm.name
    WHERE 
        ad.do_you_have_height_weight = 1 
        AND ad.measurement_taken_date IS NOT NULL
        AND DATE(ad.measurement_taken_date) BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(ad.measurement_taken_date, '%%Y-%%m');
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    weight_for_height_data = {
        "Weight for Height = 1": [0] * len(labels),
        "Weight for Height = 2": [0] * len(labels),
        "Weight for Height = 3": [0] * len(labels),
        "Weight for Height = 0": [0] * len(labels),
    }

    month_index_map = {label: i for i, label in enumerate(labels)}
    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            weight_for_height_data["Weight for Height = 1"][index] = row["Weight for Height = 1"]
            weight_for_height_data["Weight for Height = 2"][index] = row["Weight for Height = 2"]
            weight_for_height_data["Weight for Height = 3"][index] = row["Weight for Height = 3"]
            weight_for_height_data["Weight for Height = 0"][index] = row["Weight for Height = 0"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Red",
                "values": weight_for_height_data["Weight for Height = 1"],
            },
            {
                "name": "Yellow",
                "values": weight_for_height_data["Weight for Height = 2"],
            },
            {
                "name": "Green",
                "values": weight_for_height_data["Weight for Height = 3"],
            },

        ]
    }


@frappe.whitelist(allow_guest=True)
def height_for_age_status(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y') AS month_year,    
        SUM(CASE WHEN ad.height_for_age = 1 THEN 1 ELSE 0 END) AS `Height For Age = 1`,
        SUM(CASE WHEN ad.height_for_age = 2 THEN 1 ELSE 0 END) AS `Height For Age = 2`,
        SUM(CASE WHEN ad.height_for_age = 3 THEN 1 ELSE 0 END) AS `Height For Age = 3`,
        SUM(CASE WHEN ad.height_for_age = 0 THEN 1 ELSE 0 END) AS `Height For Age = 0`
    FROM 
        `tabChild Growth Monitoring` AS cgm 
    LEFT JOIN 
        `tabAnthropromatic Data` AS ad ON ad.parent = cgm.name
    WHERE 
        ad.do_you_have_height_weight = 1 
        AND ad.measurement_taken_date IS NOT NULL
        AND DATE(ad.measurement_taken_date) BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cgm.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cgm.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cgm.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(ad.measurement_taken_date, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(ad.measurement_taken_date, '%%Y-%%m');
    
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    height_for_age = {
        "Height For Age = 1": [0] * len(labels),
        "Height For Age = 2": [0] * len(labels),
        "Height For Age = 3": [0] * len(labels),
        "Height For Age = 0": [0] * len(labels),
    }

    month_index_map = {label: i for i, label in enumerate(labels)}
    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            height_for_age["Height For Age = 1"][index] = row["Height For Age = 1"]
            height_for_age["Height For Age = 2"][index] = row["Height For Age = 2"]
            height_for_age["Height For Age = 3"][index] = row["Height For Age = 3"]
            height_for_age["Height For Age = 0"][index] = row["Height For Age = 0"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Red",
                "values": height_for_age["Height For Age = 1"],
            },
            {
                "name": "Yellow",
                "values": height_for_age["Height For Age = 2"],
            },
            {
                "name": "Green",
                "values": height_for_age["Height For Age = 3"],
            }
        ]
    }

@frappe.whitelist(allow_guest=True)
def child_ref_nrc(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(cp.date_of_referral, '%%b-%%Y') AS month_year,
        COUNT(DISTINCT cp.childenrolledguid) AS "Referred to NRC"
    FROM 
        `tabChild Referral` AS cp
    WHERE 
        cp.referred_to_nrc = 4
        AND  DATE(cp.date_of_referral) BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cp.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cp.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(cp.date_of_referral, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(cp.date_of_referral, '%%Y-%%m');
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    ref_to_nrc = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            ref_to_nrc[index] = row["Referred to NRC"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Referred to NRC Count",
                "values": ref_to_nrc,
            }
        ]
    }



@frappe.whitelist(allow_guest=True)
def child_adm_nrc(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
   
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(cp.admission_date, '%%b-%%Y') AS month_year,
        COUNT(DISTINCT cp.childenrolledguid) AS "Admitted to NRC"
    FROM 
        `tabChild Referral` AS cp
    WHERE 
        cp.referred_to_nrc = 4
        AND  cp.admission_date is not null
        AND  DATE(cp.admission_date) BETWEEN %(start_date)s AND %(end_date)s
        AND (%(partner_id)s IS NULL OR cp.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cp.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(cp.admission_date, '%%b-%%Y')
    ORDER BY 
        DATE_FORMAT(cp.admission_date, '%%Y-%%m');

    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    adm_to_nrc = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper()
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            adm_to_nrc[index] = row["Admitted to NRC"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Admitted to NRC Count",
                "values": adm_to_nrc,
            }
        ]
    }

@frappe.whitelist(allow_guest=True)
def ref_health_care(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        DATE_FORMAT(cr.date_of_referral, '%%b-%%Y') AS `Month-Year`,
        COUNT(cr.name) AS "Referred to Health Care"
    FROM 
        `tabCreche` AS c
    LEFT JOIN 
        `tabChild Referral` AS cr ON c.name = cr.creche_id
    WHERE 
        cr.referred_to IS NOT NULL
        AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cr.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cr.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cr.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cr.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cr.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(cr.date_of_referral, '%%b-%%Y')
    HAVING 
        COUNT(cr.name) > 0
    ORDER BY 
        `Month-Year`;
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    reffer_health = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["Month-Year"].upper() 
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            reffer_health[index] = row["Referred to Health Care"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Referred to Health Care",
                "values": reffer_health,
            }
        ]
    }



@frappe.whitelist(allow_guest=True)
def visited_health_care(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    SELECT 
        tf.month_year AS `Month-Year`,
        tf.ac AS "Visited to Health Care"
    FROM (
        SELECT 
            DATE_FORMAT(cr.visit_date, '%%b-%%Y') AS month_year,
            COUNT(DISTINCT cr.childenrolledguid) AS ac
        FROM 
            tabCreche AS c
        LEFT JOIN 
            `tabChild Referral` AS cr ON c.name = cr.creche_id
        WHERE 
            cr.visit_date IS NOT NULL
            AND cr.visit_date BETWEEN %(start_date)s AND %(end_date)s 
            AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
            AND (%(creche_id)s IS NULL OR cr.creche_id = %(creche_id)s)
            AND (%(state_id)s IS NULL OR cr.state_id = %(state_id)s)
            AND (%(district_id)s IS NULL OR cr.district_id = %(district_id)s)
            AND (%(block_id)s IS NULL OR cr.block_id = %(block_id)s)
            AND (%(gp_id)s IS NULL OR cr.gp_id = %(gp_id)s)
        GROUP BY 
            DATE_FORMAT(cr.visit_date, '%%b-%%Y')
            
    ) AS tf
    HAVING 
        tf.ac > 0
    ORDER BY 
        tf.month_year;
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    reffer_health = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["Month-Year"].upper() 
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            reffer_health[index] = row["Visited to Health Care"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Visited to Health Care",
                "values": reffer_health,
            }
        ]
    }



# others details -------------------------------------------------------------------------------------------


@frappe.whitelist(allow_guest=True)
def children_having_disability(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    
    SELECT 
        DATE_FORMAT(cee.creation, '%%b-%%Y') AS month_year,
        COUNT(*) AS "Disabled Children"
    FROM 
        `tabChild Profile` AS cp
    LEFT JOIN `tabChild Enrollment and Exit` AS cee 
        ON cee.hhcguid = cp.chhguid    
    WHERE 
        cp.does_child_have_any_disability = 1
        AND cee.creation BETWEEN %(start_date)s AND %(end_date)s 
        AND (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(cee.creation, '%%b-%%Y')
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    dis_children = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper() 
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            dis_children[index] = row["Disabled Children"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Disabled Children",
                "values": dis_children,
            }
        ]
    }


@frappe.whitelist(allow_guest=True)
def children_having_long_illness(year=None, month=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    partner_id = int(partner_id) if partner_id and partner_id.isdigit() else None
    state_id = int(state_id) if state_id and state_id.isdigit() else None
    district_id = int(district_id) if district_id and district_id.isdigit() else None
    block_id = int(block_id) if block_id and block_id.isdigit() else None
    gp_id = int(gp_id) if gp_id and gp_id.isdigit() else None
    creche_id = int(creche_id) if creche_id and creche_id.isdigit() else None

    if not year or not month:
        frappe.throw("Year and month are required.")

    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day, 23, 59, 59)
    start_date = end_date - relativedelta(months=11, day=1)

    labels = []
    current_date = start_date
    for _ in range(12):
        labels.append(current_date.strftime("%b-%Y").upper())
        current_date += relativedelta(months=1)

    query = """
    
    SELECT 
        DATE_FORMAT(cee.creation, '%%b-%%Y') AS month_year,
        COUNT(*) AS "Children having long term illness"
    FROM 
        `tabChild Profile` AS cp
    LEFT JOIN `tabChild Enrollment and Exit` AS cee 
        ON cee.hhcguid = cp.chhguid    
    WHERE 
        cp.does_child_have_any_longterm_illness_more_than_6_months = 1
        AND cee.creation BETWEEN %(start_date)s AND %(end_date)s 
        AND (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s)
        AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
        AND (%(state_id)s IS NULL OR cp.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cp.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cp.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cp.gp_id = %(gp_id)s)
    GROUP BY 
        DATE_FORMAT(cee.creation, '%%b-%%Y')
    """

    query_params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "block_id": block_id,
        "gp_id": gp_id,
        "creche_id": creche_id,
    }

    data = frappe.db.sql(query, query_params, as_dict=True)

    long_term_ill_children = [0] * len(labels)
    month_index_map = {label: i for i, label in enumerate(labels)}

    for row in data:
        month_abbr = row["month_year"].upper() 
        if month_abbr in month_index_map:
            index = month_index_map[month_abbr]
            long_term_ill_children[index] = row["Children having long term illness"]

    frappe.response["data"] = {
        "labels": labels,
        "datasets": [
            {
                "name": "Children having long term illness",
                "values": long_term_ill_children,
            }
        ]
    }