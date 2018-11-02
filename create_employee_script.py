import requests
import csv

from common import superuser_login, get_employee_types, get_employee_status
from config import config


def main():
    city = config.CITY_NAME

    sheets = config.BASE_PPATH / "employees"
    sheet_name = sheets / (city.lower() + ".csv")
    tenant_id = "pb." + city.lower()

    # For UAT
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

            is_primary = True
            for department in row[6].split("|"):
                details.append(
                    {"fromDate": row[4], "toDate": row[5], "department": department.strip(), "designation": row[7],
                     "position": row[12],
                     "isPrimary": is_primary, "hod": []})
                is_primary = False

            post_data = {
                "RequestInfo": {"apiId": "org.egov.pgr", "ver": "1.0", "ts": "24-04-2016 12:12:12", "action": "asd",
                                "did": "4354648646", "key": "xyz", "msgId": None, "authToken": auth_token},
                "Employee": {"code": row[8], "dateOfAppointment": row[4], "employeeStatus": employed_employee_status_code, "employeeType": permanent_employee_type_code,
                             "assignments": details, "jurisdictions": ["100"], "physicallyDisabled": False,
                             "transferredEmployee": False, "medicalRep  ortProduced": True, "languagesKnown": [],
                             "maritalStatus": "MARRIED", "ifscCode": "ffwe", "documents": [], "serviceHistory": [],
                             "probation": [], "regularisation": [], "technical": [], "education": [], "test": [],
                             "user": {"roles": [{"code": row[10], "name": row[11], "tenantId": tenant_id}],
                                      "userName": row[8], "name": row[0], "gender": row[1], "mobileNumber": row[2],
                                      "emailId": "", "permanentAddress": city, "permanentCity": "Punjab",
                                      "permanentPinCode": "24324", "correspondenceCity": city,
                                      "correspondencePinCode": "34353", "correspondenceAddress": tenant_id,
                                      "active": True, "dob": row[3], "locale": None, "signature": "fghdfgewfg374823",
                                      "type": "EMPLOYEE", "password": row[9], "tenantId": tenant_id},
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
