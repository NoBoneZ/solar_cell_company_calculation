# Solar Cell Company

## Description
This is a Frappe-based application designed to calculate power consumption and determine the Return on Investment (ROI) for clients switching to solar energy. The system processes power consumption records collected per hour (KWH) and every 15 minutes (KW) to compute key metrics that help in financial decision-making.

### Features
- **Average Consumption Calculation:** Computes the average KW and KWH for all records or within a specified date range.
- **Tariff-Based Pricing:** Calculates low and high tariffs based on specific time periods:
  - **Low Tariff Period:** 11:00 PM - 5:59 AM (charged at 10% of average KWH)
  - **High Tariff Period:** 6:00 AM - 10:59 PM (charged at 30% of average KWH)
  
- **Customer-Specific ROI Entries:**
  - Entries can be created for each customer at any time.
  - Sales teams can create and edit entries.
  - Accounting teams have read-only access.
- **Data Management:** Ensures all relevant fields from imported datasets (e.g., Excel files) are included in the calculations.
- **Role-Based Access Control:** Restricts access based on user roles.

## Installation
To install and set up this app, follow these steps:

### 1. Set Up Frappe Bench
If you don’t have Frappe installed, follow these steps:

#### Install Prerequisites
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install python3-dev python3-pip python3-venv redis-server curl -y
sudo apt install mariadb-server mariadb-client -y
sudo apt install libmysqlclient-dev -y
```

#### Install Node.js and Yarn
```sh
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs
sudo npm install -g yarn
```

#### Install Frappe Bench
```sh
pip install frappe-bench
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
```

### 2. Create and Start a New Site
```sh
bench new-site solar.local
bench use solar.local
```

### 3. Install the App
Get the app and install it on your Frappe instance:
```sh

bench get-app https://github.com/NoBoneZ/solar_cell_company_calculation
bench install-app test_abraham
```

### 4. Start the Frappe Server
```sh
bench start
```
Now you can access the app via your browser at `http://localhost:8000`.

## Additional Resources
For more details on Frappe installation and configuration, visit the official Frappe documentation:
[https://frappeframework.com/docs](https://frappeframework.com/docs)

## License
MIT

