import frappe
from frappe.utils import getdate

@frappe.whitelist(allow_guest=True)
def login(usr, pwd, app_device_id=None, app_device_version=None): 
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()

        user = frappe.get_cached_doc("User", frappe.session.user)
        device_changed = 0 

        if not app_device_id or not app_device_version:  
             frappe.response["message"] = "Please update your version to 2.1.2 or later."
             frappe.local.response["http_status_code"] = 403
             return
    

        required_version = "2.1.2"
        if app_device_version < required_version:
            frappe.response["message"] = "Please update your version to 2.1.2 or later."
            frappe.local.response["http_status_code"] = 403
            return
            

        if app_device_id and app_device_version:  
            if not user.app_device_id or not user.app_device_version or user.app_device_version != app_device_version:
                user.app_device_id = app_device_id
                user.app_device_version = app_device_version
                device_changed = 0  
                user.save()
                save_login_history(user, app_device_id, app_device_version) 

            if user.app_device_id != app_device_id:  
                device_changed = 1

        api_generate = generate_keys(user.name)

        if usr.isdigit(): 
            user_query = f"""SELECT name FROM `tabUser` WHERE mobile_no = '{usr}';"""
            user_name = frappe.db.sql(user_query, as_dict=True)
            if user_name:
                usr = user_name[0]['name']  

        query = f"""
            SELECT COUNT(*) AS nohh 
            FROM `tabHousehold Form` thf 
            INNER JOIN `tabUser Geography Mapping` tugm 
            ON thf.gp_id = tugm.gp_id 
            WHERE tugm.parent = '{usr}';
        """
        hh = frappe.db.sql(query, as_dict=False)

        if hh and hh[0]:  
            hh_value = hh[0][0]  
        else:
            hh_value = 0  
        
        mapping = []
        if hasattr(user, "mapping") and user.mapping:
            mapping = [
                {
                    "name": map_entry.name,
                    "owner": map_entry.owner,
                    "creation": str(map_entry.creation),
                    "modified": str(map_entry.modified),
                    "modified_by": str(map_entry.modified_by),
                    "docstatus": str(map_entry.docstatus),
                    "idx":(map_entry.idx),
                    "state_id": str(map_entry.state_id),
                    "district_id": str(map_entry.district_id),
                    "block_id": str(map_entry.block_id),
                    "gp_id": str(map_entry.gp_id),
                    "village_id": str(map_entry.village_id or ""),
                    "parent": map_entry.parent,
                    "parentfield": map_entry.parentfield,
                    "parenttype": map_entry.parenttype,
                    "doctype": map_entry.doctype,
                }
                for map_entry in user.mapping
            ]

        frappe.response["auth"] = {
            "success_key": 1,
            "message": "Authentication success",
            "sid": frappe.session.sid,
            "api_key": user.api_key,
            "api_secret": api_generate,
            "username": user.name,
            "role": user.type,
            "mapping": mapping,
            "partner": str(user.partner),
            "mobile_no": user.mobile_no,
            "app_device_id": user.app_device_id,
            "app_device_version": user.app_device_version,
            "is_device_changed": device_changed,
            "household": hh_value,
            "Back_data_entry_date": "2025-05-30"
        }

    except frappe.PermissionError:
        frappe.response["error"] = {
            "error_code": 402,
            "error_message": "Permission denied. Invalid App Device ID.",
        }
        frappe.local.response["http_status_code"] = 402  
        return

    except:
        frappe.throw(title="Error", msg="Invalid ID or Password")
        return

def generate_keys(usr):
    user_details = frappe.get_cached_doc("User", usr)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.token = f"token {user_details.api_key}:{user_details.api_secret}"
    user_details.save()

    return api_secret

def save_login_history(user, old_device_id, app_device_version, new_device_id=None):
    try:
        if not new_device_id:
            new_device_id = old_device_id
        
        login_history = frappe.get_doc({
            "doctype": "User Device Change Log",
            "mobile_no": user.mobile_no,
            "old_device_id": old_device_id,
            "new_device_id": new_device_id,
            "app_device_version": app_device_version
        })
        login_history.insert()
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "User Device Change Log Save Error")
        raise e

@frappe.whitelist(allow_guest=True)
def update_device_id(usr, pwd, app_device_id, app_device_version):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
        user = frappe.get_cached_doc("User", frappe.session.user)
        old_device_id = user.app_device_id
        user.app_device_id = app_device_id
        user.app_device_version = app_device_version
        user.save()

        save_login_history(user, old_device_id, app_device_version, app_device_id) 

        frappe.response["status code"] = {
            "status code": 200,
            "message": "Device ID updated successfully",
        }
        frappe.local.response["http_status_code"] = 200 
    except frappe.PermissionError:
        frappe.response["error"] = {
            "error_code": 502,
            "error_message": "Device ID not updated",
        }
        frappe.local.response["http_status_code"] = 502 
        return

#Child Attendance upload api
@frappe.whitelist(allow_guest=True)
def child_attendance():
    user = frappe.session.user
    auth = frappe.request.headers.get('Authorization')
    data_usr = frappe.get_doc("User", user)

    if data_usr.token == auth:
        data = frappe._dict(frappe.local.form_dict)
        query = """
            SELECT tcc.name, tcal.childenrolledguid, tcal.name as cname
            FROM `tabChild Attendance` tcc 
            LEFT JOIN `tabChild Attendance List` tcal 
            ON tcc.name = tcal.parent 
            WHERE tcc.date_of_attendance = %s AND tcc.creche_id = %s
        """

        existing_attendance = frappe.db.sql(query, (data.get("date_of_attendance"), data.get("creche_id")), as_dict=True)

        if existing_attendance:
            attendance_doc = frappe.get_doc("Child Attendance", existing_attendance[0].get("name"))
            attendance_doc.partner_id = data.partner_id
            attendance_doc.state_id = data.state_id
            attendance_doc.district_id = data.district_id
            attendance_doc.block_id = data.block_id
            attendance_doc.gp_id = data.gp_id
            attendance_doc.village_id = data.village_id
            attendance_doc.is_shishu_ghar_is_closed_for_the_day = data.is_shishu_ghar_is_closed_for_the_day
            attendance_doc.reason_for_closure_id = data.reason_for_closure_id
            attendance_doc.reason_other = data.reason_other
            attendance_doc.open_time = data.open_time
            attendance_doc.close_time = data.close_time
            attendance_doc.isecd_activities_done_for_the_day = data.isecd_activities_done_for_the_day
            attendance_doc.breakfast = data.breakfast
            attendance_doc.lunch = data.lunch
            attendance_doc.egg = data.egg
            attendance_doc.evening_snacks = data.evening_snacks
            attendance_doc.childattenguid = data.childattenguid
            if data.is_shishu_ghar_is_closed_for_the_day == 1:
                attendance_doc.childattendancelist = []
            attendance_doc.save()
        else:
            attendance_doc = frappe.get_doc({
                "doctype": "Child Attendance",
                "app_created_by": data.app_created_by,
                "app_created_on": data.app_created_on,
                "childattenguid": data.childattenguid,
                "creche_id": data.creche_id,
                "partner_id": data.partner_id,
                "state_id": data.state_id,
                "district_id": data.district_id,
                "block_id": data.block_id,
                "gp_id": data.gp_id,
                "village_id": data.village_id,
                "date_of_attendance": data.date_of_attendance,
                "is_shishu_ghar_is_closed_for_the_day": data.is_shishu_ghar_is_closed_for_the_day,
                "reason_for_closure_id": data.reason_for_closure_id,
                "reason_other": data.reason_other,
                "open_time": data.open_time,
                "close_time": data.close_time,
                "isecd_activities_done_for_the_day": data.isecd_activities_done_for_the_day,
                "app_updated_on": data.app_updated_on,
                "app_updated_by": data.app_updated_by,
                "breakfast": data.breakfast,
                "lunch": data.lunch,
                "egg": data.egg,
                "evening_snacks": data.evening_snacks,
                "childattendancelist": []
            })
            attendance_doc.insert()

        child_attendance_list = data.get("childattendancelist", [])
        for child_data in child_attendance_list:
            child_data = frappe._dict(child_data)
            existing_child_attendance = next(
                (item.get("cname") for item in existing_attendance if item.get("childenrolledguid") == child_data.childenrolledguid), 
                None
            )

            if existing_child_attendance:
                        child_attendance_detail_doc = frappe.get_doc("Child Attendance List", existing_child_attendance)
                        child_attendance_detail_doc.attendance = child_data.attendance
                        child_attendance_detail_doc.name_of_child = child_data.name_of_child
                        child_attendance_detail_doc.save()
            else:
                      frappe.get_doc({
                        "doctype": "Child Attendance List",
                        "parent": attendance_doc.name,
                        "parenttype": "Child Attendance",
                        "parentfield": "childattendancelist",
                        "childattenguid": child_data.childattenguid,
                        "date_of_attendance": child_data.date_of_attendance,
                        "childenrolledguid": child_data.childenrolledguid,
                        "attendance": child_data.attendance,
                        "name_of_child": child_data.name_of_child,
                        "child_profile_id": child_data.child_profile_id
                    }).insert()


        att = frappe.db.exists("Child Attendance", {
            "date_of_attendance": data.get("date_of_attendance"),
            "creche_id": data.get("creche_id"),
        })
        frappe.response["Data"] = frappe.get_doc("Child Attendance", att)

    else:
        frappe.response["Error"] = "Invalid API"
        raise frappe.AuthenticationError

#Child Growth Monitoring Api
#Child Growth Monitoring Api
@frappe.whitelist(allow_guest=True)
def growth_monitoring():
    user = frappe.session.user
    auth = frappe.request.headers.get('Authorization')
    data_usr = frappe.get_doc("User", user)

    if data_usr.token == auth:
        data = frappe._dict(frappe.local.form_dict)
        measurement_date = getdate(data.get("measurement_date"))
        year = measurement_date.year
        month = measurement_date.month
        creche_id = data.get("creche_id")

        existing_gm = frappe.db.sql("""
            SELECT name FROM `tabChild Growth Monitoring` WHERE creche_id = %s AND YEAR(measurement_date) = %s AND MONTH(measurement_date) = %s""",
            (creche_id, year, month), as_dict=True)

        if existing_gm:
            # Fetch full details for each record, including child data
            gm_details = []
            for gm in existing_gm:
                gm_doc = frappe.get_doc("Child Growth Monitoring", gm['name'])
                gm_data = gm_doc.as_dict()
                child_data = frappe.db.sql("""
                    SELECT * 
                    FROM `tabAnthropromatic Data`
                    WHERE parent = %s
                """, (gm_doc.name,), as_dict=True)

                gm_data["anthropromatic_details"] = child_data
                gm_details.append(gm_data)


        if existing_gm:
            gm_doc = frappe.get_doc("Child Growth Monitoring", existing_gm[0].name)
            gm_doc.update({
                "partner_id": data.partner_id,
                "state_id": data.state_id,
                "district_id": data.district_id,
                "block_id": data.block_id,
                "gp_id": data.gp_id,
                "village_id": data.village_id,
                "measurement_date": data.measurement_date,
                "created_by": data.created_by,
                "created_on": data.created_on,
                "updated_by": data.updated_by,
                "updated_on": data.updated_on,
                "updated_on": data.updated_on,
                "is_active": data.is_active,
                "cgmguid": data.cgmguid,
                "childenrollguid":data.childenrollguid
            })
            gm_doc.save(ignore_version=True)  
        else:
            gm_doc = frappe.get_doc({
                "doctype": "Child Growth Monitoring",
                "name": data.name,
                "partner_id": data.partner_id,
                "state_id": data.state_id,
                "district_id": data.district_id,
                "block_id": data.block_id,
                "gp_id": data.gp_id,
                "village_id": data.village_id,
                "creche_id": data.creche_id,
                "measurement_date": data.measurement_date,
                "created_by": data.created_by,
                "created_on": data.created_on,
                "is_active": data.is_active,
                "updated_by": data.updated_by,
                "updated_on": data.updated_on,
                "updated_on": data.updated_on,
                "cgmguid": data.cgmguid,
                "childenrollguid":data.childenrollguid
            })
            gm_doc.insert()

        anthropometric_details = data.get("anthropromatic_details", [])
        for child_data in anthropometric_details:
            child_data = frappe._dict(child_data)
            existing_child_attendance = frappe.db.exists("Anthropromatic Data", {
                "cgmguid": child_data.cgmguid,
                "childenrollguid": child_data.childenrollguid
            })

            if existing_child_attendance:
                gm_detail_doc = frappe.get_doc("Anthropromatic Data", existing_child_attendance)
                gm_detail_doc.created_on = child_data.created_on
                gm_detail_doc.modified_by = child_data.modified_by
                gm_detail_doc.measurement_taken_date = child_data.measurement_taken_date
                gm_detail_doc.measurement_equipment = child_data.measurement_equipment
                gm_detail_doc.child_id = child_data.child_id
                gm_detail_doc.height = child_data.height
                gm_detail_doc.weight = child_data.weight
                gm_detail_doc.age_months = child_data.age_months
                gm_detail_doc.weight_for_age = child_data.weight_for_age
                gm_detail_doc.weight_for_height = child_data.weight_for_height
                gm_detail_doc.height_for_age = child_data.height_for_age
                gm_detail_doc.any_medical_major_illness = child_data.any_medical_major_illness
                gm_detail_doc.awc = child_data.awc
                gm_detail_doc.thr = child_data.thr
                gm_detail_doc.vhsnd = child_data.vhsnd
                gm_detail_doc.cgmguid = child_data.cgmguid
                gm_detail_doc.do_you_have_height_weight = child_data.do_you_have_height_weight
                gm_detail_doc.measurement_reason = child_data.measurement_reason
                gm_detail_doc.childenrollguid = child_data.childenrollguid
                #For ZScore Data
                gm_detail_doc.weight_for_age_zscore = child_data.weight_for_age_zscore
                gm_detail_doc.weight_for_height_zscore = child_data.weight_for_height_zscore
                gm_detail_doc.height_for_age_zscore = child_data.height_for_age_zscore
                # field for other users
                gm_detail_doc.re_measurement_equipment = child_data.re_measurement_equipment
                gm_detail_doc.re_do_you_have_height_weight = child_data.re_do_you_have_height_weight
                gm_detail_doc.re_measurement_taken_date = child_data.re_measurement_taken_date
                gm_detail_doc.re_measurement_reason = child_data.re_measurement_reason
                gm_detail_doc.re_height = child_data.re_height
                gm_detail_doc.re_weight = child_data.re_weight
                gm_detail_doc.re_age_months = child_data.re_age_months
                gm_detail_doc.re_weight_for_age = child_data.re_weight_for_age
                gm_detail_doc.re_weight_for_height = child_data.re_weight_for_height
                gm_detail_doc.re_height_for_age = child_data.re_height_for_age

                gm_detail_doc.re_weight_for_age_zscore = child_data.re_weight_for_age_zscore
                gm_detail_doc.re_weight_for_height_zscore = child_data.re_weight_for_height_zscore
                gm_detail_doc.re_height_for_age_zscore = child_data.re_height_for_age_zscore
                gm_detail_doc.dob_when_measurement_taken = child_data.dob_when_measurement_taken
                gm_detail_doc.s_flag = child_data.s_flag
                if child_data.dob_when_measurement_taken:
                    gm_detail_doc.flag = 1 
                else :
                    gm_detail_doc.flag = 0 
                
                gm_detail_doc.save()  
            else:
                gm_detail_doc =   frappe.get_doc({
                    "doctype": "Anthropromatic Data",
                    "parent": gm_doc.name,
                    "parenttype": "Child Growth Monitoring",
                    "parentfield": "anthropromatic_details",
                    "name": child_data.name,
                    "owner": child_data.owner,
                    "creation": child_data.creation,
                    "modified": child_data.modified,
                    "modified_by": child_data.modified_by,
                    "docstatus": child_data.docstatus,
                    "idx": child_data.idx,
                    "measurement_equipment": child_data.measurement_equipment,
                    "child_id": child_data.child_id,
                    "do_you_have_height_weight": child_data.do_you_have_height_weight,
                    "height": child_data.height,
                    "weight": child_data.weight,
                    "age_months": child_data.age_months,
                    "weight_for_age": child_data.weight_for_age,
                    "weight_for_height": child_data.weight_for_height,
                    "height_for_age": child_data.height_for_age,
                    "any_medical_major_illness": child_data.any_medical_major_illness,
                    "awc": child_data.awc,
                    "thr": child_data.thr,
                    "vhsnd": child_data.vhsnd,
                    "cgmguid": child_data.cgmguid,
                    "chhguid": child_data.chhguid,
                    "childenrollguid": child_data.childenrollguid,
                    "measurement_taken_date": child_data.measurement_taken_date,
                    "measurement_reason": child_data.measurement_reason,
                    
                    "weight_for_age_zscore" : child_data.weight_for_age_zscore,
                    "weight_for_height_zscore" : child_data.weight_for_height_zscore,
                    "height_for_age_zscore" : child_data.height_for_age_zscore,
                    "dob_when_measurement_taken" : child_data.dob_when_measurement_taken,
                    "s_flag" : child_data.s_flag,
                    "flag": 1 if child_data.dob_when_measurement_taken else 0,
                    "parent": gm_doc.name,
                    "parentfield": "anthropromatic_details",
                    "parenttype": "Child Growth Monitoring"
                })
                gm_detail_doc.insert()

        cgm = frappe.db.exists("Child Growth Monitoring", {
            "measurement_date": data.get("measurement_date"),
            "creche_id": data.get("creche_id"),
        })
        frappe.response["Data"] = frappe.get_doc("Child Growth Monitoring", cgm)
    else:
        frappe.response["Error"] = "Invalid API"
        raise frappe.AuthenticationError

## Child Immunization api
@frappe.whitelist(allow_guest=True)
def child_immunization():
    user = frappe.session.user
    auth = frappe.request.headers.get("Authorization")
    data_usr = frappe.get_doc("User", user)

    if data_usr.token == auth:
        data = frappe._dict(frappe.local.form_dict)
        existing_vaccination = frappe.db.exists("Child Immunization", {
            "childenrolledguid": data.get("childenrolledguid"),
            "creche_id": data.get("creche_id"),
        })
        if existing_vaccination:
            vaccination_doc = frappe.get_doc("Child Immunization",existing_vaccination)
            vaccination_doc.partner_id = data.partner_id
            vaccination_doc.state_id = data.state_id
            vaccination_doc.district_id = data.district_id
            vaccination_doc.block_id = data.block_id
            vaccination_doc.gp_id = data.gp_id
            vaccination_doc.village_id = data.village_id
            vaccination_doc.creche_id = data.creche_id
            vaccination_doc.child_id = data.child_id
            vaccination_doc.childenrolledguid = data.childenrolledguid
            vaccination_doc.appcreated_by = data.appcreated_by
            vaccination_doc.appcreated_on = data.appcreated_on
            vaccination_doc.app_updated_on = data.app_updated_on
            vaccination_doc.app_updated_by = data.app_updated_by
            vaccination_doc.child_immunization_guid = data.child_immunization_guid
            vaccination_doc.save()
        else:
            vaccination_doc = frappe.get_doc({
                "doctype": "Child Immunization",
                "name": data.name,
                "app_created_by": data.app_created_by,
                "app_created_on": data.app_created_on,
                "creche_id": data.creche_id,
                "partner_id": data.partner_id,
                "state_id": data.state_id,
                "district_id": data.district_id,
                "block_id": data.block_id,
                "gp_id": data.gp_id,
                "child_id": data.child_id,
                "village_id": data.village_id,
                "childenrolledguid": data.childenrolledguid,
                "child_immunization_guid": data.child_immunization_guid,
                "vaccine_details": [],
            })
            vaccination_doc.insert()
        child_vaccine_list = data.get("vaccine_details", [])
        index = 1

        for child_data in child_vaccine_list:
            child_data = frappe._dict(child_data)
            existing_vaccines = frappe.db.exists("Vaccine Details", {
                "vaccine_id": child_data.vaccine_id,
                "parent": vaccination_doc.name
            })
            if existing_vaccines:
                child_vaccines_detail_doc = frappe.get_doc("Vaccine Details", existing_vaccines)
                child_vaccines_detail_doc.vaccination_date = child_data.vaccination_date
                child_vaccines_detail_doc.vaccinated = child_data.vaccinated
                child_vaccines_detail_doc.vaccine_created_at = child_data.vaccine_created_at
                child_vaccines_detail_doc.vaccine_updated_by = child_data.vaccine_updated_by
                child_vaccines_detail_doc.idx = index
                child_vaccines_detail_doc.save()
            else:
                new_vaccine_detail = frappe.get_doc({
                    "doctype": "Vaccine Details",
                    "parent": vaccination_doc.name,
                    "parenttype": "Child Immunization",
                    "parentfield": "vaccine_details",
                    "vaccine_id": child_data.vaccine_id,
                    "vaccination_date": child_data.vaccination_date,
                    "vaccinated": child_data.vaccinated,
                    "vaccine_created_at": child_data.vaccine_created_at,
                    "vaccine_updated_by": child_data.vaccine_updated_by,
                    "idx": index  
                })
                new_vaccine_detail.insert()
            index += 1

        imm = frappe.db.exists("Child Immunization", {
            "childenrolledguid": data.get("childenrolledguid"),
            "creche_id": data.get("creche_id"),
        })
        frappe.response["Data"] = frappe.get_doc("Child Immunization", imm)
    else:
        frappe.response["Error"] = "Invalid API"
        raise frappe.AuthenticationError