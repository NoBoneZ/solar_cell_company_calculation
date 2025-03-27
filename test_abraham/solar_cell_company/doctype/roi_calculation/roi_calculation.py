# Copyright (c) 2025, NoBoneZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ROICalculation(Document):
	

	def autoname(self):
		number_of_customer = frappe.db.sql(
			"""SELECT COUNT(*) as customer_count FROM `tabROI Calculation` WHERE customer = %s""",
			(self.customer,),
			as_dict=True
		)[0].get("customer_count", 0)

		self.name = f"{self.customer}--{self.month}--{self.year}-{number_of_customer + 1}"

