import frappe
from frappe.utils import nowdate
from datetime import date
import calendar

def execute(filters=None):
    columns = get_columns()
    data = get_summary_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "Operational Creches", "fieldname": "operation_creches", "fieldtype": "Int", "width": 200},
        {"label": "Cumulative Enrolled Children", "fieldname": "cumm_enrolled_children", "fieldtype": "Int", "width": 260},
        {"label": "Cumulative Exited Children", "fieldname": "cumulative_exit_children", "fieldtype": "Int", "width": 260},
        {"label": "Cumulative Graduated Children", "fieldname": "cumulative_graduate_children", "fieldtype": "Int", "width": 260},
        {"label": "Eligible Children in this month", "fieldname": "cur_eligible_children", "fieldtype": "Int", "width": 260},
        {"label": "Enrolled Children in this month", "fieldname": "current_enrolled_children", "fieldtype": "Int", "width": 260},
        {"label": "Exited Children in this month", "fieldname": "current_exit_children", "fieldtype": "Int", "width": 260},
        {"label": "Average Attendance of this Month", "fieldname": "average_attendance", "fieldtype": "Data", "width": 260},
        {"label": "Min Attendance", "fieldname": "min_average_attendance", "fieldtype": "Data", "width": 200},
        {"label": "Max Attendance", "fieldname": "max_average_attendance", "fieldtype": "Data", "width": 200},
        {"label": "Above 75%", "fieldname": "above_75", "fieldtype": "Data", "width": 200},
        {"label": "50-75%", "fieldname": "between_50_75", "fieldtype": "Data", "width": 200},
        {"label": "Below 50%", "fieldname": "below_50", "fieldtype": "Data", "width": 200}
    ]

@frappe.whitelist()
def get_summary_data(filters=None):
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") if filters and filters.get("partner") else current_user_partner

    today = nowdate()
    year = int(filters.get("year") if filters and filters.get("year") else today.split('-')[0])
    month = int(filters.get("month") if filters and filters.get("month") else today.split('-')[1])
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])

    state_query = """
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s 
        ORDER BY ts.state_name
    """
    state_params = (partner_id,)
    user_states = frappe.db.sql(state_query, state_params, as_dict=True)
    state_id = filters.get("state") if filters and filters.get("state") else (user_states[0]['state_id'] if user_states else None)

    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "partner": partner_id,
        "state": state_id,
        "month": month,
        "year": year,
    }
    sql_query = """
    SELECT 
            s.state_name AS state,
            COUNT(*) AS operation_creches,
            IFNULL(cec.cumm_enrolled_children, 0) AS cumm_enrolled_children,
            IFNULL(cce.cumulative_exit_children, 0) AS cumulative_exit_children,
            IFNULL(cg.cumulative_graduate_children, 0) AS cumulative_graduate_children,
            IFNULL(celc.cur_eligible_children, 0) AS cur_eligible_children,
            IFNULL(crelc.current_enrolled_children, 0) AS current_enrolled_children,
            IFNULL(cexc.current_exit_children, 0) AS current_exit_children,
            ROUND((pc.total_children /nodco.co_days),2)  AS average_attendance,
            mx_att.minc AS min_average_attendance,
            mx_att.maxc AS max_average_attendance,
            pc.above_75 AS above_75,
            pc.between_75_50 AS between_50_75,
            pc.below_50 AS below_50
        
        FROM `tabCreche` c
        JOIN `tabState` s ON c.state_id = s.name
        JOIN `tabPartner` p ON c.partner_id = p.name
        LEFT JOIN (
            SELECT state_id, COUNT(*) AS cumm_enrolled_children
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_enrollment <= %(end_date)s
            AND (%(partner)s IS NULL OR partner_id = %(partner)s)
            AND (%(state)s IS NULL OR state_id = %(state)s)
            GROUP BY state_id
        ) cec ON c.state_id = cec.state_id
        LEFT JOIN (
            SELECT state_id, COUNT(*) AS cumulative_exit_children
            FROM `tabChild Enrollment and Exit`
            WHERE is_active = 0 AND is_exited = 1 AND date_of_exit <= %(end_date)s
            AND (%(partner)s IS NULL OR partner_id = %(partner)s)
            AND (%(state)s IS NULL OR state_id = %(state)s)
            GROUP BY state_id
        ) cce ON c.state_id = cce.state_id
        LEFT JOIN (
            SELECT state_id, COUNT(*) AS cumulative_graduate_children
            FROM `tabChild Enrollment and Exit`
            WHERE is_active = 0 AND reason_for_exit = 2 AND date_of_enrollment <= %(end_date)s
            AND (%(partner)s IS NULL OR partner_id = %(partner)s)
            AND (%(state)s IS NULL OR state_id = %(state)s)
            GROUP BY state_id
        ) cg ON c.state_id = cg.state_id
        LEFT JOIN (
            SELECT state_id, COUNT(hhc.name) AS cur_eligible_children
            FROM `tabHousehold Child Form` hhc
            JOIN `tabHousehold Form` hf ON hf.name = hhc.parent
            WHERE hhc.is_dob_available = 1 
            AND TIMESTAMPDIFF(MONTH, hhc.child_dob, %(end_date)s) BETWEEN 6 AND 36
            AND (%(partner)s IS NULL OR hf.partner_id = %(partner)s)
            AND (%(state)s IS NULL OR hf.state_id = %(state)s)
            GROUP BY state_id
        ) celc ON c.state_id = celc.state_id

        LEFT JOIN (
            SELECT state_id, COUNT(*) AS current_enrolled_children
            FROM `tabChild Enrollment and Exit`
            WHERE is_active = 1
            AND YEAR(date_of_enrollment) = %(year)s
            AND MONTH(date_of_enrollment) = %(month)s
            AND date_of_exit IS NULL
            AND (%(partner)s IS NULL OR partner_id = %(partner)s)
            AND (%(state)s IS NULL OR state_id = %(state)s)
            GROUP BY state_id
        ) crelc ON c.state_id = crelc.state_id


        LEFT JOIN (
            SELECT state_id, COUNT(*) AS current_exit_children
            FROM `tabChild Enrollment and Exit`
            WHERE is_active = 0 AND is_exited = 1 AND YEAR(date_of_exit) = %(year)s AND MONTH(date_of_exit) = %(month)s
            AND (%(partner)s IS NULL OR partner_id = %(partner)s)
            AND (%(state)s IS NULL OR state_id = %(state)s)
            GROUP BY state_id
        ) cexc ON c.state_id = cexc.state_id
        LEFT JOIN (
                SELECT 
                    ca.state_id,
                    COUNT(DISTINCT ca.date_of_attendance) AS co_days
                FROM `tabChild Attendance` ca
                INNER JOIN `tabChild Attendance List` cal ON ca.name = cal.parent
                WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0 
                AND YEAR(ca.date_of_attendance) = %(year)s 
                AND MONTH(ca.date_of_attendance) = %(month)s
                AND (%(partner)s IS NULL OR ca.partner_id = %(partner)s)
                AND (%(state)s IS NULL OR ca.state_id = %(state)s)
                GROUP BY ca.state_id  
        ) nodco ON c.state_id = nodco.state_id
        
        LEFT JOIN (
            SELECT  
                MAX(cc_prs) AS maxc, 
                MIN(cc_prs) AS minc, 
                aa.state_id
            FROM (
                SELECT 
                    ca.date_of_attendance,  
                    ca.state_id,
                    COUNT(cal.name) AS cc_prs  
                FROM 
                    `tabChild Attendance` AS ca
                INNER JOIN 
                    `tabChild Attendance List` AS cal ON ca.name = cal.parent  
                WHERE 
                    cal.attendance = 1  
                    AND ca.is_shishu_ghar_is_closed_for_the_day = 0  
                    AND YEAR(ca.date_of_attendance) = %(year)s  
                    AND MONTH(ca.date_of_attendance) = %(month)s  
                    AND (%(partner)s IS NULL OR ca.partner_id = %(partner)s)  
                    AND (%(state)s IS NULL OR ca.state_id = %(state)s)  
                GROUP BY 
                    ca.date_of_attendance, ca.state_id
            ) AS aa
            GROUP BY 
                aa.state_id
        ) AS mx_att ON c.state_id = mx_att.state_id
        LEFT JOIN (
            SELECT 
                state_id,
                COUNT(DISTINCT child_profile_id) AS total_children,
                SUM(CASE WHEN attendance_percentage > 75 THEN 1 ELSE 0 END) AS above_75,
                SUM(CASE WHEN attendance_percentage BETWEEN 50 AND 75 THEN 1 ELSE 0 END) AS between_75_50,
                SUM(CASE WHEN attendance_percentage < 50 THEN 1 ELSE 0 END) AS below_50
            FROM (
                WITH operational_days AS (
                    SELECT 
                        state_id,
                        COUNT(DISTINCT date_of_attendance) AS total_days
                    FROM `tabChild Attendance`
                    WHERE 
                        is_shishu_ghar_is_closed_for_the_day = 0  
                        AND YEAR(date_of_attendance) =  %(year)s   
                        AND MONTH(date_of_attendance) =  %(month)s 
                        AND (%(partner)s IS NULL OR partner_id = %(partner)s)
                        AND (%(state)s IS NULL OR state_id = %(state)s)
                    GROUP BY state_id
                )
                SELECT 
                    ca.state_id,
                    cal.child_profile_id,
                    (COUNT(cal.name) * 100.0 / od.total_days) AS attendance_percentage
                FROM `tabChild Attendance` ca
                INNER JOIN `tabChild Attendance List` cal ON ca.name = cal.parent
                INNER JOIN operational_days od ON ca.state_id = od.state_id
                WHERE 
                    cal.attendance = 1
                    AND ca.is_shishu_ghar_is_closed_for_the_day = 0  
                    AND YEAR(ca.date_of_attendance) =  %(year)s   
                    AND MONTH(ca.date_of_attendance) =  %(month)s 
                    AND (%(partner)s IS NULL OR ca.partner_id = %(partner)s)
                    AND (%(state)s IS NULL OR ca.state_id = %(state)s)
                GROUP BY ca.state_id, cal.child_profile_id, od.total_days
            ) AS attendance_data
            GROUP BY state_id
        
        ) as pc on pc.state_id = c.state_id
        
        WHERE 
        c.is_active = 1 
        AND c.creche_opening_date <=  %(end_date)s
        AND (%(partner)s IS NULL OR p.name = %(partner)s)
        AND (%(state)s IS NULL OR s.name = %(state)s)
        GROUP BY s.state_name
        ORDER BY s.state_name
"""

    return frappe.db.sql(sql_query, params, as_dict=True)
