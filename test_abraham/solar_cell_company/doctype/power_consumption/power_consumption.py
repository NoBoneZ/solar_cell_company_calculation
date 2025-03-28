# Copyright (c) 2025, NoBoneZ and contributors
# For license information, please see license.txt
from calendar import monthrange
from datetime import datetime

import frappe
from frappe.model.document import Document

from test_abraham.base.constants import month_dict, TarriffChoices

class PowerConsumption(Document):

	def autoname(self):
		customer_count = frappe.db.sql(
			"""SELECT COUNT(*) as customer_count FROM `tabPower Consumption` WHERE customer = %s""",
			(self.customer,),
			as_dict=True
		)[0].get("customer_count", 0)
		date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")
		self.name = f"{self.customer}-{date.year}-{customer_count + 1}"



	

	def on_submit(self):
		self.set_tarriff()
		self.calculate_average_tariffs_for_month()


	
	def set_tarriff(self):
		formatted_date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")
		self.tarriff = TarriffChoices.LOW if 23 <= formatted_date.hour or formatted_date.hour < 6 else TarriffChoices.HIGH



	def calculate_average_tariffs_for_month(self):
		"""
		Calculate average tariffs for a given month and update the ROI Calculation doctype.

		Steps:
		1. Fetch all power consumption records for the customer within the given month.
		2. Compute overall average `kwh` and `kwh__` values separately.
		3. Calculate low and high tariff values based on usage time.
		4. Update or create an entry in the "ROI Calculation" doctype.

		Returns:
			None
		"""

		# Get the year and month from the current date
		formatted_date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")
		year = formatted_date.year
		month = formatted_date.month
		last_day = monthrange(year, month)[1]  # Get the last day of the month

		start_date = f"{year}-{str(month).zfill(2)}-01"
		end_date = f"{year}-{str(month).zfill(2)}-{last_day}"

		# First Query: Fetch raw kwh data
		query_raw = """
			SELECT kwh, kwh__, date
			FROM `tabPower Consumption`
			WHERE customer = %s
			AND date BETWEEN %s AND %s
		"""
		current_records = frappe.db.sql(query_raw, (self.customer, start_date, end_date), as_dict=True)

		if not current_records:
			return None  # No records found, exit early

		# Second Query: Fetch average kwh values separately (for efficiency)
		query_avg = """
			SELECT AVG(kwh) as average_kw, AVG(kwh__) as average_kwh
			FROM `tabPower Consumption`
			WHERE customer = %s
			AND date BETWEEN %s AND %s
		"""
		
		avg_result = frappe.db.sql(query_avg, (self.customer, start_date, end_date), as_dict=True)
		average_kw = avg_result[0]["average_kw"] if avg_result else 0
		average_kwh = avg_result[0]["average_kwh"] if avg_result else 0


		query_tarriff = """
				SELECT 
					AVG(CASE WHEN tarriff= 'High' THEN kwh__ ELSE NULL END) AS average_kwh_high,
					AVG(CASE WHEN tarriff = 'Low' THEN kwh__ ELSE NULL END) AS average_kwh_low
				FROM `tabPower Consumption`
				WHERE customer = %s
				AND date BETWEEN %s AND %s
			"""
		tariff_result = frappe.db.sql(query_tarriff, (self.customer, start_date, end_date), as_dict=True)
		print(tariff_result, "\n"*20)



		# Categorizing low and high tariff records
		# low_tariff_records = []
		# high_tariff_records = []

		# for record in current_records:
		# 	record_date = record["date"]

		# 	if isinstance(record_date, str):  
		# 		record_date = datetime.strptime(record_date, "%Y-%m-%d %H:%M:%S")  # Ensure datetime format

		# 	low_tariff_records.append(record["kwh__"]) if 23 <= record_date.hour or record_date.hour < 6 else high_tariff_records.append(record["kwh__"])
				
		
		# Compute tariff values
		average_low = tariff_result[0]["average_kwh_low"] if tariff_result else 0
		average_high = tariff_result[0]["average_kwh_high"] if tariff_result else 0

		low_tariff = 0.1 * average_low if average_low else 0
		high_tariff = 0.3 * average_high if average_high else 0

		# Map month to its equivalent name
		month_equivalent = month_dict.get(str(month), "").capitalize()


		# Check if an ROI Calculation record already exists for the given customer, month, and year
		existing_roi = frappe.db.get_value(
			"ROI Calculation",
			{"customer": self.customer, "month": month_equivalent, "year": year},
			"name",
			as_dict=True
		)

		if existing_roi:
			# Update existing ROI Calculation record
			frappe.db.set_value("ROI Calculation", existing_roi["name"], {
				"average_kw": average_kw,
				"average_kwh": average_kwh,
				"low_tariff": low_tariff,
				"high_tarriff": high_tariff
			})
		else:
			# Create a new ROI Calculation record
			roi_entry = frappe.get_doc({
				"doctype": "ROI Calculation",
				"customer": self.customer,
				"month": month_equivalent,
				"year": year,
				"average_kw": average_kw,
				"average_kwh": average_kwh,
				"low_tariff": low_tariff,
				"high_tarriff": high_tariff,
			})
			roi_entry.insert()

		frappe.db.commit()
		return
