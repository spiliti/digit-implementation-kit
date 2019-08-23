import json
import uuid
from urllib.parse import urljoin

import numpy
import pandas as pd
import re
import requests

from config import config


def get_employee_types(tenantid, auth_token):
    headers = {'Content-Type': 'application/json'}

    post_data = {"RequestInfo": {"authToken": auth_token}}
    post_response = requests.post(url=config.HOST + '/hr-masters-v2/employeetypes/_search?tenantId=' + tenantid,
                                  headers=headers,
                                  json=post_data)
    return post_response.json()['EmployeeType']


def get_employee_status(tenantid, auth_token):
    headers = {'Content-Type': 'application/json'}
    post_data = {"RequestInfo": {"authToken": auth_token}}
    post_response = requests.post(url=config.HOST + '/hr-masters-v2/hrstatuses/_search?tenantId=' + tenantid,
                                  headers=headers,
                                  json=post_data)
    return post_response.json()['HRStatus']


def open_excel_file(path):
    xl_file = pd.ExcelFile(path)

    dfs = {sheet_name: xl_file.parse(sheet_name)
           for sheet_name in xl_file.sheet_names}

    return dfs


def clean_name(name):
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def get_sheet(dfs, sheet_name):
    if sheet_name in dfs:
        return dfs[sheet_name]
    else:
        new_sheet_name = clean_name(sheet_name)
        for key in dfs.keys():
            key_name = clean_name(key)

            if key_name == new_sheet_name:
                return dfs[key]

        # we have not found any sheet matching full name, lets check starts with
        for key in dfs.keys():
            key_name = clean_name(key)

            if key_name.startswith(new_sheet_name):
                return dfs[key]


def get_column_index(df, column_name):
    new_column_name = clean_name(column_name)
    for i, name in enumerate(df.columns.values.tolist()):
        new_name = clean_name(name)
        if new_name.startswith(new_column_name):
            return i


def superuser_login():
    return login_egov(config.SUPERUSER.username, config.SUPERUSER.password, config.SUPERUSER.tenant_id, "EMPLOYEE")


def login_egov(username, password, tenant_id, user_type="EMPLOYEE"):
    resp = requests.post(config.URL_LOGIN, data={
        "username": username,
        "password": password,
        "grant_type": "password",
        "scope": "read",
        "tenantId": tenant_id,
        "userType": user_type
    }, headers={
        "Authorization": "Basic ZWdvdi11c2VyLWNsaWVudDplZ292LXVzZXItc2VjcmV0"
    })

    assert resp.status_code == 200, "Login should respond with 200: " + json.dumps(resp.json(), indent=2)
    return resp.json()


def open_google_spreadsheet(link_or_id_or_path: str, sheet_name: str = None):
    import os
    if os.path.isfile(link_or_id_or_path):
        return open_excel_file(link_or_id_or_path)

    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(config.GOOGLE_AUTH_CONFIG, scope)

    gc = gspread.authorize(credentials)

    if link_or_id_or_path.startswith("http"):
        wks = gc.open_by_url(link_or_id_or_path)
    else:
        wks = gc.open_by_key(link_or_id_or_path)

    dfs = {}

    for wk in wks.worksheets():
        if sheet_name is None:
            dfs[wk.title] = pd.DataFrame(wk.get_all_records())
        elif clean_name(sheet_name) == clean_name(wk.title):
            dfs[wk.title] = pd.DataFrame(wk.get_all_records())

    return dfs, wks


def get_slab_template():
    return {
        "RequestInfo": {
            "authToken": ""
        },
        "BillingSlab": [
            {
                "tenantId": "",
                "propertyType": "",
                "propertySubType": "",
                "usageCategoryMajor": "",
                "usageCategoryMinor": "",
                "usageCategorySubMinor": "",
                "usageCategoryDetail": "",
                "ownerShipCategory": "",
                "subOwnerShipCategory": "",
                "areaType": "",
                "fromPlotSize": -100,
                "toPlotSize": -100,
                "occupancyType": "",
                "fromFloor": -100,
                "toFloor": -100,
                "unitRate": -100,
                "isPropertyMultiFloored": False,
                "unBuiltUnitRate": -100,
                "arvPercent": -100
            }
        ]
    }


def validate_boundary_data(auth_token, boundary_data, boundary_type, duplicate_check=True,
                           used_boundary_codes_check=True):
    tenant_boundary = {}
    errors = []

    for tenantboundary in boundary_data["TenantBoundary"]:
        if tenantboundary["hierarchyType"]["code"] == boundary_type:
            tenant_boundary = tenantboundary["boundary"]
            break

    if not tenant_boundary:
        return errors

    locality_code_map = {}
    locality_name_map = {}

    for zone in tenant_boundary["children"]:
        for wardOrBlock in zone["children"]:
            for locality in wardOrBlock["children"]:
                locality_code_map[locality["code"]] = locality_code_map.get(locality["code"], 0) + 1
                locality_name_map[locality["name"]] = locality_name_map.get(locality["name"], []) + [
                    locality["code"]] + [zone["name"]] + [wardOrBlock["name"]]

    if used_boundary_codes_check:
        localities_in_use = get_used_localities(auth_token, boundary_data, boundary_type)
        missing_boundary_codes = list(set(localities_in_use) - set(locality_code_map.keys()))
        for locality in missing_boundary_codes:
            errors.append(
                "\nBoundary code \"{}\" is used by existing properties and not present in current boundary".format(
                    locality))

    if duplicate_check:
        for locality_code, count in locality_code_map.items():
            if count > 1:
                errors.append("\nDuplicate Locality Code \"{}\" Repeated for \"{}\" times".format(locality_code, count))

        for locality_name, zone_n_block in locality_name_map.items():
            if len(zone_n_block) > 3:
                # As we are adding locality code, zone name, ward name locality name against locality name
                # So, each locality name contains atleast 3 data in the list.
                # If size of list is more that 3 then locality name is repeated for multiple times
                errors.append(
                    "\nDuplicate Locality Name: \"{}\" Zone : \"{}\" Ward/Block : \"{}\"".format(locality_name,
                                                                                                 zone_n_block[1],
                                                                                                 zone_n_block[2]))
                # errors.append("Name : {}".format(locality_name))
                # errors.append("Zone : {}".format(zone_n_block[1]))
                # errors.append("Ward/Block : {}".format(zone_n_block[2]))

                # Getting all the locality code from "zone_n_block" list
                same_name_locality_code = [zone_n_block[i] for i in range(0, len(zone_n_block)) if i % 3 == 0]
                errors.append("\nRepetition : \"{}\" locality code: \"{}\" ".format(len(same_name_locality_code),
                                                                                    same_name_locality_code))
                for loc_code in same_name_locality_code:
                    if loc_code in localities_in_use:
                        errors.append("\t\t{} : {}".format(loc_code, "USED"))
                    else:
                        errors.append("\t\t{} : {}".format(loc_code, "NOT USED"))

    return errors


def get_used_localities(auth_token, boundary_data, boundary_type):
    if boundary_type == "REVENUE":
        URL = config.URL_SEARCH_LOCALITIES_USED_IN_REVENUE
    elif boundary_type == "ADMIN":
        URL = config.URL_SEARCH_LOCALITIES_USED_IN_ADMIN

    tenant_id = boundary_data["tenantId"]

    resp = requests.post(URL, data=json.dumps({
        "RequestInfo": {
            "authToken": auth_token
        },
        "searchCriteria": {
            "tenantId": tenant_id
        }
    }), headers={'Content-Type': 'application/json'})

    localities_used = resp.json()["services"]
    localities_in_use = []
    for locality in localities_used:
        localities_in_use.append(locality["locality"])

    return localities_in_use


def create_boundary(config_function, boundary_type):
    # load_admin_boundary_config()
    current_boundary_type = boundary_type
    config_function()
    dfs = open_excel_file(config.SHEET)

    wards = get_sheet(dfs, config.SHEET_WARDS)
    zones = get_sheet(dfs, config.SHEET_ZONES)
    locality = get_sheet(dfs, config.SHEET_LOCALITY)

    offset = 1

    index_code = get_column_index(wards, config.COLUMN_WARD_CODE) or 1
    index_name = get_column_index(wards, config.COLUMN_WARD_NAME) or 2
    index_zone_name = get_column_index(wards, config.COLUMN_WARD_ADMIN_ZONE_NAME) or 3

    ward_to_code_map = {}
    for _, row in wards.iterrows():
        ward_to_code_map[row[index_code].strip()] = row[index_name].strip()
        ward_to_code_map[row[index_name].strip()] = row[index_code].strip()

    wards_data = wards.apply(lambda row: {"id": str(uuid.uuid4()),
                                          "boundaryNum": 1,
                                          "name": row[index_name].strip(),
                                          "localname": row[index_name].strip(),
                                          "longitude": None,
                                          "latitude": None,
                                          "label": "Block",
                                          "code": row[index_code].strip(),
                                          "zone": row[index_zone_name].strip(),
                                          "children": []}
                             , axis=1)

    index_code = get_column_index(zones, config.COLUMN_ZONE_CODE) or 1
    index_name = get_column_index(zones, config.COLUMN_ZONE_NAME) or 2

    zone_to_code_map = {}
    for _, row in zones.iterrows():
        zone_to_code_map[row[index_code].strip()] = row[index_name].strip()
        zone_to_code_map[row[index_name].strip()] = row[index_code].strip()

    zones_data = zones.apply(lambda row: {"id": str(uuid.uuid4()),
                                          "boundaryNum": 1,
                                          "name": row[index_name].strip(),
                                          "localname": row[index_name].strip(),
                                          "longitude": None,
                                          "latitude": None,
                                          "label": "Zone",
                                          "code": row[index_code].strip(),
                                          "children": []}
                             , axis=1)

    index_code = get_column_index(locality, config.COLUMN_LOCALITY_CODE) or 1
    index_name = get_column_index(locality, config.COLUMN_LOCALITY_NAME) or 2
    index_admin_block = get_column_index(locality, config.COLUMN_LOCALITY_ADMIN_BLOCK) or 3
    if current_boundary_type == "REVENUE":
        index_area = get_column_index(locality, config.COLUMN_LOCALITY_AREA) or 4

    def process_locality(row):
        area = "" if current_boundary_type == "ADMIN" else row[index_area].strip().upper().replace(" ", "").replace(
            "-", "")
        area_code = area.replace("AREA", "A")

        if current_boundary_type == "REVENUE" and area not in ("AREA1", "AREA2", "AREA3"):
            raise InvalidArgumentException("Area type is not valid - " + area)

        if area_code:
            area_code = " - " + area_code

        return {
            "id": str(uuid.uuid4()),
            "boundaryNum": 1,
            "name": row[index_name].strip() + " - " + ward_to_code_map[row[index_admin_block].strip()] + area_code,
            "localname": row[index_name].strip() + " - " + ward_to_code_map[row[index_admin_block].strip()] + area_code,
            "longitude": None,
            "latitude": None,
            "label": "Locality",
            "code": row[index_code].strip(),
            "ward": row[index_admin_block].strip(),
            "area": area,
            "children": []
        }

    locality_data = locality.apply(process_locality, axis=1)

    wards_list = wards_data.tolist()
    locality_list = locality_data.tolist()
    zones_list = zones_data.tolist()

    wards_map = {}

    for ward in wards_list:
        zone = ward.pop('zone')

        wards_map[zone] = wards_map.get(zone, [])
        wards_map[zone].append(ward)

        wards_map[zone_to_code_map[zone]] = wards_map[zone]

    locality_map = {}

    for loca in locality_list:
        ward = loca.pop('ward')
        locality_map[ward] = locality_map.get(ward, [])
        locality_map[ward].append(loca)

        locality_map[ward_to_code_map[ward]] = locality_map[ward]

    for ward in wards_list:
        code = ward['code']
        ward['children'] = locality_map.get(code, [])

    for zone in zones_list:
        name = zone['name']
        zone['children'] = wards_map[name]

    import json
    # current_boundary_type = "ADMIN"

    new_boundary_data = {
        "hierarchyType": {
            "code": current_boundary_type,
            "name": current_boundary_type
        },
        "boundary": {
            "id": 1,
            "boundaryNum": 1,
            "name": config.CITY_NAME,
            "localname": config.CITY_NAME,
            "longitude": None,
            "latitude": None,
            "label": "City",
            "code": config.TENANT_ID,
            "children": zones_list
        }
    }

    final_data = {
        "tenantId": config.TENANT_ID,
        "moduleName": "egov-location",
        "TenantBoundary": [
            new_boundary_data
        ]
    }

    data = json.dumps(final_data, indent=2)

    print(data)

    auth_token = superuser_login()["access_token"]
    errors = validate_boundary_data(auth_token, final_data, boundary_type, config.BOUNDARY_DUPLICATE_CHECK,
                                    config.BOUNDARY_USED_CHECK)
    if len(errors) > 0:
        for error in errors:
            print(error)
        return

    import os
    response = os.getenv("ASSUME_YES", None) or input("Do you want to append the data in repo (y/[n])?")

    if response.lower() == "y":

        boundary_path = config.MDMS_LOCATION / config.CITY_NAME.lower() / "egov-location"
        os.makedirs(boundary_path, exist_ok=True)

        if os.path.isfile(boundary_path / "boundary-data.json"):
            with open(boundary_path / "boundary-data.json") as f:
                existing_boundary_data = json.load(f)

            if len(existing_boundary_data["TenantBoundary"]) == 0:
                # should never happen but just in case
                existing_boundary_data["TenantBoundary"].append(new_boundary_data)
                print("Boundary added")
            elif len(existing_boundary_data["TenantBoundary"]) == 1:
                if existing_boundary_data["TenantBoundary"][0]["hierarchyType"]["code"] == current_boundary_type:
                    existing_boundary_data["TenantBoundary"][0] = new_boundary_data
                    print("Boundary already exists. Overwriting")
                else:
                    existing_boundary_data["TenantBoundary"].append(new_boundary_data)
                    print("Boundary file exists. Adding new data")
            elif len(existing_boundary_data["TenantBoundary"]) == 2:
                if existing_boundary_data["TenantBoundary"][0]["hierarchyType"]["code"] == current_boundary_type:
                    existing_boundary_data["TenantBoundary"][0] = new_boundary_data
                else:
                    existing_boundary_data["TenantBoundary"][1] = new_boundary_data
                print("Boundary already exists. Overwriting")
                print("File Path : ", boundary_path, "boundary-data.json")

        else:
            # the file doesn't exists already, so we can safely generate current boundary
            print("Boundary didn't exist. Creating one")
            print("File Path : ", boundary_path + "boundary-data.json")
            existing_boundary_data = final_data

        with open(boundary_path / "boundary-data.json", "w") as f:
            json.dump(existing_boundary_data, f, indent=2)


def fix_value(val, default_str="", default_nan=None):
    if val is None:
        return default_str

    if type(val) is str and "°" in val:
        return val.split("°")[0]

    if type(val) is str:
        return val.strip()
    elif numpy.isnan(val):
        return default_nan
    else:
        return str(val)


def get_employees(auth_token, **kwargs):
    data = requests.post(url=config.HOST + '/user/_search',
                         json={
                             **{
                                 "RequestInfo": {
                                     "authToken": auth_token
                                 }
                             }, **kwargs,
                         })
    # print(data.json())
    return data.json()["user"]


def get_employees_by_id(auth_token, username, tenantid):
    # data = requests.post(url=config.HOST + '/user/_search',
    #                      json={
    #                          "RequestInfo": {
    #                              "authToken": auth_token
    #                          },
    #                          "userName": username,
    #                          "tenantId": tenantid
    #                      })
    #
    # return data.json()["user"]
    return get_employees(auth_token, userName=username, tenantId=tenantid)


def get_employees_by_phone(auth_token, phone, tenantid):
    # data = requests.post(url=config.HOST + '/user/_search',
    #                      json={
    #                          "RequestInfo": {
    #                              "authToken": auth_token
    #                          },
    #                          "mobileNumber": phone,
    #                          "tenantId": tenantid
    #                      })
    #
    # return data.json()["user"]
    return get_employees(auth_token, mobileNumber=phone, tenantId=tenantid)


def add_role_to_user(auth_token, username, tenant_id, add_roles, change_roles={}, remove_previous_roles=False):
    user = get_employees_by_id(auth_token, username, tenant_id)

    if remove_previous_roles:
        user[0]["roles"] = []

    if change_roles:
        changed = False
        for role in user[0]["roles"]:
            if role["code"] in change_roles:
                role["code"] = change_roles[role["code"]]
                changed = True

        if not changed:
            return

    for role in add_roles:
        user[0]["roles"].append({
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


def update_user_password(auth_token, tenant_id, username, password):
    user = get_employees_by_id(auth_token, username, tenant_id)

    user[0]['dob'] = None
    user[0]['password'] = password

    data = requests.post(url=config.HOST + '/user/users/_updatenovalidate',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "user": user[0],
                         })

    return data.json()["user"]


def update_user_activation(auth_token, tenant_id, username, activate=False):
    user = get_employees_by_id(auth_token, username, tenant_id)

    user[0]['dob'] = None
    user[0]['active'] = activate

    data = requests.post(url=config.HOST + '/user/users/_updatenovalidate',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "user": user[0],
                         })

    return data.json()["user"]


def search_property(auth_token, tenant_id, property_id):
    data = requests.post(url=config.HOST + '/pt-services-v2/property/_search',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             }
                         }, params={"ids": property_id, "tenantId": tenant_id})

    return data.json()


def update_property(auth_token, tenant_id, property):
    data = requests.post(url=config.HOST + '/pt-services-v2/property/_update',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "Properties": property
                         }, params={"tenantId": tenant_id})

    return data.json()


def search_demand(auth_token, tenantId=None, consumerCode=None, businessService=None):
    args = {}

    if tenantId:
        args["tenantId"] = tenantId

    if consumerCode:
        args["consumerCode"] = consumerCode

    if businessService:
        args["businessCode"] = businessService

    data = requests.post(url=config.HOST + '/billing-service/demand/_search',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             }
                         }, params=args)

    return data.json()


def update_demand(auth_token, demands):
    data = requests.post(url=config.HOST + '/billing-service/demand/_update',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "Demands": demands
                         })

    return data.json()


def generate_bill(auth_token, tenant_id, demand_id, consumer_code, business_service):
    data = requests.post(url=config.HOST + '/billing-service/bill/_generate',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "GenerateBillCriteria": [

                             ]
                         }, params={
            "tenantId": tenant_id,
            "demandId": demand_id,
            "consumerCode": consumer_code,
            "businessService": business_service,
        })

    return data.json()


def create_receipt(auth_token, tenant_id, receipt):
    data = requests.post(url=config.HOST + '/collection-services/receipts/_create',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "Receipt": receipt
                         }, params={"tenantId": tenant_id})

    return data.json()


def search_receipt(auth_token, receiptNumbers=None, tenantId=None, consumerCode=None, businessCode=None, status=None):
    args = {}

    if status:
        args["status"] = status

    if receiptNumbers:
        args["receiptNumbers"] = receiptNumbers

    if tenantId:
        args["tenantId"] = tenantId

    if consumerCode:
        args["consumerCode"] = consumerCode

    if businessCode:
        args["businessCode"] = businessCode

    data = requests.post(url=config.HOST + '/collection-services/receipts/_search',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             }
                         }, params=args)

    return data.json()


def cancel_receipt(auth_token, receipt_number, consumer_code, message):
    data = requests.post(url=config.HOST + '/collection-services/receipts/_workflow',
                         json={
                             "RequestInfo": {
                                 "authToken": auth_token
                             },
                             "ReceiptWorkflow": [
                                 {
                                     "consumerCode": consumer_code,
                                     "receiptNumber": receipt_number,
                                     "action": "CANCEL",
                                     "reason": message
                                 }
                             ]
                         })

    return data.json()


def upsert_localization(auth_token, body):
    body["RequestInfo"]["authToken"] = auth_token
    data = requests.post(url=config.HOST + '/localization/messages/v1/_upsert', json=body)
    return data.json()


def mdms_call(auth_token, module_name, master_details):
    url = urljoin(config.HOST, '/egov-mdms-service/v1/_search')
    request_body = {}
    request_body["RequestInfo"] = {"authToken": auth_token}
    request_body["MdmsCriteria"] = {"tenantId": "pb", "moduleDetails": [
        {"moduleName": module_name, "masterDetails": [{"name": master_details}]}]}
    parms = {"tenantId": "pb"}
    return requests.post(url, params=parms, json=request_body).json()


def search_localization(auth_token, module_name, locale, tenant_id=config.TENANT_ID):
    url = urljoin(config.HOST, '/localization/messages/v1/_search')
    request_body = {}
    request_body["RequestInfo"] = {"authToken": auth_token}
    parms = {"tenantId": tenant_id, "module": module_name, "locale": locale}
    return requests.post(url, params=parms, json=request_body).json()


def search_tl_billing_slab(auth_token, tenant_id=config.TENANT_ID):
    url = urljoin(config.HOST, '/tl-calculator/billingslab/_search')
    request_body = {}
    request_body["RequestInfo"] = {"authToken": auth_token}
    parms = {"tenantId": tenant_id}
    return requests.post(url, params=parms, json=request_body).json()
