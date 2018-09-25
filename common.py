import json
import uuid

import numpy
import pandas as pd
import re
import requests
from config import config


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


def create_boundary(config_function, boundary_type):
    # load_admin_boundary_config()
    current_boundary_type = boundary_type
    config_function()
    dfs = open_excel_file(config.SHEET)

    wards = get_sheet(dfs, config.SHEET_WARDS)
    zones = get_sheet(dfs, config.SHEET_ZONES)
    locality = get_sheet(dfs, config.SHEET_LOCALITY)

    offset = 1

    index_code = get_column_index(wards, config.COLUMN_WARD_CODE)
    index_name = get_column_index(wards, config.COLUMN_WARD_NAME)
    index_zone_name = get_column_index(wards, config.COLUMN_WARD_ADMIN_ZONE_NAME)

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

    index_code = get_column_index(zones, config.COLUMN_ZONE_CODE)
    index_name = get_column_index(zones, config.COLUMN_ZONE_NAME)

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

    index_code = get_column_index(locality, config.COLUMN_LOCALITY_CODE)
    index_name = get_column_index(locality, config.COLUMN_LOCALITY_NAME)
    index_admin_block = get_column_index(locality, config.COLUMN_LOCALITY_ADMIN_BLOCK)
    if current_boundary_type == "REVENUE":
        index_area = get_column_index(locality, config.COLUMN_LOCALITY_AREA)

    locality_data = locality.apply(lambda row: {
        "id": str(uuid.uuid4()),
        "boundaryNum": 1,
        "name": row[index_name].strip() + " - " + ward_to_code_map[row[index_admin_block].strip()],
        "localname": row[index_name].strip() + " - " + ward_to_code_map[row[index_admin_block].strip()],
        "longitude": None,
        "latitude": None,
        "label": "Locality",
        "code": row[index_code].strip(),
        "ward": row[index_admin_block].strip(),
        "area": "" if current_boundary_type == "ADMIN" else row[index_area].strip().upper().replace(" ", "").replace(
            "-", ""),
        "children": []
    }, axis=1)

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
        else:
            # the file doesn't exists already, so we can safely generate current boundary
            print("Boundary didn't exist. Creating one")
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
