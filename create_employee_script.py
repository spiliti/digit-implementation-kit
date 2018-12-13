import requests
import csv

from common import superuser_login, get_employee_types, get_employee_status
from config import config



def get_employees_by_id(auth_token, username, tenantid):
    data = requests.post(url=config.HOST + '/user/_search',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "userName": username,
                             "tenantId": tenantid
                         })

    return data.json()["user"]


def get_employees_by_phone(auth_token, phone, tenantid):
    data = requests.post(url=config.HOST + '/user/_search',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "mobileNumber": phone,
                             "tenantId": tenantid
                         })

    return data.json()["user"]


def add_role_to_user(auth_token, username, tenant_id, add_roles):
    user = get_employees_by_id(auth_token, username, tenant_id)

    for role in add_roles:
        user[0]["roles"].append ({
            "code": role,
            "name": config.ROLE_CODE_MAP[role]
        })

    user[0]['dob'] = None

    data = requests.post(url=config.HOST + '/user/users/_updatenovalidate',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "user": user[0],
                         })

    return data.json()["user"]


def main():
    city = config.CITY_NAME

    sheets = config.BASE_PPATH / "employees"
    sheet_name = sheets / (city.lower() + ".csv")
    tenant_id = "pb." + city.lower()

    auth_token = superuser_login()["access_token"]
    start_row = 1

    employee_type_list = get_employee_types(tenant_id, auth_token)

    permanent_employee_type_code = None
    for etype in employee_type_list:
        if etype["name"] == "Permanent":
            permanent_employee_type_code = etype["id"]
            break

    employee_status_list = get_employee_status(tenant_id, auth_token)

    employed_employee_status_code = None

    for estatus in employee_status_list:
        if estatus["code"] == "EMPLOYED":
            employed_employee_status_code = estatus["id"]
            break

    if permanent_employee_type_code is None:
        raise Exception("There is no code for Permanent Employee Type")

    if employed_employee_status_code is None:
        raise Exception("There is no Code for Employed Employee Status")

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

                if existing_employees != mobile_number:
                    print(
                        "The employee {} already exist with mobile number {}. You have specified a different mobile number {}".format(
                            username, existing_mobilenumber, mobile_number))

                print("Employee", username, tenant_id, name, mobile_number, "already exists - ",
                      len(existing_employees))

                if roles_needed.issubset(roles_currently):
                    print ("The employee already has all required roles. Nothing needed")
                else:
                    print ("Adding required roles to user - {}".format(username))
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
                    username_update = input("Which user would you like to update with " + role_codes + " [Use n for skip]? ")
                else:
                    username_update = input(
                        "Will you like to add the " + role_codes + " to user {} [Yn]? ".format(existing_employees[0]["userName"]))
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
                        print ("Cannot find employee with username - " + username_update)
                    else:
                        roles_currently = set(map(lambda role: role['code'], employee_found[0]['roles']))
                        add_role_to_user(auth_token, username_update, tenant_id, roles_needed - roles_currently)
                continue

            for department in departments.split("|"):
                details.append(
                    {"fromDate": row[4], "toDate": row[5], "department": department.strip(), "designation": designation,
                     "position": row[12],
                     "isPrimary": is_primary, "hod": []})
                is_primary = False

            for role, role_name in zip(role_codes.split("|"), role_names.split("|")):
                roles.append({"code": role, "name": role_name, "tenantId": tenant_id})

            post_data = {
                "RequestInfo": {"authToken": auth_token},
                "Employee": {"code": username, "dateOfAppointment": row[4],
                             "employeeStatus": employed_employee_status_code, "employeeType":
                                 permanent_employee_type_code,
                             "assignments": details, "jurisdictions": ["100"], "physicallyDisabled": False,
                             "transferredEmployee": False, "medicalRep  ortProduced": True, "languagesKnown": [],
                             "maritalStatus": "MARRIED", "ifscCode": "ffwe", "documents": [], "serviceHistory": [],
                             "probation": [], "regularisation": [], "technical": [], "education": [], "test": [],
                             "user": {"roles": roles,
                                      "userName": username, "name": row[0], "gender": row[1],
                                      "mobileNumber": mobile_number,
                                      "emailId": "", "permanentAddress": city, "permanentCity": "Punjab",
                                      "permanentPinCode": "", "correspondenceCity": city,
                                      "correspondencePinCode": "", "correspondenceAddress": tenant_id,
                                      "active": True, "dob": row[3], "locale": None, "signature": "",
                                      "type": "EMPLOYEE", "password": password, "tenantId": tenant_id},
                             "tenantId": tenant_id}}
            post_response = requests.post(url=config.HOST + '/hr-employee-v2/employees/_create', headers=headers,
                                          json=post_data)
            print("==================================================")
            print(post_data)
            print("--------")
            print(post_response.json())
            print("==================================================")
            print("\n\n")


if __name__ == "__main__":
    main()
