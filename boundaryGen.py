import uuid
from common import *
from config import *

dfs = open_excel_file(SHEET)

wards = get_sheet(dfs, SHEET_WARDS)
zones = get_sheet(dfs, SHEET_ZONES)
locality = get_sheet(dfs, SHEET_LOCALITY)

offset = 1

index_code = get_column_index(wards, COLUMN_WARD_CODE)
index_name = get_column_index(wards, COLUMN_WARD_NAME)
index_zone_name = get_column_index(wards, COLUMN_WARD_ADMIN_ZONE_NAME)

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

index_code = get_column_index(zones, COLUMN_ZONE_CODE)
index_name = get_column_index(zones, COLUMN_ZONE_NAME)

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

index_code = get_column_index(locality, COLUMN_LOCALITY_CODE)
index_name = get_column_index(locality, COLUMN_LOCALITY_NAME)
index_admin_block = get_column_index(locality, COLUMN_LOCALITY_ADMIN_BLOCK)

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
    "area": "",
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

final_data = {
    "tenantId": TENANT_ID,
    "moduleName": "egov-location",
    "TenantBoundary": [
        {
            "hierarchyType": {
                "code": "ADMIN",
                "name": "ADMIN"
            },
            "boundary": {
                "id": 1,
                "boundaryNum": 1,
                "name": CITY_NAME,
                "localname": CITY_NAME,
                "longitude": None,
                "latitude": None,
                "label": "City",
                "code": TENANT_ID,
                "children": zones_list
            }
        }
    ]
}

# final_data_json = {
#     "tenantId": TENANT_ID,
#     "moduleName": "egov-location",
#     "TenantBoundary": [
#         {
#             "hierarchyType": {
#                 "code": "ADMIN",
#                 "name": "ADMIN"
#             },
#             "boundary":
#                 {
#                     "id": 1,
#                     "boundaryNum": 1,
#                     "name": CITY_NAME,
#                     "localname": CITY_NAME,
#                     "longitude": None,
#                     "latitude": None,
#                     "label": "City",
#                     "code": TENANT_ID,
#                     "children": [final_data]
#                 }
#         }
#     ]
# }

data = json.dumps(final_data, indent=2)

import os

boundary_path = Path("boundaries")
try:
    os.mkdir(boundary_path / CITY_NAME.lower())
except FileExistsError:
    pass

try:
    os.mkdir(boundary_path / CITY_NAME.lower() / "egov-location")
except FileExistsError:
    pass

with open(boundary_path / CITY_NAME.lower() / "egov-location" / "boundary-data.json", "w") as f:
    f.write(data)
