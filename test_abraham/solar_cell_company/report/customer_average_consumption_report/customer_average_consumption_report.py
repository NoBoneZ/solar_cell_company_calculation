import frappe

def execute(filters=None):
    # Default filters to use all records if none are provided
    from_date = filters.get("from_date") if filters and filters.get("from_date") else "0000-01-01"
    to_date = filters.get("to_date") if filters and filters.get("to_date") else "9999-12-31"
    
    # Define columns for the report
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Customer Full Name", "fieldname": "full_name", "fieldtype": "Data", "width": 200},
        {"label": "Average kW", "fieldname": "average_kw", "fieldtype": "Float", "width": 150},
        {"label": "Average kWh", "fieldname": "average_kwh", "fieldtype": "Float", "width": 150},
    ]
    
    # Query to fetch average power consumption per customer
    data = frappe.db.sql(
        """
        SELECT 
            pc.customer,
            c.full_name AS full_name,
            AVG(pc.kwh) AS average_kw,
            AVG(pc.kwh__) AS average_kwh
        FROM `tabPower Consumption` pc
        LEFT JOIN `tabCustomer` c ON pc.customer = c.name
        WHERE pc.date BETWEEN %s AND %s
        GROUP BY pc.customer, c.customer_name
        """,
        (from_date, to_date),
        as_dict=True
    )
    
    return columns, data