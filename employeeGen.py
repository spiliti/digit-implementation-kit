from math import isnan
from pathlib import Path

from common import *
from config import config

dfs = open_excel_file(config.SHEET)

designations = {}
for val in json.load(open(config.MDMS_DESIGNATION_JSON))["Designation"]:
    designations[clean_name(val["code"])] = val["name"]
    designations[clean_name(val["name"])] = val["code"]


departments = {}
for val in json.load(open(config.MDMS_DEPARTMENT_JSON))["Department"]:
    departments[clean_name(val["code"])] = val["name"]
    departments[clean_name(val["name"])] = val["code"]

employees = get_sheet(dfs, config.SHEET_EMPLOYEE)

# Employee Name	Gender	Mobile	DOB	Start Date	End Date	Department	Designation	Code	Password	Role Code	Role Name	Position
# Name*	Gender*	Mobile Number*	DOB	Appointed From Date*	Appointed To Date*	Department*	Designation*	Employee Code*	Mobile Number*
# Sh.Balbir Raj 	Male	9501149592	01/07/2000	01/01/2018	31/03/2020	Executive Branch	Commissioner Municipal Coorporations	HSPEC1	9501149592	PGR-ADMIN	PGR Administrator	1

indexes = {}

columns = ["Name", "Gender", "Mobile Number", "DOB", "Appointed From Date", "Appointed To Date", "Department", "Designation", "Employee Code", "Mobile Number", "PGR Role"]
for key in columns:
    indexes[key] = get_column_index(employees, key)

rows = []
count = 1

role_map = {
    "GRO": "GRO",
    "ADMIN": "PGR-ADMIN",
    "CSR": "CSR",
    "LME": "EMPLOYEE",
}

role_name_map = {
    "GRO": "Grievance Routing Officer",
    "ADMIN": "PGR Administrator",
    "CSR": "Citizen Service Representative",
    "LME": "Employee",
}

for _, row in employees.iterrows():
    row_data = []
    for col in columns:
        val = row[indexes[col]] or ""

        if type(val) in (int, float):
            if isnan(val):
                val = ""
            else:
                val = str(int(val))

        if type(val) is not str:
            val = str(val)

        val = val.strip()
        orig_val = val

        if col.lower() == "mobile number":
            val = val.replace("-", "").replace(" ","").replace("+91", "")
        elif col == "Employee Code":
            if not val or val == "nan" or val == "":
                val = "%03d" % count
        elif col == "Department":
            val = []
            for dep in orig_val.split(","):
                val.append(departments[clean_name(dep)])
            val = "|".join(val)
        elif col == "Designation":
            val = designations[clean_name(val)]
        elif col == "DOB":
            val = "01/07/2000"
        elif col == "Appointed From Date":
            val = "01/07/2018"
        elif col == "Appointed To Date":
            val = "01/07/2020"
        elif col == "PGR Role":
            val = role_map[orig_val.upper()]
        row_data.append(val)

        if col == "PGR Role":
            val = role_name_map[orig_val.upper()]
            row_data.append(val)
            row_data.append(str(count))
            count += 1

    rows.append(",".join(row_data))

with open(Path("employees/" + config.CITY_NAME.lower() + ".csv"), "w") as f:
    f.write("\n".join(rows))