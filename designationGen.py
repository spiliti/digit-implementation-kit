import json
from common import *
from config import *

dfs = open_excel_file(SHEET)

designations = get_sheet(dfs, SHEET_DESIGNATION)

index_designation = get_column_index(designations, COLUMN_DESIGNATION)

new_designations = set()

designations.apply(lambda row: new_designations.add(row[index_designation].strip()), axis=1)

dess_existing = json.load(open(MDMS_DESIGNATION_JSON))

existing_designations = set()


for des in dess_existing["Designation"]:
    existing_designations.add(des["name"])

dess_to_add = new_designations - existing_designations
len_existing_des = len(existing_designations)

dess = []

for des in dess_to_add:
    len_existing_des += 1
    dess.append({"name": des, "description": des, "code": "DESIG_" + str(len_existing_des), "active": True})

print(json.dumps(dess, indent=2))

response = input("Do you want to append the data in repo (y/[n])?")

if response.lower() == "y":
    dess_existing["Designation"].extend(dess)

    with open(MDMS_DESIGNATION_JSON, "w") as f:
        f.write(json.dumps(dess_existing, indent=2))

    print("Added the designations to MDMS data")
else:
    print("Not adding the designations to MDMS data")

