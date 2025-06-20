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
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 200},
        {"label": "Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Data", "width": 200},
        {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Data", "width": 200},
        {"label": "Measurements Taken", "fieldname": "measurements_taken", "fieldtype": "Data", "width": 200},
        {"label": "Weight for age normal", "fieldname": "weight_for_age_normal", "fieldtype": "Data", "width": 200},
        {"label": "Weight for age moderate", "fieldname": "weight_for_age_moderate", "fieldtype": "Data", "width": 200},
        {"label": "Weight for age severe", "fieldname": "weight_for_age_severe", "fieldtype": "Data", "width": 200},
        {"label": "Height for age normal", "fieldname": "height_for_age_normal", "fieldtype": "Data", "width": 200},
        {"label": "Height for age moderate", "fieldname": "height_for_age_moderate", "fieldtype": "Data", "width": 200},
        {"label": "Height for age severe", "fieldname": "height_for_age_severe", "fieldtype": "Data", "width": 200},
        
        {"label": "Weight for height normal", "fieldname": "weight_for_height_normal", "fieldtype": "Data", "width": 200},
        {"label": "Weight for height moderate", "fieldname": "weight_for_height_moderate", "fieldtype": "Data", "width": 200},
        {"label": "Weight for height severe", "fieldname": "weight_for_height_severe", "fieldtype": "Data", "width": 200},
        
        {"label": "Red flag", "fieldname": "red_flag", "fieldtype": "Data", "width": 200}
    ]

@frappe.whitelist()
def get_summary_data(filters=None):
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") if filters and filters.get("partner") else current_user_partner

    today = nowdate()
    year = int(filters.get("year") if filters and filters.get("year") else today.split('-')[0])
    month = int(filters.get("month") if filters and filters.get("month") else today.split('-')[1])
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

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
        "partner_id": partner_id,
        "state_id": state_id,
        "month": month,
        "year": year,
    }



    sql_query = """
   SELECT 
        ts.state_name as state,
        COUNT(*) AS operational_creches,

        -- Enrolled children
        COALESCE(tceae.enr_chd, 0) AS enrolled_children,

        -- Measurements taken 
        COALESCE(gmchd.gm_chd, 0) AS measurements_taken,

        -- Weight for Age
        COALESCE(merged_data.weight_for_age_normal, 0) AS weight_for_age_normal,
        COALESCE(merged_data.weight_for_age_moderate, 0) AS weight_for_age_moderate,
        COALESCE(merged_data.weight_for_age_severe, 0) AS weight_for_age_severe,

        -- Height for Age
        COALESCE(merged_data.height_for_age_normal, 0) AS height_for_age_normal,
        COALESCE(merged_data.height_for_age_moderate, 0) AS height_for_age_moderate,
        COALESCE(merged_data.height_for_age_severe, 0) AS height_for_age_severe,

        -- Weight for Height
        COALESCE(merged_data.weight_for_height_normal, 0) AS weight_for_height_normal,
        COALESCE(merged_data.weight_for_height_moderate, 0) AS weight_for_height_moderate,
        COALESCE(merged_data.weight_for_height_severe, 0) AS weight_for_height_severe,
        
        -- Red flag condition
        COALESCE(merged_data.red_flag_count, 0) AS red_flag
        

    FROM 
        `tabCreche` tc
    INNER JOIN 
        `tabState` ts ON tc.state_id = ts.name

    -- Enrolled children
    LEFT JOIN (
        SELECT state_id, COUNT(*) AS enr_chd FROM `tabChild Enrollment and Exit` te 
        WHERE te.date_of_enrollment <= %(end_date)s
        AND is_active = 1 
        AND (%(partner_id)s IS NULL OR te.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR te.state_id = %(state_id)s)
        GROUP BY state_id) AS tceae ON tc.state_id = tceae.state_id


    -- Measurements taken
    LEFT JOIN (SELECT 
        state_id, 
        COUNT(ad.parent) AS gm_chd FROM `tabAnthropromatic Data` AS ad 
        LEFT JOIN `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
        WHERE MONTH(ad.measurement_taken_date) = MONTH(%(end_date)s) AND YEAR(ad.measurement_taken_date) = YEAR(%(end_date)s)
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        GROUP BY cgm.state_id
    ) AS gmchd ON gmchd.state_id = tc.state_id

    --  Data for Weight for Age, Height for Age, and Weight for Height
    LEFT JOIN (
        SELECT 
            cgm.state_id,

            -- Weight for Age
            COUNT(CASE WHEN ad.weight_for_age = 3 THEN 1 END) AS weight_for_age_normal,
            COUNT(CASE WHEN ad.weight_for_age = 2 THEN 1 END) AS weight_for_age_moderate,
            COUNT(CASE WHEN ad.weight_for_age = 1 THEN 1 END) AS weight_for_age_severe,

            -- Height for Age
            COUNT(CASE WHEN ad.height_for_age = 3 THEN 1 END) AS height_for_age_normal,
            COUNT(CASE WHEN ad.height_for_age = 2 THEN 1 END) AS height_for_age_moderate,
            COUNT(CASE WHEN ad.height_for_age = 1 THEN 1 END) AS height_for_age_severe,

            -- Weight for Height
            COUNT(CASE WHEN ad.weight_for_height = 3 THEN 1 END) AS weight_for_height_normal,
            COUNT(CASE WHEN ad.weight_for_height = 2 THEN 1 END) AS weight_for_height_moderate,
            COUNT(CASE WHEN ad.weight_for_height = 1 THEN 1 END) AS weight_for_height_severe,

            -- Red flag 
            COUNT(CASE WHEN ad.any_medical_major_illness = 1 AND ad.weight_for_age = 1 AND (ad.weight_for_height = 1 OR ad.weight_for_height = 2) THEN 1 END) AS red_flag_count

        FROM 
            `tabAnthropromatic Data` ad
        LEFT JOIN 
            `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
        WHERE 
            ad.do_you_have_height_weight = 1
            AND MONTH(ad.measurement_taken_date) = MONTH(%(end_date)s) 
            AND YEAR(ad.measurement_taken_date) = YEAR(%(end_date)s)
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (%(state_id)s IS NULL OR cgm.state_id = %(state_id)s)
        GROUP BY 
            cgm.state_id
    ) AS merged_data ON merged_data.state_id = tc.state_id
    WHERE 
        tc.is_active = 1 
        AND tc.creche_opening_date <= %(end_date)s
        AND (tc.creche_closing_date IS NULL OR tc.creche_closing_date > %(end_date)s)
        AND (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
        AND (%(state_id)s IS NULL OR tc.state_id = %(state_id)s)
    GROUP BY 
        tc.state_id
    ORDER BY 
        ts.state_name;

    """

    return frappe.db.sql(sql_query, params, as_dict=True)