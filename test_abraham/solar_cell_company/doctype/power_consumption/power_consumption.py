# Copyright (c) 2025, NoBoneZ and contributors
# For license information, please see license.txt
from calendar import monthrange
from datetime import datetime

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from test_abraham.base.constants import month_dict, TarriffChoices

class PowerConsumption(Document):
	"""
	Represents power consumption records for a customer. 
	This document is responsible for storing and processing power usage data.
	"""

	def autoname(self):
		"""
		Automatically generates a unique name for the Power Consumption document.
		Naming format: `customer-year-instance_count`
		
		- Counts existing power consumption records for the customer.
		- Extracts the year from the provided date.
		- Appends an incremental count to maintain uniqueness.
		"""
		customer_count = frappe.db.sql(
			"""
			SELECT COUNT(*) as customer_count 
			FROM `tabPower Consumption` 
			WHERE customer = %s
			""",
			(self.customer,),
			as_dict=True
		)[0].get("customer_count", 0)

		# Convert date string to datetime object if necessary
		date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S") if isinstance(self.date, str) else self.date

		# Assign a unique name
		self.name = f"{self.customer}-{date.year}-{customer_count + 1}"

	def validate(self):
		"""
		Validates the document before saving.
		Ensures that there are no duplicate power consumption records for the same customer and date.
		"""
		self.validate_unique()
		self.validate_future_dates()

	def validate_future_dates(self):
		if self.date > now_datetime:
			frappe.throw("Power consumption can not be recorded for future dates")

	def validate_unique(self):
		"""
		Checks for duplicate power consumption entries for the same customer and date.
		Prevents duplicate kWh values from being stored.
		"""
		if self.is_new() and frappe.db.exists(
			"Power Consumption", 
			{"date": self.date, "customer": self.customer, "kwh": self.kwh, "kwh__": self.kwh__}
		):
			frappe.throw("A record for this date with the same KWH and KW already exists.")


	def update_customer_consumption(self):
		"""
		Updates the average power consumption values for the associated customer.

		This function calculates the average power consumption (`kwh` and `kwh__`)
		for a given customer by querying the `Power Consumption` table. The computed
		values are then updated in the corresponding `Customer` document.

		Steps:
		1. Query the database to calculate the average `kwh` and `kwh__` values for the customer.
		2. Update the `average_kw` and `average_kwh` fields in the `Customer` doctype.

		Returns:
			None
		"""

		# SQL query to fetch the average power consumption values for the customer
		query_avg = """ 
			SELECT AVG(kwh) AS average_kw, AVG(kwh__) AS average_kwh 
			FROM `tabPower Consumption` 
			WHERE customer = %s
		"""

		# Execute the query and fetch the result
		result_avg = frappe.db.sql(query_avg, (self.customer,), as_dict=True)

		# Update the Customer document with the calculated average values
		frappe.db.set_value('Customer', self.customer, {
			'average_kw': result_avg[0]["average_kw"] if result_avg else 0,
			'average_kwh': result_avg[0]["average_kwh"] if result_avg else 0
		})


	def on_submit(self):
		"""
		Executes actions when the document is submitted.

		This function ensures that relevant computations and updates occur upon submission
		of a `Power Consumption` record.

		Actions performed:
		1. Determine the tariff type based on the time of consumption (`set_tarriff`).
		2. Compute and update the average monthly tariffs (`calculate_average_tariffs_for_month`).
		3. Update the customer's average power consumption data (`update_customer_consumption`).

		Returns:
			None
		"""

		# Set the tariff type for the record
		self.set_tarriff()

		# Calculate and update average tariffs for the customer's monthly consumption
		self.calculate_average_tariffs_for_month()

		# Update the customer's overall average power consumption
		self.update_customer_consumption()


	def set_tarriff(self):
		"""
		Determines the tariff category (LOW or HIGH) based on the consumption time.

		- "LOW" tariff applies between 11 PM and 6 AM.
		- "HIGH" tariff applies between 6 AM and 11 PM.
		"""
		formatted_date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S") if isinstance(self.date, str) else self.date
		self.tarriff = TarriffChoices.LOW if 23 <= formatted_date.hour or formatted_date.hour < 6 else TarriffChoices.HIGH

	def calculate_average_tariffs_for_month(self):
		"""
		Calculates and updates the average power consumption tariffs for a given month.

		**Process:**
		1. Fetch all power consumption records for the customer within the current month.
		2. Compute the overall average of `kwh` and `kwh__` values.
		3. Calculate tariff-specific averages for LOW and HIGH tariff time periods.
		4. Update or create an entry in the "ROI Calculation" document.

		Returns:
			None
		"""

		# Extract year and month from the date field
		formatted_date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S") if isinstance(self.date, str) else self.date
		year = formatted_date.year
		month = formatted_date.month
		last_day = monthrange(year, month)[1]  # Get the last day of the month

		start_date = f"{year}-{str(month).zfill(2)}-01"
		end_date = f"{year}-{str(month).zfill(2)}-{last_day}"

		# Fetch all power consumption records for the customer in the given month
		query_raw = """
			SELECT kwh, kwh__, date
			FROM `tabPower Consumption`
			WHERE customer = %s
			AND date BETWEEN %s AND %s
		"""
		current_records = frappe.db.sql(query_raw, (self.customer, start_date, end_date), as_dict=True)

		if not current_records:
			return None  # Exit if no records exist

		# Compute average kwh and kwh__
		query_avg = """
			SELECT AVG(kwh) as average_kw, AVG(kwh__) as average_kwh
			FROM `tabPower Consumption`
			WHERE customer = %s
			AND date BETWEEN %s AND %s
		"""
		avg_result = frappe.db.sql(query_avg, (self.customer, start_date, end_date), as_dict=True)
		average_kw = avg_result[0]["average_kw"] if avg_result else 0
		average_kwh = avg_result[0]["average_kwh"] if avg_result else 0

		# Compute average tariffs based on time periods
		query_tarriff = """
			SELECT 
				AVG(CASE WHEN tarriff = 'High' THEN kwh__ ELSE NULL END) AS average_kwh_high,
				AVG(CASE WHEN tarriff = 'Low' THEN kwh__ ELSE NULL END) AS average_kwh_low
			FROM `tabPower Consumption`
			WHERE customer = %s
			AND date BETWEEN %s AND %s
		"""
		tariff_result = frappe.db.sql(query_tarriff, (self.customer, start_date, end_date), as_dict=True)

		# Extract tariff values
		average_low = tariff_result[0]["average_kwh_low"] if tariff_result else 0
		average_high = tariff_result[0]["average_kwh_high"] if tariff_result else 0

		low_tariff = 0.1 * average_low if average_low else 0
		high_tariff = 0.3 * average_high if average_high else 0

		# Map numeric month to its string equivalent
		month_equivalent = month_dict.get(str(month), "").capitalize()

		# Check if an ROI Calculation already exists for this month & customer
		existing_roi = frappe.db.get_value(
			"ROI Calculation",
			{"customer": self.customer, "month": month_equivalent, "year": year},
			"name",
			as_dict=True
		)

		if existing_roi:
			# Update the existing ROI Calculation record
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
			
			roi_entry.submit()
			

		frappe.db.commit()
		return
	
	def on_thrash(self):
		self.recalculate_roi_after_deletion()

	
	def on_cancel(self):
		self.recalculate_roi_after_deletion()


	def recalculate_roi_after_deletion(self):
		"""
		Recalculates and updates the ROI Calculation entry for a customer 
		if a Power Consumption record is deleted.

		**Process:**
		1. Recalculate the average `kw` and `kwh` for the remaining records in that month.
		2. Recalculate the `low_tariff` and `high_tariff` values.
		3. Update the existing ROI Calculation if data remains.
		4. Delete the ROI Calculation if no records exist.

		Args:
			customer (str): The customer ID whose power consumption record was deleted.
			date (str or datetime): The date of the deleted record.

		Returns:
			None
		"""

		# Extract year and month from the date field
		formatted_date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S") if isinstance(self.date, str) else self.date
		year = formatted_date.year
		month = formatted_date.month
		last_day = monthrange(year, month)[1]

		start_date = f"{year}-{str(month).zfill(2)}-01"
		end_date = f"{year}-{str(month).zfill(2)}-{last_day}"

		# Fetch remaining power consumption records for the customer in that month
		query_count = """
			SELECT COUNT(*) as record_count
			FROM `tabPower Consumption`
			WHERE customer = %s AND date BETWEEN %s AND %s
		"""
		record_count = frappe.db.sql(query_count, (self.customer, start_date, end_date), as_dict=True)[0]["record_count"]

		if record_count == 0:
			# If no records remain, delete the ROI Calculation entry
			existing_roi = frappe.db.get_value(
				"ROI Calculation",
				{"customer": self.customer, "month": month_dict.get(str(month), "").capitalize(), "year": year},
				"name"
			)
			if existing_roi:
				frappe.delete_doc("ROI Calculation", existing_roi)
				frappe.db.commit()
			return

		# Compute new average kwh and kwh__
		query_avg = """
			SELECT AVG(kwh) as average_kw, AVG(kwh__) as average_kwh
			FROM `tabPower Consumption`
			WHERE customer = %s AND date BETWEEN %s AND %s
		"""
		avg_result = frappe.db.sql(query_avg, (self.customer, start_date, end_date), as_dict=True)
		average_kw = avg_result[0]["average_kw"] if avg_result else 0
		average_kwh = avg_result[0]["average_kwh"] if avg_result else 0

		# Compute new average tariffs
		query_tariff = """
			SELECT 
				AVG(CASE WHEN tarriff = 'High' THEN kwh__ ELSE NULL END) AS average_kwh_high,
				AVG(CASE WHEN tarriff = 'Low' THEN kwh__ ELSE NULL END) AS average_kwh_low
			FROM `tabPower Consumption`
			WHERE customer = %s AND date BETWEEN %s AND %s
		"""
		tariff_result = frappe.db.sql(query_tariff, (self.customer, start_date, end_date), as_dict=True)
		average_low = tariff_result[0]["average_kwh_low"] if tariff_result else 0
		average_high = tariff_result[0]["average_kwh_high"] if tariff_result else 0

		low_tariff = 0.1 * average_low if average_low else 0
		high_tariff = 0.3 * average_high if average_high else 0

		# Update the existing ROI Calculation record
		frappe.db.set_value(
			"ROI Calculation",
			{"customer": self.customer, "month": month_dict.get(str(month), "").capitalize(), "year": year},
			{
				"average_kw": average_kw,
				"average_kwh": average_kwh,
				"low_tariff": low_tariff,
				"high_tarriff": high_tariff,
			}
		)

		frappe.db.commit()
