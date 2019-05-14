import json

import os
import xlwt
from xlwt import Worksheet
from config import config


def download_boundary(tenant, boundary_type):
    # url = "https://raw.githubusercontent.com/egovernments/punjab-mdms-data/master/data/{}/egov-location/boundary-data.json".replace(
    #     "{}", tenant.replace(".", "/"))

    boundary_path = config.MDMS_LOCATION / tenant.split(".")[-1] / "egov-location" / "boundary-data.json"

    if not os.path.isfile(boundary_path):
        print(boundary_path)
        print("No boundary data exists for tenantId \"{}\", not downloading".format(tenant.upper()))
        return

    wk = xlwt.Workbook()
    zone: Worksheet = wk.add_sheet("Revenue Zone")
    ward: Worksheet = wk.add_sheet("Revenue Block or Ward")
    locality: Worksheet = wk.add_sheet("Locality")

    for i, col in enumerate(["S.No", "Rev Zone Code*", "Rev Zone Name*"]):
        zone.write(0, i, col)

    for i, col in enumerate(["S.No", "Rev Block/Ward Code*", "Rev Block/Ward Name*", "Rev Zone Name*"]):
        ward.write(0, i, col)

    for i, col in enumerate(
            ["S.No", "Locality Code*", "Locality Name*", "Rev Block/Ward Name", "Area Name (Area 1, 2 or 3)"]):
        locality.write(0, i, col)

    # response = requests.get(url)
    #
    # boundary = response.json()['TenantBoundary']

    with open(boundary_path) as f:
        boundary = json.load(f)['TenantBoundary']

    if boundary[0]["hierarchyType"]["code"] == boundary_type:
        boundary_data = boundary[0]["boundary"]
    elif len(boundary) > 1:
        boundary_data = boundary[1]["boundary"]
    else:
        return

    row_zone = 1
    row_ward = 1
    row_locality = 1

    for l1 in boundary_data["children"]:
        zone.write(row_zone, 0, row_zone)
        zone.write(row_zone, 1, l1['code'])
        zone.write(row_zone, 2, l1['name'])
        row_zone += 1

        for l2 in l1["children"]:
            ward.write(row_ward, 0, row_ward)
            ward.write(row_ward, 1, l2['code'])
            ward.write(row_ward, 2, l2['name'])
            ward.write(row_ward, 3, l1['name'])
            row_ward += 1

            for value in l2["children"]:
                name = value['name'].split(" - ")
                if len(name) >= 3:
                    name = name[0:-2]
                name = " - ".join(name)

                locality.write(row_locality, 0, row_locality)
                locality.write(row_locality, 1, value['code'])
                locality.write(row_locality, 2, name)
                locality.write(row_locality, 3, l2['code'])
                locality.write(row_locality, 4, value['area'])
                row_locality += 1
                # print(value['name'] + "," + value['code'])
    file_name = tenant + "_rev_boundary.xls"
    dir_name = "boundary_download/"
    wk.save(dir_name+file_name)
    print("\n", "XLSX file created with file name : {}".format(tenant) + "_rev_boundary.xls")


if __name__ == "__main__":
    download_boundary(config.TENANT_ID, "REVENUE")



