import uuid
from urllib.parse import urljoin

import requests

from common import open_excel_file, get_sheet, get_column_index, superuser_login, \
    validate_boundary_data
from config import load_new_revenue_boundary_config, config


def mdms_call_tenant(auth_token, tenant_id, module_name, master_details):
    url = urljoin(config.HOST, '/egov-mdms-service/v1/_search')
    request_body = {}
    request_body["RequestInfo"] = {"authToken": auth_token}
    request_body["MdmsCriteria"] = {"tenantId": tenant_id, "moduleDetails": [
        {"moduleName": module_name, "masterDetails": [{"name": master_details}]}]}
    parms = {"tenantId": tenant_id}
    return requests.post(url, params=parms, json=request_body).json()


def get_mdms_boundary_data(auth_token, tenant_id):
    get_boundary_data = \
        mdms_call_tenant(auth_token, tenant_id, "egov-location", "TenantBoundary")["MdmsRes"]["egov-location"][
            "TenantBoundary"]
    return get_boundary_data


def create_boundary_new(auth_token, config_function, boundary_type):
    current_boundary_type = boundary_type
    config_function()

    tenant_id = config.TENANT_ID
    boundary_datas = get_mdms_boundary_data(auth_token, tenant_id)

    for boundary_datas in boundary_datas:
        if boundary_datas["hierarchyType"]["code"] == boundary_type:
            boundary_datas = boundary_datas["boundary"]["children"]
            break

    dfs = open_excel_file(config.SHEET)
    locality = get_sheet(dfs, config.SHEET_LOCALITY)

    index_zone_name = get_column_index(locality, config.COLUMN_ZONE_NAME) or 1
    index_zone_code = get_column_index(locality, config.COLUMN_ZONE_CODE) or 2
    index_ward_name = get_column_index(locality, config.COLUMN_WARD_NAME) or 3
    index_ward_code = get_column_index(locality, config.COLUMN_WARD_CODE) or 4
    index_locality_name = get_column_index(locality, config.COLUMN_LOCALITY_NAME) or 5
    index_locality_code = get_column_index(locality, config.COLUMN_LOCALITY_CODE) or 6
    index_area_name = get_column_index(locality, config.COLUMN_LOCALITY_AREA) or 7

    zone_to_code_map = {}
    zone_code_map = {}
    ward_code_map = {}
    ward_to_code_map = {}
    locality_data = []
    ward_data = {}
    zone_ward_map = {}
    for _, row in locality.iterrows():
        zone_to_code_map[row[index_zone_name].strip()] = row[index_zone_code].strip()
        zone_to_code_map[row[index_zone_code].strip()] = row[index_zone_name].strip()
        zone_code_map[row[index_zone_code].strip()] = row[index_zone_name].strip()
        ward_to_code_map[row[index_ward_name].strip()] = row[index_ward_code].strip()
        ward_to_code_map[row[index_ward_code].strip()] = row[index_ward_name].strip()
        ward_code_map[row[index_ward_code].strip()] = row[index_ward_name].strip()

        zone_ward_map[row[index_zone_code].strip()] = zone_ward_map.get(row[index_zone_code].strip(), set())
        zone_ward_map[row[index_zone_code].strip()].add(row[index_ward_code].strip())

        if row[index_ward_name] not in ward_data:
            ward_data[row[index_ward_name]] = []
            ward_data[row[index_ward_name]].append({"id": str(uuid.uuid4()),
                                                    "boundaryNum": 1,
                                                    "name": row[index_ward_name].strip(),
                                                    "localname": row[index_ward_name].strip(),
                                                    "longitude": None,
                                                    "latitude": None,
                                                    "label": "Block",
                                                    "code": row[index_ward_code].strip(),
                                                    "zone": row[index_zone_code].strip(),
                                                    "children": []})

        area = "" if current_boundary_type == "ADMIN" else row[index_area_name].strip().upper().replace(" ",
                                                                                                        "").replace(
            "-", "")
        area_code = area.replace("AREA", "A")

        if current_boundary_type == "REVENUE" and area not in ("AREA1", "AREA2", "AREA3"):
            raise InvalidArgumentException("Area type is not valid - " + area)

        if area_code:
            area_code = " - " + area_code

        locality_data.append({"id": str(uuid.uuid4()),
                              "boundaryNum": 1,
                              "name": row[index_locality_name].strip() + " - " + ward_to_code_map[
                                  row[index_ward_name].strip()] + area_code,
                              "localname": row[index_locality_name].strip() + " - " + ward_to_code_map[
                                  row[index_ward_name].strip()] + area_code,
                              "longitude": None,
                              "latitude": None,
                              "label": "Locality",
                              "code": row[index_locality_code].strip(),
                              "ward": row[index_ward_code].strip(),
                              "area": area,
                              "children": []
                              })
    ward_list = []
    zone_ward_len = 0
    for code, zone_ward in zone_ward_map.items():
        for ward in zone_ward:
            ward_list.append(ward)
        zone_ward_len = zone_ward_len + len(zone_ward)

    zone_data = []
    for zones in zone_code_map:
        name = zone_code_map[zones]
        zone_data.append({
            "id": str(uuid.uuid4()),
            "boundaryNum": 1,
            "name": name.strip(),
            "localname": name.strip(),
            "longitude": None,
            "latitude": None,
            "label": "Zone",
            "code": zones.strip(),
            "children": []})

    for boundary_data in boundary_datas:
        for ward in boundary_data["children"]:
            for revloc in ward["children"]:
                for locality in locality_data:
                    if locality['code'] == revloc['code']:
                        # locality['id']=None
                        locality['id'] = revloc['id']

    ward_loc_data = []
    for id, wards_data in ward_data.items():
        for wards in wards_data:
            for locality in locality_data:
                if locality["ward"] == wards["code"]:
                    wards["children"].append(locality)
            ward_loc_data.append(wards)

    for boundary_data in boundary_datas:
        for zones in zone_data:
            if zones['code'] == boundary_data['code']:
                zones['id'] = boundary_data['id']
        for ward in boundary_data["children"]:
            for loc_ward in ward_loc_data:
                if loc_ward["code"] == ward["code"]:
                    loc_ward["id"] = ward["id"]

    for ward_loc in ward_loc_data:
        for loc in ward_loc["children"]:
            if loc["ward"]:
                loc.pop("ward")

    for zone in zone_data:
        for ward_loc in ward_loc_data:
            if zone["code"] == ward_loc["zone"]:
                zone["children"].append(ward_loc)

    for zones in zone_data:
        for wards in zones["children"]:
            if wards['zone']:
                wards.pop('zone')

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
            "children": zone_data
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

    auth_token = superuser_login()["access_token"]
    errors = validate_boundary_data(auth_token, final_data, boundary_type, config.BOUNDARY_DUPLICATE_CHECK,
                                    config.BOUNDARY_USED_CHECK)

    # validate for one block is in multiple zones
    freq = {}
    for item in ward_list:
        if (item in freq):
            freq[item] += 1
        else:
            freq[item] = 1

    for key, value in freq.items():
        if value > 1:
            errors.append("\nBlock : \"{}\"  is in multiple zones ".format(key))

    if len(errors) > 0:
        print("error list")
        for error in errors:
            print(error)
        return

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
                print("File Path : ", boundary_path, "boundary-data.json")

        else:
            # the file doesn't exists already, so we can safely generate current boundary
            print("Boundary didn't exist. Creating one")
            print("File Path : ", boundary_path + "boundary-data.json")
            existing_boundary_data = final_data

        with open(boundary_path / "boundary-data.json", "w") as f:
            json.dump(existing_boundary_data, f, indent=2)


def main():
    auth_token = superuser_login()["access_token"]
    create_boundary_new(auth_token, load_new_revenue_boundary_config, "REVENUE")


if __name__ == "__main__":
    main()
