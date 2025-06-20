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
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 250},
        {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 250},
        {"label": "No.of children's measurements taken in this month", "fieldname": "measurement_taken", "fieldtype": "Int", "width": 450},
        {"label": "No.of enrolled children as of this month", "fieldname": "cumm_enrolled_children", "fieldtype": "Int", "width": 350},
        {"label": "No.of children are stunted", "fieldname": "Stunted_Children", "fieldtype": "Int", "width": 250},
        {"label": "% of children are stunted", "fieldname": "Percentage", "fieldtype": "Float", "width": 250}
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
	SELECT s.state_name AS state,
			COUNT(*) AS operational_creches,
			IFNULL(cec.cumm_enrolled_children, 0) AS cumm_enrolled_children, 
			uc.uc AS Stunted_Children, 
			(uc.uc * 100) / cec.cumm_enrolled_children AS Percentage, 
			mt.measurements_taken AS measurement_taken
		FROM `tabCreche` c
		JOIN `tabState` s ON c.state_id = s.name
		JOIN `tabPartner` p ON c.partner_id = p.name
		
		LEFT JOIN (
			SELECT state_id, COUNT(*) AS cumm_enrolled_children 
			FROM `tabChild Enrollment and Exit` 
			WHERE is_active = 1 AND date_of_enrollment <= %(end_date)s 
			AND(%(partner)s IS NULL OR partner_id = %(partner)s) 
			AND (%(state)s IS NULL OR state_id = %(state)s)
			GROUP BY state_id
		) cec ON c.state_id = cec.state_id
		
		-- stuned chilldren
		
		LEFT JOIN (
			SELECT cgm.state_id, COUNT(DISTINCT ad.chhguid) AS uc 
			FROM `tabAnthropromatic Data` ad
			LEFT JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
			WHERE do_you_have_height_weight = 1 AND height_for_age < 3 AND height_for_age != 0 
			AND MONTH(ad.measurement_taken_date) = MONTH(%(end_date)s) 
			AND YEAR(ad.measurement_taken_date) = YEAR(%(end_date)s)
			AND(%(partner)s IS NULL OR cgm.partner_id = %(partner)s) 
			AND (%(state)s IS NULL OR cgm.partner_id = %(state)s)
			GROUP BY cgm.state_id
		) uc ON c.state_id = uc.state_id
		
		-- measurement taken
		LEFT JOIN (
			SELECT 
				state_id, 
				COUNT(*) AS measurements_taken
			FROM `tabAnthropromatic Data` AS ad
			LEFT JOIN `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
			WHERE 
				MONTH(ad.measurement_taken_date) = MONTH(%(end_date)s) 
				AND YEAR(ad.measurement_taken_date) = YEAR(%(end_date)s)
				AND(%(partner)s IS NULL OR cgm.partner_id = %(partner)s) 
				AND (%(state)s IS NULL OR cgm.partner_id = %(state)s)
			GROUP BY cgm.state_id
		) AS mt ON c.state_id = mt.state_id

		WHERE
		c.is_active = 1 
			AND c.creche_opening_date <= %(end_date)s
			AND (c.creche_closing_date IS NULL OR c.creche_closing_date > %(end_date)s)
			AND(%(partner)s IS NULL OR p.name = %(partner)s) 
			AND (%(state)s IS NULL OR s.name = %(state)s)
	GROUP BY s.state_name
		HAVING uc.uc > 0
		ORDER BY s.state_name;

    """

    return frappe.db.sql(sql_query, params, as_dict=True)
