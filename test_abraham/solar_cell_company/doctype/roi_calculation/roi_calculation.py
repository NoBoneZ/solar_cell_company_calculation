# Copyright (c) 2025, NoBoneZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class ROICalculation(Document):
	"""
	Represents an ROI Calculation document, which stores monthly ROI calculations 
	for a customer based on power consumption data.
	"""

	def autoname(self):
		"""
		Automatically generates a unique name for the ROI Calculation document.
		The naming format is: `customer-month-year-instance_count`
		- Counts existing ROI documents for the same customer.
		- Ensures unique identification when multiple ROI calculations exist for a month.
		"""
		number_of_customer = frappe.db.sql(
			"""
			SELECT COUNT(*) as customer_count 
			FROM `tabROI Calculation` 
			WHERE customer = %s
			""",
			(self.customer,),
			as_dict=True
		)[0].get("customer_count", 0)

		self.name = f"{self.customer}-{self.month}-{self.year}-{number_of_customer + 1}"

	def validate(self):
		"""
		Validates the document before saving.
		- Ensures that an ROI Calculation does not already exist for the same customer, 
			month, and year to prevent duplicate records.
		"""
		self.validate_unique()


	def validate_unique(self):
		"""
		Checks for an existing ROI Calculation document for the same customer, month, and year.
		- If found, raises an error to prevent duplicate entries.
		"""
		if self.is_new() and frappe.db.exists(
			"ROI Calculation", {"month": self.month, "year": self.year, "customer": self.customer}
		):
			frappe.throw(
				f"ROI document for the month of {self.month} of {self.year} already exists. "
				"Kindly update that document if changes are required."
			)