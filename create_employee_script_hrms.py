import requests
import csv

from common import superuser_login, get_employee_types, get_employee_status, add_role_to_user, get_employees_by_phone, \
    get_employees_by_id
from config import config


def main():
    city = config.CITY_NAME

    sheets = config.BASE_PPATH / "employees"
    sheet_name = sheets / (city.lower() + ".csv")
    tenant_id = "pb." + city.lower()

    auth_token = superuser_login()["access_token"]
    start_row = 1

    with open(sheet_name) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        current_row = 0
        for row in readCSV:
            current_row += 1

            if current_row < start_row:
                continue

            headers = {'Content-Type': 'application/json'}

            details = []
            roles = []
            is_primary = True

            departments = row[6]
            role_codes = row[10]
            role_names = row[11]
            designation = row[7]
            password = row[9]
            username = row[8]
            mobile_number = row[2]
            name = row[0]

            existing_employees = get_employees_by_id(auth_token, username, tenant_id)

            roles_needed = set(map(str.strip, role_codes.split("|")))

            if existing_employees:
                # This employee already exists
                existing_mobilenumber = existing_employees[0]['mobileNumber']
                roles_currently = set(map(lambda role: role['code'], existing_employees[0]['roles']))
                ask_for_role_update = False

                if existing_mobilenumber != mobile_number:
                    print(
                        "The employee {} already exist with mobile number {}. You have specified a different mobile number {}".format(
                            username, existing_mobilenumber, mobile_number))
                    ask_for_role_update = True
                else:
                    print("Employee", username, tenant_id, name, mobile_number, "already exists - ",
                          len(existing_employees))

                if roles_needed.issubset(roles_currently):
                    print("The employee already has all required roles. Nothing needed")
                else:
                    if ask_for_role_update:
                        username_update = input(
                            "Would you like to add " + role_codes + " to " + username + "[Use n for skip]? ")
                        if username_update.lower() == "n":
                            print("Skipping adding required roles to user - {}".format(username))
                            continue
                    else:
                        print("Adding required roles to user - {}".format(username))
                    add_role_to_user(auth_token, username, tenant_id, roles_needed - roles_currently)
                continue

            existing_employees = get_employees_by_phone(auth_token, mobile_number, tenant_id)

            if existing_employees:
                info = map(lambda emp: "(username={}, mob={}, name={}, roles={}".format(
                    emp["userName"],
                    emp["mobileNumber"],
                    emp["name"],
                    "|".join(map(lambda role: role["code"], emp["roles"])))
                           , existing_employees)
                print("{} Employee(s) with mobile number {} already exists".format(len(existing_employees),
                                                                                   mobile_number), list(info))
                if len(existing_employees) > 1:
                    username_update = input(
                        "Which user would you like to update with " + role_codes + " [Use n for skip]? ")
                else:
                    username_update = input(
                        "Will you like to add the " + role_codes + " to user {} [Yn]? ".format(
                            existing_employees[0]["userName"]))
                    if username_update.strip().lower() == "n":
                        print("Skipping the user creation for {}".format(username))
                        continue
                    else:
                        username_update = existing_employees[0]["userName"]

                if username_update.strip().lower() == "n":
                    print("Skipping the user creation for {}".format(username))
                    continue
                else:
                    employee_found = list(filter(lambda emp: emp["userName"] == username_update, existing_employees))
                    if not employee_found:
                        print("Cannot find employee with username - " + username_update)
                    else:
                        roles_currently = set(map(lambda role: role['code'], employee_found[0]['roles']))
                        add_role_to_user(auth_token, username_update, tenant_id, roles_needed - roles_currently)
                continue

            for department in departments.split("|"):
                {
                    "fromDate": 0,
                    "toDate": None,
                    "department": department.strip(),
                    "isCurrentAssignment": True,
                    "designation": designation.strip(),
                    "reportingTo": "",
                    "isHod": True
                }
                is_primary = False

            for role, role_name in zip(role_codes.split("|"), role_names.split("|")):
                roles.append({"code": role, "name": role_name, "tenantId": tenant_id})

            post_data = {
                "RequestInfo": {
                    "authToken": "{{access_token}}"
                },
                "Employees": [
                    {
                        "user": {
                            "name": name,
                            "userName": username,
                            "fatherOrHusbandName": "F",
                            "mobileNumber": mobile_number,
                            "gender": "",
                            "dob": 0,
                            "roles": [
                            ],
                            "tenantId": tenant_id
                        },
                        "dateOfAppointment": 0,
                        "employeeType": "PERMANENT",
                        "employeeStatus": "EMPLOYED",
                        "jurisdictions": [
                            {
                                "hierarchy": "ADMIN",
                                "boundary": tenant_id,
                                "boundaryType": "City",
                                "tenantId": tenant_id
                            }
                        ],
                        "active": True,
                        "assignments": [

                        ],
                        "serviceHistory": [

                        ],
                        "education": [
                        ],
                        "tests": [
                        ],
                        "tenantId": tenant_id
                    }
                ]
            }
            post_response = requests.post(url=config.HOST + '/egov-hrms/employees/_create', headers=headers,
                                          json=post_data)
            print("==================================================")
            print(post_data)
            print("--------")
            print(post_response.json())
            print("==================================================")
            print("\n\n")


if __name__ == "__main__":
    main()
