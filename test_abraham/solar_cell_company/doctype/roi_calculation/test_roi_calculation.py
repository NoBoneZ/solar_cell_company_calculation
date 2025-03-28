# Copyright (c) 2025, NoBoneZ and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestROICalculation(FrappeTestCase):
    """
    Test case for the ROICalculation Doctype.
    """

    def setUp(self):
        """Create a test customer for ROI Calculation."""
        self.customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Test Customer",
            "email": "test@example.com"
        }).insert()

    def test_autoname_format(self):
        """Ensure autoname format follows 'customer-month-year-instance_count'."""
        roi_doc = frappe.get_doc({
            "doctype": "ROI Calculation",
            "customer": self.customer.name,
            "month": "January",
            "year": 2025
        })
        roi_doc.autoname()
        self.assertTrue(roi_doc.name.startswith(f"{self.customer.name}-January-2025-"))

    def test_unique_roi_document(self):
        """Ensure that a duplicate ROI Calculation document cannot be created."""
        frappe.get_doc({
            "doctype": "ROI Calculation",
            "customer": self.customer.name,
            "month": "February",
            "year": 2025
        }).insert()

        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({
                "doctype": "ROI Calculation",
                "customer": self.customer.name,
                "month": "February",
                "year": 2025
            }).insert()

    def tearDown(self):
        """Cleanup test data."""
        frappe.db.rollback()