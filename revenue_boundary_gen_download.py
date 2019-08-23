from os.path import dirname

from xlwt import Worksheet
import xlwt
from common import superuser_login
from urllib.parse import urljoin
import requests
from config import config


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


def download_revenue_boundary(auth_token, boundary_type):
    wk = xlwt.Workbook()
    revenue_boundary: Worksheet = wk.add_sheet("RevenueBoundary")

    for i, col in enumerate(
            ["S.N.", "Rev Zone Name", "Rev Zone Code", "rev Block/ward name", "Rev Block/ward code", "Locality name",
             "Locality Code", "Area name"]):
        revenue_boundary.write(0, i, col)

    tenant_id = config.TENANT_ID
    boundary_datas = get_mdms_boundary_data(auth_token, tenant_id)

    for boundary_data in boundary_datas:
        if boundary_data["hierarchyType"]["code"] == boundary_type:
            boundarydata = boundary_data["boundary"]["children"]
            break

    row_no = 1

    for zone in boundarydata:
        for block in zone["children"]:
            for locality in block["children"]:
                locality_code = locality["code"]
                locality_name = locality["name"]
                locality_name = locality_name.rsplit('-', 2)[0].strip()
                area_name = locality["area"]
                block_code = block["code"]
                block_name = block["name"]
                zone_code = zone["code"]
                zone_name = zone["name"]
                revenue_boundary.write(row_no, 0, row_no)
                revenue_boundary.write(row_no, 1, zone_name)
                revenue_boundary.write(row_no, 2, zone_code)
                revenue_boundary.write(row_no, 3, block_name)
                revenue_boundary.write(row_no, 4, block_code)

                revenue_boundary.write(row_no, 5, locality_name)
                revenue_boundary.write(row_no, 6, locality_code)
                revenue_boundary.write(row_no, 7, area_name)

                row_no = row_no + 1

    file_name = "{}.xls".format(config.TENANT_ID)
    wk.save(file_name)
    print("\n", "XLSX file created with file name : {}".format(file_name))
    print(" PATH : {}/{}".format(dirname(__file__), file_name))


def main():
    auth_token = superuser_login()["access_token"]

    download_revenue_boundary(auth_token, "REVENUE")


if __name__ == "__main__":
    main()
