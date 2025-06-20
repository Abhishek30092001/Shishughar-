import frappe
from frappe.utils import nowdate
import calendar
from datetime import datetime, timedelta, date

def execute(filters=None):
    columns = get_columns(filters)
    data = get_summary_data(filters)
    return columns, data


def get_columns(filters=None):

    month = int(filters.get("month") if filters else date.today().month)
    year = int(filters.get("year") if filters else date.today().year)

    months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(12)]

    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
        {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 200},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 200},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
        {"label": "Date of Enrollment", "fieldname": "date_of_enrollment", "fieldtype": "Data", "width": 200},
        {"label": "Age (in month)", "fieldname": "age", "fieldtype": "Data", "width": 150},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
    ]


    for y, m in months:
        month_name = date(year, m, 1).strftime("%b")  
        year_month = f"{y}_{m:02d}"  

        columns.append({
            "label": f"Attendance-[{month_name} {y}]",
            "fieldname": f"attendance_percentage_{year_month}",
            "fieldtype": "Data",
            "width": 190,
            "default": "-" 
        })
        columns.append({
            "label": f"Underweight-[{month_name} {y}]",
            "fieldname": f"underweight_status_{year_month}",
            "fieldtype": "Data",
            "width": 190,
        })
        columns.append({
            "label": f"Wasting-[{month_name} {y}]",
            "fieldname": f"wasting_status_{year_month}",
            "fieldtype": "Data",
            "width": 180,
        })
        columns.append({
            "label": f"Stunting-[{month_name} {y}]",
            "fieldname": f"stuning_status_{year_month}",
            "fieldtype": "Data",
            "width": 180,
        })


    return columns

@frappe.whitelist()
def get_summary_data(filters=None):

    month = int(filters.get("month") if filters else nowdate().split('-')[1])
    year = int(filters.get("year") if filters else nowdate().split('-')[0])
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
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


            
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner = filters.get("partner") or current_user_partner

    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s 
        ORDER BY ts.state_name
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state = filters.get("state") or (current_user_state[0]['state_id'] if current_user_state else None)
    district = filters.get("district") if filters else None
    block = filters.get("block") if filters else None
    creche = filters.get("creche") if filters else None
    supervisor_id = filters.get("supervisor_id") if filters else None
    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
    partner = None if not partner else partner
    state = None if not state else state

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "partner": partner,
        "state": state,
        "district": district,
        "block": block,
        "creche": creche,
        "supervisor_id": supervisor_id,
        "year": year,
        "month": month,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "creche_status_id": creche_status_id,
        "phases": phases_cleaned
        
    }


    def generate_attendance_percentage_query(year, month):
        months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(12)]
        select_clause = ["cal.childenrolledguid"]
        
        for y, m in months:
            select_clause.append(f"""
                CONCAT(
                    CASE 
                        WHEN COUNT(*) = 0 THEN '0'
                        ELSE FORMAT(
                            (IFNULL(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
                                                AND MONTH(ca.date_of_attendance) = {m} 
                                                AND cal.attendance = 1 THEN 1 END), 0) 
                            / NULLIF(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
                                                AND MONTH(ca.date_of_attendance) = {m} THEN 1 END), 0)) * 100, 2
                        ) 
                    END, 
                    '%% (',
                    IFNULL(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
                                    AND MONTH(ca.date_of_attendance) = {m} 
                                    AND cal.attendance = 1 THEN 1 END), 0),
                    ')'
                ) AS attendance_percentage_{y}_{m:02d}
            """)
        
        select_clause_str = ",\n    ".join(select_clause)
        
        query = f"""
            SELECT 
                {select_clause_str}
            FROM `tabChild Attendance` AS ca
            INNER JOIN `tabChild Attendance List` AS cal ON cal.parent = ca.name
            WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
            GROUP BY cal.childenrolledguid

        """
        return query



    def generate_underweight_status_query(year, month):
        months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(12)]
        select_clause = ["tad.childenrollguid"]
        
        for y, m in months:
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        AND tad.weight_for_age IN (1, 2, 3) 
                        THEN 
                            CASE tad.weight_for_age 
                                WHEN 1 THEN 'Severe'
                                WHEN 2 THEN 'Moderate'
                                WHEN 3 THEN 'Normal'
                            END
                        ELSE '-'
                    END
                ) AS underweight_status_{y}_{m:02d}
            """)
        
        select_clause_str = ",\n    ".join(select_clause)
        
        query = f"""
        SELECT 
            {select_clause_str}
        FROM `tabAnthropromatic Data` tad 
        INNER JOIN `tabChild Growth Monitoring` tcgm ON tad.parent = tcgm.name 
        WHERE tad.measurement_taken_date IS NOT NULL
        GROUP BY tad.childenrollguid
        """
        return query

    def generate_wasting_status_query(year, month):
        months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(12)]
        select_clause = ["tad.childenrollguid"]
        
        for y, m in months:
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        AND tad.weight_for_height IN (1, 2, 3) 
                        THEN 
                            CASE tad.weight_for_height 
                                WHEN 1 THEN 'Severe'
                                WHEN 2 THEN 'Moderate'
                                WHEN 3 THEN 'Normal'
                            END
                        ELSE '-'
                    END
                ) AS wasting_status_{y}_{m:02d}
            """)
        
        select_clause_str = ",\n    ".join(select_clause)
        
        query = f"""
        SELECT 
            {select_clause_str}
        FROM `tabAnthropromatic Data` tad 
        INNER JOIN `tabChild Growth Monitoring` tcgm ON tad.parent = tcgm.name 
        WHERE tad.measurement_taken_date IS NOT NULL
        GROUP BY tad.childenrollguid
        """
        return query
    def generate_stunting_status_query(year, month):
        months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(12)]
        select_clause = ["tad.childenrollguid"]
        
        for y, m in months:
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        AND tad.height_for_age IN (1, 2, 3) 
                        THEN 
                            CASE tad.height_for_age 
                                WHEN 1 THEN 'Severe'
                                WHEN 2 THEN 'Moderate'
                                WHEN 3 THEN 'Normal'
                            END
                        ELSE '-'
                    END
                ) AS stuning_status_{y}_{m:02d}
            """)
        
        select_clause_str = ",\n    ".join(select_clause)
        
        query = f"""
        SELECT 
            {select_clause_str}
        FROM `tabAnthropromatic Data` tad 
        INNER JOIN `tabChild Growth Monitoring` tcgm ON tad.parent = tcgm.name 
        WHERE tad.measurement_taken_date IS NOT NULL
        GROUP BY tad.childenrollguid
        """
        return query



    attendance_percentage_query = generate_attendance_percentage_query(year, month)
    underweight_status_query = generate_underweight_status_query(year, month)
    wasting_status_query = generate_wasting_status_query(year, month)
    stuning_status_query = generate_stunting_status_query(year, month)

    sql_query = f"""
    SELECT    
        cr.creche_name AS 'creche_name',
        cr.creche_id AS 'creche_id',
        usr.full_name AS 'supervisor',
        cee.child_id AS 'child_id',
        cee.child_name AS 'child_name',
        DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS 'date_of_enrollment',

        cee.age_at_enrollment_in_months AS 'age',
        
        -- Dynamic attendance percentages for last 12 months
        opx.*,
        
        -- Dynamic underweight status for last 12 months
        uws.*,
        
        -- Dynamic wasting status for last 12 months
        ws.*,
        
        -- Dynamic wasting status for last 12 months
        ss.*,
        
        (CASE 
            WHEN cee.gender_id = '1' THEN 'M' 
            WHEN cee.gender_id = '2' THEN 'F' 
            ELSE cee.gender_id 
        END) AS gender,
        p.partner_name AS partner,
        s.state_name AS state,
        d.district_name AS district,
        b.block_name AS block
    FROM  
        `tabChild Enrollment and Exit` AS cee  
    LEFT JOIN (
        {attendance_percentage_query}
    ) AS opx ON opx.childenrolledguid = cee.childenrollguid    
    LEFT JOIN (
        {underweight_status_query}
    ) AS uws ON uws.childenrollguid = cee.childenrollguid    
    LEFT JOIN (
        {wasting_status_query}
    ) AS ws ON ws.childenrollguid = cee.childenrollguid    
    LEFT JOIN (
        {stuning_status_query}
    ) AS ss ON ss.childenrollguid = cee.childenrollguid    
    INNER JOIN 
        `tabCreche` AS cr ON cee.creche_id = cr.name 
    INNER JOIN 
        `tabUser` AS usr ON cr.supervisor_id = usr.name 
    INNER JOIN 
        `tabPartner` AS p ON p.name = cr.partner_id
    INNER JOIN 
        `tabState` AS s ON s.name = cr.state_id
    INNER JOIN 
        `tabDistrict` AS d ON d.name = cr.district_id
    INNER JOIN 
        `tabBlock` AS b ON b.name = cr.block_id
    WHERE 
        cee.date_of_enrollment <= %(end_date)s and (cee.date_of_exit IS null or cee.date_of_exit  >=  %(start_date)s)
        AND (%(partner)s IS NULL OR cr.partner_id = %(partner)s) 
        AND (%(state)s IS NULL OR cr.state_id = %(state)s) 
        AND (%(district)s IS NULL OR cr.district_id = %(district)s)
        AND (%(block)s IS NULL OR cr.block_id = %(block)s)
        AND (%(creche)s IS NULL OR cr.name = %(creche)s)
        AND (%(creche_status_id)s IS NULL OR cr.creche_status_id = %(creche_status_id)s)
		AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))   
    ORDER BY
        partner,state,district,block,supervisor,creche_name,child_name
    """

    data = frappe.db.sql(sql_query, params, as_dict=True)
    return data


