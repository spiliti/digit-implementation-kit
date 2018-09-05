from common import *
from config import config

dfs = open_excel_file(config.SHEET)

departments = get_sheet(dfs, config.SHEET_DEPARTMENTS)

index_department = get_column_index(departments, config.COLUMN_DEPARTMENT)

new_departments = set()

def update_departments(row):
    global new_departments
    for dep_name in row[index_department].strip().split(","):
        new_departments.add(dep_name.strip())

departments.apply(update_departments , axis=1)

deps_existing = json.load(open(config.MDMS_DEPARTMENT_JSON))

existing_departments = set()


for dep in deps_existing["Department"]:
    existing_departments.add(dep["name"])

deps_to_add = new_departments - existing_departments
len_existing_dep = len(existing_departments)

deps = []

for dep in deps_to_add:
    len_existing_dep += 1
    deps.append({"name": dep, "code": "DEPT_" + str(len_existing_dep), "active": True})

print(json.dumps(deps, indent=2))

response = input("Do you want to append the data in repo (y/[n])?")

if response.lower() == "y":
    deps_existing["Department"].extend(deps)

    with open(config.MDMS_DEPARTMENT_JSON, "w") as f:
        f.write(json.dumps(deps_existing, indent=2))
    print("Added the departments to MDMS data")
else:
    print("Not adding the departments to MDMS data")
