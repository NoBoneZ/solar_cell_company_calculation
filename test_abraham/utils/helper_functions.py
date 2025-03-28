import frappe

def response(message, status_code, data=None, error=None):
    """This method generates a response for an API call with appropriate data and status code.

    Args:
        message (str): Message to be shown depending upon API result. Eg: Success/Error/Forbidden/Bad Request.
        status_code (int): Status code of API response.
        data (Any, optional): Any data to be passed as response (Dict, List, etc). Defaults to None.
    """

    try:
        frappe.local.response["message"] = message
        frappe.local.response["http_status_code"] = status_code
        frappe.local.response["status_code"] = status_code
        if data:
            frappe.local.response["data"] = data
        elif error:
            frappe.local.response["error"] = error
        return
    except Exception as e:
        frappe.log_error(title="API Response", message=frappe.get_traceback())


@frappe.whitelist
def filtered_get_list(doctype, *args, **kwargs):
    """Modify queries to restrict access based on the logged-in user."""
    
    if frappe.session.user != "Administrator":
        # Get the customer linked to the logged-in user
        customer = frappe.get_value("Customer", {"user": frappe.session.user}, "name")
        
        if customer:
            # Ensure only records belonging to the customer are returned
            if not kwargs.get("filters"):
                kwargs["filters"] = {}
            kwargs["filters"]["customer"] = customer

    return frappe.desk.reportview.get(doctype, *args, **kwargs)