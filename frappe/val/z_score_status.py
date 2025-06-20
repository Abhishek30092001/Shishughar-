from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate
from frappe.model.document import Document
import math
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from collections import defaultdict
def calculate_z_score(value, M, L, S):
    if L == 0:
        raise ValueError("L should not be zero to avoid division errors.")
    ratio = float(value / M)
    ratio_to_L = float(math.pow(ratio, L))
    numerator = float(ratio_to_L - 1)
    denominator = float(S * L)
    z_score = float(numerator / denominator)
    if z_score <= -3:
        sd3neg = float(M * math.pow(1 + L * S * (-3), 1 / L))
        sd2neg = float(M * math.pow(1 + L * S * (-2), 1 / L))
        sd23neg = float(sd2neg - sd3neg)
        z_score = float(-3 + (value - sd3neg) / sd23neg)
    elif z_score >= 3:
        sd3pos = float(M * math.pow(1 + L * S * (3), 1 / L))
        sd2pos = float(M * math.pow(1 + L * S * (2), 1 / L))
        sd23pos = float(sd3pos - sd2pos)
        z_score = float(3 + (value - sd3pos) / sd23pos)
    return round(z_score, 2)


@frappe.whitelist(allow_guest=True)
def trigger_growth_status_update():
    frappe.enqueue(
        "frappe.val.z_score_status.update_growth_status_for_all_children",
        queue='long',
        timeout=1800
    )
    return "Update task has been enqueued"

def update_growth_status_for_all_children():
    cgm_list = frappe.get_all(
        "Child Growth Monitoring",
        filters={"docstatus": 0, "do_you_have_height_weight":1 , "flag" : 0 },
        fields=["name"]
    )

    for cgm in cgm_list:
        update_growth_status_for_child(cgm.name)

# @frappe.whitelist(allow_guest=True)
# def update_growth_status_for_all_children():
#     # Get date range for last month
#     today = date.today()
#     first_day_of_current_month = today.replace(day=1)
#     last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
#     first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

#     cgm_list = frappe.get_all(
#         "Child Growth Monitoring",
#         filters={
#             "docstatus": 0,
#             "measurement_date": ["between", [first_day_of_previous_month, last_day_of_previous_month]]
#         },
#         fields=["name"]
#     )
    
#     for cgm in cgm_list:
#         update_growth_status_for_child(cgm.name)

def update_growth_status_for_child(cgm_name):
    cgm = frappe.get_doc("Child Growth Monitoring", cgm_name)
    weight_for_age_boys_data = get_weight_for_age_boys_table()
    weight_for_age_girls_data = get_weight_for_age_girls_table()
    weight_to_height_boys_data = get_weight_to_height_boys()
    weight_to_height_girls_data = get_weight_to_height_girls()
    height_for_age_boys_data = get_height_for_age_boys()
    height_for_age_girls_data = get_height_for_age_girls()
    if cgm.get("anthropromatic_details"):

        for row in cgm.get("anthropromatic_details"):

            # if not row.do_you_have_height_weight or row.flag == 1:
            #     continue
            age_months = row.age_months
            guid = row.childenrollguid.strip()
            gender_id = frappe.db.get_value("Child Enrollment and Exit",{"childenrollguid": guid},"gender_id")
            weight = row.weight
            height = row.height
            measurement_equipment = row.measurement_equipment

            weight_for_age_status = None
            weight_for_height_status = None
            height_for_age_status = None

            # Calculating dob_when_measurement_taken
            if row.measurement_taken_date and age_months:
                try:
                    measurement_date = row.measurement_taken_date
                    age_days = age_months  

                    dob_date = measurement_date - timedelta(days=age_days)

                    row.dob_when_measurement_taken = dob_date
                except Exception as e:
                    frappe.msgprint(f"Error: {e}", "Error")
                    row.dob_when_measurement_taken = None
            else:
                row.dob_when_measurement_taken = None

            
          # weight for age
            if age_months is not None and weight is not None and weight > 0 and gender_id in ('1', '2'):
                try:
                    age_in_days = int(age_months)
                    weight = float(weight)
                    growth_data = weight_for_age_boys_data.get(age_in_days) if gender_id == '1' else weight_for_age_girls_data.get(age_in_days)
                    if growth_data:
                        try:
                            sd3neg = float(growth_data.get("sd3neg", 0))
                            sd2neg = float(growth_data.get("sd2neg", 0))
                            sd2 = float(growth_data.get("sd2", 0))
                            if weight < sd3neg:
                                weight_for_age_status = 1
                            elif weight >= sd3neg and weight < sd2neg:
                                weight_for_age_status = 2
                            elif weight >= sd2neg and weight <= sd2:
                                weight_for_age_status = 3
                            elif weight > sd2:
                                weight_for_age_status = 4
                        except (ValueError, TypeError):
                            pass
                except (ValueError, TypeError):
                    pass
            # weight for height

            if height is not None and weight is not None and weight > 0 and height > 0 and gender_id in ('1', '2'):
              try:
                  height_rounded = round(height,1) # Round Removed
                  weight = float(weight)
                  age_in_days = int(age_months)
                  
                  age_type_0_boys = {
                      height: next(
                          (record for record in records if str(record.get('age_type')).strip() in ['0', '0.0']),
                          None
                      )
                      for height, records in weight_to_height_boys_data.items()
                  }

                  age_type_24_boys = {
                      height: next(
                          (record for record in records if str(record.get('age_type')).strip() in ['24', '24.0']),
                          None
                      )
                      for height, records in weight_to_height_boys_data.items()
                  }

                  age_type_0_girls = {
                      height: next(
                          (record for record in records if str(record.get('age_type')).strip() in ['0', '0.0']),
                          None
                      )
                      for height, records in weight_to_height_girls_data.items()
                  }

                  age_type_24_girls = {
                      height: next(
                          (record for record in records if str(record.get('age_type')).strip() in ['24', '24.0']),
                          None
                      )
                      for height, records in weight_to_height_girls_data.items()
                  }


                  wfh_growth_data = None
                  if age_in_days <= 730:
                      if measurement_equipment == 'Stadiometer':
                          height_rounded = round(height_rounded + 0.7,1)

                  if age_in_days > 730:
                      if measurement_equipment == 'Infantometer':
                          height_rounded = round(height_rounded - 0.7,1)

                  if age_in_days <= 730:
                      if gender_id == '1':
                          wfh_growth_data = age_type_0_boys.get(height_rounded)
                      else:
                          wfh_growth_data = age_type_0_girls.get(height_rounded)

                  if age_in_days > 730:
                      if gender_id == '1':
                          wfh_growth_data = age_type_24_boys.get(height_rounded)
                      else:
                          wfh_growth_data = age_type_24_girls.get(height_rounded)


                  if wfh_growth_data:
                      try:
                          L = float(wfh_growth_data.get("l", 0))
                          M = float(wfh_growth_data.get("m", 0))
                          S = float(wfh_growth_data.get("s", 0))
                          z_score = calculate_z_score(weight, M, L, S)
                          
                          sd3neg = float(wfh_growth_data.get("sd3neg", 0))
                          sd2neg = float(wfh_growth_data.get("sd2neg", 0))
                          sd2 = float(wfh_growth_data.get("sd2", 0))

                          if weight < sd3neg:
                            weight_for_height_status = 1
                          elif weight >= sd3neg and weight < sd2neg:
                            weight_for_height_status = 2
                          elif weight >= sd2neg and weight <= sd2:
                            weight_for_height_status = 3
                          elif weight > sd2:
                            weight_for_height_status = 4
                          
                      except (ValueError, TypeError):
                          pass
              except (ValueError, TypeError):
                  pass

          # height for age
            if age_months is not None and height is not None and height > 0 and gender_id in ('1', '2'):
                try:
                    age_in_days = int(age_months)
                    height = float(height)
                    if measurement_equipment and row.measurement_taken_date:
                        measurement_date = row.measurement_taken_date
                        if isinstance(measurement_date, str):
                            measurement_date = datetime.strptime(measurement_date, "%Y-%m-%d").date()
                        two_years_ago = measurement_date - relativedelta(months=24)
                        dob = measurement_date - timedelta(days=age_in_days)
                        if dob > two_years_ago:
                            if measurement_equipment == '1':
                                height += 0.7
                        else:
                            if measurement_equipment == '2':
                                height -= 0.7
                    growth_data = height_for_age_boys_data.get(age_in_days) if gender_id == '1' else height_for_age_girls_data.get(age_in_days)
                    if growth_data:
                        try:
                            sd3neg = float(growth_data.get("sd3neg", 0))
                            sd2neg = float(growth_data.get("sd2neg", 0))
                            sd2 = float(growth_data.get("sd2", 0))
                            if height < sd3neg:
                                height_for_age_status = 1
                            elif height >= sd3neg and height < sd2neg:
                                height_for_age_status = 2
                            elif height >= sd2neg and height <= sd2:
                                height_for_age_status = 3
                            else:
                                height_for_age_status = 4
                        except (ValueError, TypeError):
                            pass
                except (ValueError, TypeError):
                    pass

            child_doctype = "Anthropromatic Data"
                        
            if weight_for_age_status is not None:
                frappe.db.set_value(child_doctype, row.name, "weight_for_age", weight_for_age_status)
            if weight_for_height_status is not None:
                frappe.db.set_value(child_doctype, row.name, "weight_for_height", weight_for_height_status)
            if height_for_age_status is not None:
                frappe.db.set_value(child_doctype, row.name, "height_for_age", height_for_age_status)

            if row.dob_when_measurement_taken is not None:
                dob_date = row.dob_when_measurement_taken
                if isinstance(dob_date, datetime):
                    dob_date = dob_date.date()
                frappe.db.set_value(child_doctype, row.name, "dob_when_measurement_taken", dob_date)
            
            frappe.db.set_value(child_doctype, row.name, "flag", 1)
            frappe.db.commit()

# --- Helper functions unchanged ---
def get_wfh_data_for_age(data_dict, height, age_type):
    if height in data_dict:
        for record in data_dict[height]:
            if str(record.get('age_type')).strip() in [age_type, f"{age_type}.0"]:
                return record
    return None

def get_weight_for_age_boys_table():
    fields = ["age_in_days", "l", "m", "s", "sd3neg", "sd2neg", "sd2"]
    records = frappe.get_all("Weight for age Boys", fields=fields)
    return {row["age_in_days"]: row for row in records}

def get_weight_for_age_girls_table():
    fields = ["age_in_days", "l", "m", "s", "sd3neg", "sd2neg", "sd2"]
    records = frappe.get_all("Weight for age Girls", fields=fields)
    return {row["age_in_days"]: row for row in records}


def get_weight_to_height_boys():
    """Returns all weight-to-height data for boys, preserving duplicate lengths"""
    fields = [
        "age_type", "length", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    
    try:
        records = frappe.get_all("Weight to Height Boys",
                              fields=fields,
                              limit=0)  # Get all records
        
        # Group by length while preserving all records
        data = defaultdict(list)
        for row in records:
            data[row["length"]].append(row)
            
        return dict(data)
        
    except Exception as e:
        frappe.log_error(f"Error loading boys data: {str(e)}")
        return {}

def get_weight_to_height_girls():
    """Returns all weight-to-height data for girls, preserving duplicate lengths"""
    fields = [
        "age_type", "length", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    
    try:
        records = frappe.get_all("Weight to Height Girls",
                              fields=fields,
                              limit=0)  # Get all records
        
        # Group by length while preserving all records
        data = defaultdict(list)
        for row in records:
            data[row["length"]].append(row)
            
        return dict(data)
        
    except Exception as e:
        frappe.log_error(f"Error loading girls data: {str(e)}")
        return {}

def get_height_for_age_boys():
    fields = ["age_in_days", "l", "m", "s", "sd3neg", "sd2neg", "sd2"]
    records = frappe.get_all("Height for age Boys", fields=fields)
    return {row["age_in_days"]: row for row in records}

def get_height_for_age_girls():
    fields = ["age_in_days", "l", "m", "s", "sd3neg", "sd2neg", "sd2"]
    records = frappe.get_all("Height for age Girls", fields=fields)
    return {row["age_in_days"]: row for row in records}



