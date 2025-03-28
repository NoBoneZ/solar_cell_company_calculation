# Copyright (c) 2025, NoBoneZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Customer(Document):
	
	def after_insert(self):
		self.create_user_permission()


	def create_user_permission(self):
		frappe.get_doc(**dict(
			doctype="User Permission",
			allow="Customer",
			for_value=self.name,
			user=self.email,
			apply_to_all_doctypes=1
			)
		).insert()


@frappe.whitelist()
def check_user_role(email):
	"""Check if a user has the 'Customer' role."""
	return dict(dict(exists=bool(frappe.db.exists("Has Role", {"parent": email, "role": "Customer", "parenttype": "User"}))))


@frappe.whitelist()
def get_customer_users():
    """Fetch users who have the 'Customer' role."""
    return frappe.db.sql("""
        SELECT DISTINCT parent AS name 
        FROM `tabHas Role` 
        WHERE role = 'Customer' 
        AND parenttype = 'User'
    """, as_dict=True)