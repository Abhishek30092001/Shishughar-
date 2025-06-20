import frappe
from frappe import _
from frappe.utils import getdate
from datetime import datetime, timedelta
from frappe.utils.data import get_last_day
from dateutil.relativedelta import relativedelta

@frappe.whitelist(allow_guest=True)
def update_creche_summary():
    # Get all distinct years from attendance data
    years = frappe.db.sql_list("""
        SELECT DISTINCT YEAR(date_of_attendance) 
        FROM `tabChild Attendance` 
        ORDER BY YEAR(date_of_attendance) DESC
    """)
    
    if not years:
        return "No attendance data found to generate summary"

    for year in years:
        summary_data = {}
        
        # Get all Creche records
        creches = frappe.get_all("Creche", 
            fields=["name","creche_id", "partner_id", "state_id", "district_id", "block_id", 
                    "gp_id", "creche_name", "creche_opening_date",
                    "creche_closing_date", "creche_status_id", "phase", "supervisor_id"])
        
        # Initialize summary data structure
        for creche in creches:
            summary_data[creche.name] = {
                "partner_id": creche.partner_id,
                "partner_name": frappe.db.get_value("Partner", creche.partner_id, "partner_name"),
                "state_id": creche.state_id,
                "state_name": frappe.db.get_value("State", creche.state_id, "state_name"),
                "district_id": creche.district_id,
                "district_name": frappe.db.get_value("District", creche.district_id, "district_name"),
                "block_id": creche.block_id,
                "block_name": frappe.db.get_value("Block", creche.block_id, "block_name"),
                "gp_id": creche.gp_id,
                "gp_name": frappe.db.get_value("Gram Panchayat", creche.gp_id, "gp_name"),
                "creche_name": creche.creche_name,
                "creche_id": creche.name,  # name field is the creche_id
                "c_name": creche.name,      # same as creche_id
                "c_idx":creche.creche_id,
                "creche_opening_date": creche.creche_opening_date,
                "creche_closing_date": creche.creche_closing_date,
                "creche_status_id": creche.creche_status_id,
                "phase": creche.phase,
                "supervisor_id": creche.supervisor_id,
                "supervisor_name": frappe.db.get_value("User", creche.supervisor_id, "full_name"),
                "eligible_children": [0] * 12,  # Initialize with 12 zeros
                "enrolled_children": [0] * 12,
                "children_attendance_atleast_one_day": [0] * 12,
                "avg_attd_per_day": [0] * 12,
                "min_attd": [0] * 12,
                "max_attd": [0] * 12,
                "mean_attd": [0] * 12,
                "creche_status_by_day": ["0000000000000000000000000000000"] * 12  # Initialize with 31 zeros for each month
            }
        
        for month in range(1, 13):
            month_start = datetime(year, month, 1).date()
            month_end = get_last_day(month_start)

            # Get data for the month
            eligible_counts = get_eligible_children_counts(month_end, year)
            enrolled_counts = get_enrolled_children_counts(month_end, year)
            attendance_data = get_monthly_attendance_data(month_start, month_end, year)
            creche_status_data = get_creche_status_by_day(month_start, month_end, year)
            
            # Update counts for each creche
            for creche_id, count in eligible_counts.items():
                if creche_id:
                    creche_key = int(creche_id) 
                    if creche_key in summary_data:
                        summary_data[creche_key]["eligible_children"][month-1] = count
            
            for creche_id, count in enrolled_counts.items():
                if creche_id:
                    creche_key = int(creche_id) 
                    if creche_key in summary_data:
                        summary_data[creche_key]["enrolled_children"][month-1] = count

            for creche_id, data in attendance_data.items():
                if creche_id:
                    creche_key = int(creche_id) 
                    if creche_key in summary_data:
                        summary_data[creche_key]["children_attendance_atleast_one_day"][month-1] = data["unique_children"]
                        summary_data[creche_key]["avg_attd_per_day"][month-1] = data["avg_attendance"]
                        summary_data[creche_key]["min_attd"][month-1] = data["min_att"]
                        summary_data[creche_key]["max_attd"][month-1] = data["max_att"]
                        summary_data[creche_key]["mean_attd"][month-1] = data["mean_att"]

            # Update creche status by day
            for creche_id, status_string in creche_status_data.items():
                if creche_id:
                    creche_key = int(creche_id)
                    if creche_key in summary_data:
                        summary_data[creche_key]["creche_status_by_day"][month-1] = status_string

        # Save all records for this year
        for creche_id, summary in summary_data.items():
            try:
                doc_fields = {
                    "doctype": "Creche Summary",
                    "year": year,
                    **summary,
                    "eligible_children": "|".join(map(str, summary["eligible_children"])),
                    "enrolled_children": "|".join(map(str, summary["enrolled_children"])),
                    "children_attendance_atleast_one_day": "|".join(map(str, summary["children_attendance_atleast_one_day"])),
                    "avg_attd_per_day": "|".join(map(str, summary["avg_attd_per_day"])),
                    "min_attd": "|".join(map(str, summary["min_attd"])),
                    "max_attd": "|".join(map(str, summary["max_attd"])),
                    "mean_attd": "|".join(map(str, summary["mean_attd"])),
                    "creche_status_by_day": "|".join(summary["creche_status_by_day"])
                }

                existing = frappe.db.exists("Creche Summary", {"c_name": creche_id, "year": year})
                if existing:
                    doc = frappe.get_doc("Creche Summary", existing)
                    doc.update(doc_fields)
                    doc.save()
                else:
                    frappe.get_doc(doc_fields).insert()
                
                frappe.db.commit()
            except Exception as e:
                frappe.db.rollback()
                frappe.log_error(f"Failed to update creche summary for {creche_id} year {year}: {str(e)}")

    return f"Creche Summary updated successfully for years: {', '.join(map(str, years))}"

# New helper function to get creche status by day
def get_creche_status_by_day(start_date, end_date, year):
    # Get all dates in the month
    date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    
    # Get creche opening dates
    creche_opening_dates = frappe.db.sql("""
        SELECT name, creche_opening_date, creche_closing_date
        FROM `tabCreche`
    """, as_dict=1)
    opening_dates = {c["name"]: c["creche_opening_date"] for c in creche_opening_dates}
    closing_dates = {c["name"]: c["creche_closing_date"] for c in creche_opening_dates}
    
    # Get attendance data for the month
    attendance_data = frappe.db.sql("""
        SELECT creche_id, date_of_attendance, is_shishu_ghar_is_closed_for_the_day
        FROM `tabChild Attendance`
        WHERE date_of_attendance BETWEEN %(start)s AND %(end)s
        AND YEAR(date_of_attendance) = %(year)s
    """, {"start": start_date, "end": end_date, "year": year}, as_dict=1)
    
    # Organize attendance data by creche and date
    creche_attendance = {}
    for record in attendance_data:
        creche_id = record["creche_id"]
        date = record["date_of_attendance"]
        status = record["is_shishu_ghar_is_closed_for_the_day"]
        
        if creche_id not in creche_attendance:
            creche_attendance[creche_id] = {}
        
        creche_attendance[creche_id][date] = status
    
    # Build status strings for each creche
    status_strings = {}
    for creche_id in creche_attendance.keys():
        status_string = []
        for date in date_list:
            # Future date
            if date > datetime.now().date():
                status_string.append("8")
                continue
                
            # Check if creche was opened by this date
            if opening_dates.get(creche_id) and date < opening_dates[creche_id]:
                status_string.append("4")  # Not opened yet
                continue
                
            # Check if creche was closed by this date
            if closing_dates.get(creche_id) and date > closing_dates[creche_id]:
                status_string.append("2")  # Permanently closed
                continue
                
            # Check attendance record
            if date in creche_attendance.get(creche_id, {}):
                status = creche_attendance[creche_id][date]
                status_string.append("2" if status == 1 else "1")  # 2=closed, 1=open
            else:
                status_string.append("0")  # No data submitted
        
        # Pad with zeros to make 31 characters
        while len(status_string) < 31:
            status_string.append("0")
            
        status_strings[creche_id] = "".join(status_string[:31])  # Ensure exactly 31 characters
    
    return status_strings
def get_eligible_children_counts(reference_date, year):
    sql = """
        SELECT hf.creche_id, COUNT(hhc.name) as count
        FROM `tabHousehold Child Form` hhc
        JOIN `tabHousehold Form` hf ON hf.name = hhc.parent
        WHERE hhc.is_dob_available = 1
        AND TIMESTAMPDIFF(MONTH, hhc.child_dob, %(ref_date)s) BETWEEN 6 AND 36
        AND YEAR(hf.creation) <= %(year)s
        GROUP BY hf.creche_id
    """
    results = frappe.db.sql(sql, {"ref_date": reference_date, "year": year}, as_dict=1)
    return {r["creche_id"]: r["count"] for r in results}

def get_enrolled_children_counts(reference_date, year):
    sql = """
        SELECT creche_id, COUNT(*) as count
        FROM `tabChild Enrollment and Exit`
        WHERE date_of_enrollment <= %(ref_date)s
        AND (date_of_exit IS NULL OR date_of_exit > %(ref_date)s)
        AND YEAR(date_of_enrollment) <= %(year)s
        GROUP BY creche_id
    """
    results = frappe.db.sql(sql, {"ref_date": reference_date, "year": year}, as_dict=1)
    return {r["creche_id"]: r["count"] for r in results}

def get_monthly_attendance_data(start_date, end_date, year):
    unique_sql = """
        SELECT ca.creche_id, COUNT(DISTINCT cal.childenrolledguid) as count
        FROM `tabChild Attendance List` cal
        JOIN `tabChild Attendance` ca ON ca.name = cal.parent
        WHERE cal.attendance = 1
        AND ca.is_shishu_ghar_is_closed_for_the_day = 0
        AND ca.date_of_attendance BETWEEN %(start)s AND %(end)s
        AND YEAR(ca.date_of_attendance) = %(year)s
        GROUP BY ca.creche_id
    """
    unique_results = frappe.db.sql(unique_sql, {"start": start_date, "end": end_date, "year": year}, as_dict=1)
    
    stats_sql = """
        SELECT 
            creche_id,
            MIN(daily_count) as min_att,
            MAX(daily_count) as max_att,
            ROUND(AVG(daily_count)) as mean_att,
            ROUND(SUM(daily_count) * 1.0 / COUNT(*), 1) as avg_attendance
        FROM (
            SELECT 
                ca.creche_id,
                ca.date_of_attendance,
                COUNT(cal.name) as daily_count
            FROM `tabChild Attendance` ca
            JOIN `tabChild Attendance List` cal ON ca.name = cal.parent
            WHERE cal.attendance = 1
            AND ca.is_shishu_ghar_is_closed_for_the_day = 0
            AND ca.date_of_attendance BETWEEN %(start)s AND %(end)s
            AND YEAR(ca.date_of_attendance) = %(year)s
            GROUP BY ca.creche_id, ca.date_of_attendance
        ) as daily_data
        GROUP BY creche_id
    """
    stats_results = frappe.db.sql(stats_sql, {"start": start_date, "end": end_date, "year": year}, as_dict=1)

    data = {}
    for r in unique_results:
        data[r["creche_id"]] = {
            "unique_children": r["count"],
            "min_att": 0,
            "max_att": 0,
            "mean_att": 0,
            "avg_attendance": 0
        }

    for r in stats_results:
        if r["creche_id"] not in data:
            data[r["creche_id"]] = {}
        data[r["creche_id"]].update({
            "min_att": r["min_att"] or 0,
            "max_att": r["max_att"] or 0,
            "mean_att": r["mean_att"] or 0,
            "avg_attendance": r["avg_attendance"] or 0
        })

    return data



@frappe.whitelist(allow_guest=True)
def update_child_attendance_summary():
    # Fetch all attendance data with year information
    children_data = frappe.db.sql("""
        SELECT 
            cal.childenrolledguid,
            cal.childattenguid,
            cal.child_profile_id,
            cal.name_of_child,
            cal.date_of_attendance,
            cal.attendance,
            YEAR(cal.date_of_attendance) as year,
            cex.date_of_enrollment,
            cex.date_of_exit,
            cex.hhcguid,
            cex.hhguid,
            ca.partner_id,
            p.partner_name,
            ca.state_id,
            s.state_name,
            ca.district_id,
            d.district_name,
            ca.block_id,
            b.block_name,
            ca.gp_id,
            gp.gp_name,
            ca.creche_id,
            c.creche_id as c_idx,
            c.creche_name,
            c.phase,
            c.supervisor_id,
            sup.full_name as supervisor_name,
            c.creche_status_id,
            c.creche_opening_date,
            c.creche_closing_date,
            IF(cex.gender_id = 1, 'M', 'F') AS gender_id,
            cex.age_at_enrollment_in_months,
            cex.child_id,
            ca.is_shishu_ghar_is_closed_for_the_day
        FROM `tabChild Attendance List` cal
        JOIN `tabChild Attendance` ca ON ca.name = cal.parent
        JOIN `tabChild Enrollment and Exit` cex ON cal.childenrolledguid = cex.childenrollguid
        JOIN `tabPartner` p ON p.name = cex.partner_id
        JOIN `tabState` s ON s.name = cex.state_id
        JOIN `tabDistrict` d ON d.name = cex.district_id
        JOIN `tabBlock` b ON b.name = cex.block_id
        JOIN `tabGram Panchayat` gp ON gp.name = cex.gp_id
        JOIN `tabCreche` c ON c.name = cex.creche_id
        JOIN `tabUser` sup ON sup.name = c.supervisor_id
        ORDER BY cal.childenrolledguid, cal.date_of_attendance
    """, as_dict=True)

    # Group by child and year
    children = {}
    for record in children_data:
        child_id = record['childenrolledguid']
        year = record['year']
        
        if child_id not in children:
            children[child_id] = {}
            
        if year not in children[child_id]:
            children[child_id][year] = {
                'childenrolledguid': record['childenrolledguid'],
                'childattenguid': record['childattenguid'],
                'child_profile_id': record['child_profile_id'],
                'child_id': record['child_id'],
                'name_of_child': record['name_of_child'],
                'gender_id': record['gender_id'],
                'age_at_enrollment_in_months': record['age_at_enrollment_in_months'],
                'date_of_enrollment': record['date_of_enrollment'],
                'date_of_exit': record['date_of_exit'],
                'hhcguid': record['hhcguid'],
                'hhguid': record['hhguid'],
                'partner_id': record['partner_id'],
                'partner_name': record['partner_name'],
                'state_id': record['state_id'],
                'state_name': record['state_name'],
                'district_id': record['district_id'],
                'district_name': record['district_name'],
                'block_id': record['block_id'],
                'block_name': record['block_name'],
                'gp_id': record['gp_id'],
                'gp_name': record['gp_name'],
                'creche_id': record['creche_id'],
                'creche_name': record['creche_name'],
                'c_idx': record['c_idx'],
                "supervisor_id": record['supervisor_id'],
                "supervisor_name": record['supervisor_name'],
                'phase': record['phase'],
                'creche_status_id': record['creche_status_id'],
                'creche_opening_date': record['creche_opening_date'],
                'creche_closing_date': record['creche_closing_date'],
                'year': year,
                'attendance_records': [],
                'eligible_days': {m: 0 for m in range(1, 13)},
                'present_days': {m: 0 for m in range(1, 13)},
                'absent_days': {m: 0 for m in range(1, 13)}
            }
        
        children[child_id][year]['attendance_records'].append({
            'date': record['date_of_attendance'],
            'status': record['attendance'],
            'is_creche_open': not record['is_shishu_ghar_is_closed_for_the_day']
        })

    # Process attendance for each child-year combination
    result = []
    for child_id in children:
        for year in children[child_id]:
            child_data = children[child_id][year]
            enrollment_date = getdate(child_data['date_of_enrollment'])
            exit_date = getdate(child_data['date_of_exit']) if child_data['date_of_exit'] else None
            
            # Initialize data structures
            monthly_attendance = {m: ['0']*31 for m in range(1, 13)}
            
            for record in child_data['attendance_records']:
                date = getdate(record['date'])
                month = date.month
                day = date.day - 1  # 0-based index
                
                if day >= 31:
                    continue
                    
                # Determine status code
                if exit_date and date > exit_date:
                    code = '8'
                elif date < enrollment_date:
                    code = '0'
                elif record['status'] is None:
                    code = '4'
                elif record['status'] == 1:
                    code = '1'
                    if record['is_creche_open']:
                        child_data['present_days'][month] += 1
                else:
                    code = '2'
                    if record['is_creche_open']:
                        child_data['absent_days'][month] += 1
                
                # Count eligible days (creche open days)
                if record['is_creche_open'] and enrollment_date <= date and (not exit_date or date <= exit_date):
                    child_data['eligible_days'][month] += 1
                    
                monthly_attendance[month][day] = code
            
            # Build strings for each field
            attendance_str = "|".join("".join(monthly_attendance[month]) for month in range(1, 13))
            eligible_str = "|".join(str(child_data['eligible_days'][month]) for month in range(1, 13))
            present_str = "|".join(str(child_data['present_days'][month]) for month in range(1, 13))
            absent_str = "|".join(str(child_data['absent_days'][month]) for month in range(1, 13))
            
            # Calculate attend_slot
            attend_slot = []
            for month in range(1, 13):
                eligible = child_data['eligible_days'][month]
                present = child_data['present_days'][month]
                
                if eligible == 0:
                    attend_slot.append('0')
                else:
                    percentage = (present / eligible) * 100
                    if percentage == 0:
                        slot = '0'
                    elif 0 < percentage <= 25:
                        slot = '1'
                    elif 25 < percentage <= 50:
                        slot = '2'
                    elif 50 < percentage <= 75:
                        slot = '3'
                    elif 75 < percentage < 100:
                        slot = '4'
                    else:
                        slot = '5'
                    attend_slot.append(slot)
            
            attend_slot_str = "|".join(attend_slot)
            
            # Prepare the output record with ALL required fields
            output_record = {
                'doctype': 'Child Attendance Summary',
                'partner_id': child_data['partner_id'],
                'state_id': child_data['state_id'],
                'district_id': child_data['district_id'],
                'block_id': child_data['block_id'],
                'gp_id': child_data['gp_id'],
                'creche_id': child_data['creche_id'],
                'childenrolledguid': child_data['childenrolledguid'],
                'childattenguid': child_data['childattenguid'],
                'child_profile_id': child_data['child_profile_id'],
                'hhcguid': child_data['hhcguid'],
                'hhguid': child_data['hhguid'],
                'name_of_child': child_data['name_of_child'],
                'child_id': child_data['child_id'],
                'gender_id': child_data['gender_id'],
                'age_at_enrollment_in_months': child_data['age_at_enrollment_in_months'],
                'date_of_enrollment': child_data['date_of_enrollment'],
                'date_of_exit': child_data['date_of_exit'],
                'year': year,
                'attendance': attendance_str,
                'eligible_days': eligible_str,
                'present_days': present_str,
                'absent_days': absent_str,
                'attend_slot': attend_slot_str,
                'partner_name': child_data['partner_name'],
                'state_name': child_data['state_name'],
                'district_name': child_data['district_name'],
                'block_name': child_data['block_name'],
                'gp_name': child_data['gp_name'],
                'creche_name': child_data['creche_name'],
                'c_idx': child_data['c_idx'],
                "supervisor_id": child_data['supervisor_id'],
                "supervisor_name": child_data['supervisor_name'],
                'phase': child_data['phase'],
                'creche_status_id': child_data['creche_status_id'],
                'creche_opening_date': child_data['creche_opening_date'],
                'creche_closing_date': child_data['creche_closing_date']
            }
            
            # Check if record exists
            exists = frappe.db.exists("Child Attendance Summary", {
                "childenrolledguid": child_data['childenrolledguid'],
                "year": year
            })
            
            if exists:
                # Update existing record
                doc = frappe.get_doc("Child Attendance Summary", exists)
                doc.update(output_record)
                doc.save(ignore_permissions=True)
            else:
                # Create new record
                doc = frappe.get_doc(output_record)
                doc.insert(ignore_permissions=True)
            
            frappe.db.commit()
            result.append(output_record)
    
    return {
        'status': 'success',
        'data' : output_record,
        'records_processed': len(result)
    }
