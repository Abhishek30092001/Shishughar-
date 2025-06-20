import frappe

def global_validate_logger(doc, method):
    # Log details
    log_message = f"Validating {doc.doctype}: {doc.name}"
    
    # Log to frappe's logger (optional)
    frappe.logger().info(log_message)
    
    # Create a log entry in the Log Entry doctype
    create_log_entry(doc.doctype, doc.name, 'validate', log_message)

def create_log_entry(doctype_name, docname, event, message):
    log_entry = frappe.get_doc({
        "doctype": "Log Entry",
        "doctype_name": doctype_name,
        "docname": docname,
        "event": event,
        "message": message
    })
    log_entry.insert(ignore_permissions=True)
    frappe.db.commit()
