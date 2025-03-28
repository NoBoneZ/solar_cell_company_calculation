# Copyright (c) 2025, NoBoneZ and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestCustomer(FrappeTestCase):

    def setUp(self):
        """Set up a test customer before running tests"""
        self.test_email = "test_customer@example.com"
        self.test_customer = frappe.get_doc({
            "doctype": "Customer",
            "first_name": "Test",
            "last_name": "Customer",
            "email": self.test_email
        }).insert(ignore_permissions=True)

    def tearDown(self):
        """Cleanup test customer after running tests"""
        frappe.db.delete("Customer", {"email": self.test_email})
        frappe.db.delete("User Permission", {"user": self.test_email})
        frappe.db.commit()

    def test_customer_creation(self):
        """Test if a Customer is created properly"""
        self.assertTrue(frappe.db.exists("Customer", self.test_customer.name))

    def test_create_user_permission(self):
        """Test if User Permission is created upon customer insert"""
        permission_exists = frappe.db.exists(
            "User Permission",
            {"user": self.test_email, "allow": "Customer", "for_value": self.test_customer.name}
        )
        self.assertTrue(permission_exists)

    def test_check_user_role(self):
        """Test if check_user_role correctly identifies user roles"""
        frappe.get_doc({
            "doctype": "Has Role",
            "parent": self.test_email,
            "role": "Customer",
            "parenttype": "User"
        }).insert(ignore_permissions=True)

        response = frappe.call(
            "test_abraham.solar_cell_company.doctype.customer.customer.check_user_role",
            email=self.test_email
        )
        self.assertTrue(response.get("exists"))
