import requests
import csv
from pathlib import Path
from common import superuser_login
from config import config

city = "Nawanshahr"

sheets = Path("employees")
sheet_name = sheets / (city.lower() + ".csv")
tenant_id = "pb." + city.lower()


# For UAT
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

        is_primary = True
        for department in row[6].split("|"):
            details.append({"fromDate": row[4], "toDate": row[5], "department": department.strip(), "designation": row[7], "position": row[12],
             "isPrimary": is_primary, "hod": []})
            is_primary = False

        post_data = {"RequestInfo":{"apiId":"org.egov.pgr","ver":"1.0","ts":"24-04-2016 12:12:12","action":"asd","did":"4354648646","key":"xyz","msgId":None,"authToken":auth_token},"Employee":{"code":row[8],"dateOfAppointment":row[4],"employeeStatus":"7","employeeType":"1","assignments":details,"jurisdictions":["100"],"physicallyDisabled":False,"transferredEmployee":False,"medicalReportProduced":True,"languagesKnown":[],"maritalStatus":"MARRIED","ifscCode":"ffwe","documents":[],"serviceHistory":[],"probation":[],"regularisation":[],"technical":[],"education":[],"test":[],"user":{"roles":[{"code":row[10],"name":row[11],"tenantId":tenant_id}],"userName":row[8],"name":row[0],"gender":row[1],"mobileNumber":row[2],"emailId":"","permanentAddress":city,"permanentCity":"Punjab","permanentPinCode":"24324","correspondenceCity":city,"correspondencePinCode":"34353","correspondenceAddress":tenant_id,"active":True,"dob":row[3],"locale":None,"signature":"fghdfgewfg374823","type":"EMPLOYEE","password":row[9],"tenantId":tenant_id},"tenantId": tenant_id}}
        post_response = requests.post(url=config.HOST + '/hr-employee-v2/employees/_create', headers=headers, json=post_data)
        print("==================================================")
        print(post_data)
        print("--------")
        print(post_response.json())
        print("==================================================")
        print("\n\n")

