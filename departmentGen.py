import os

from common import *
from config import config

new_departments = None


def main():
    global new_departments
    new_departments = set()

    dfs = open_excel_file(config.SHEET)

    departments = get_sheet(dfs, config.SHEET_DEPARTMENTS)

    index_department = get_column_index(departments, config.COLUMN_DEPARTMENT)
    dep_map = {}

    def update_departments(row):
        global new_departments
        for dep_name in row[index_department].strip().split(","):
            clean_dep_name = clean_name(dep_name)
            new_departments.add(clean_dep_name)
            dep_map[clean_dep_name] = dep_name
            # new_departments.add(dep_name.strip())

    departments.apply(update_departments, axis=1)

    deps_existing = json.load(open(config.MDMS_DEPARTMENT_JSON))

    existing_departments = set()
    existing_departments.add(clean_name("Engineering Branch(Civil) - for Buildings and Roads"))
    dep_map[clean_name("Engineering Branch(Civil) - for Buildings and Roads")] = "Engineering Branch (Civil - B&R)"

    existing_departments.add(clean_name("Engineering Branch(O&M) -for Water and Sewerage"))
    dep_map[clean_name("Engineering Branch(O&M) -for Water and Sewerage")] = "Engineering Branch (O&M - W&S)"

    for dep in deps_existing["Department"]:
        clean_dep_name = clean_name(dep["name"])
        dep_map[clean_dep_name] = dep["name"]
        existing_departments.add(clean_dep_name)

    deps_to_add = new_departments - existing_departments
    len_existing_dep = len(existing_departments)


    deps = []

    for dep in deps_to_add:
        len_existing_dep += 1
        deps.append({"name": dep_map[dep], "code": "DEPT_" + str(len_existing_dep), "active": True})

    print(json.dumps(deps, indent=2))

    if len(deps) > 0:
        response = os.getenv("ASSUME_YES", None) or input("Do you want to append the data in repo (y/[n])?")

        if response.lower() == "y":
            deps_existing["Department"].extend(deps)

            with open(config.MDMS_DEPARTMENT_JSON, "w") as f:
                f.write(json.dumps(deps_existing, indent=2))
            print("Added the departments to MDMS data")
        else:
            print("Not adding the departments to MDMS data")


if __name__ == "__main__":
    main()
