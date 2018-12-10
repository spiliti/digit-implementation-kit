from common import *
from config import config
import io
import os

def main():
    with io.open(config.TENANT_JSON, encoding="utf-8") as f:
        tenants_data = json.load(f)

    found = False
    for found_index, tenant in enumerate(tenants_data["tenants"]):
        if tenant["code"] == config.TENANT_ID:
            found = True
            break

    dfs = open_excel_file(config.SHEET)

    tenant = get_sheet(dfs, config.SHEET_TENANT_DETAILS)
    import numpy

    INDEX_TENANT_WEBSITE = "ULB Website"
    INDEX_TENANT_CITYCODE = "City Code"
    INDEX_TENANT_LOCALNAME = "Local Name"
    INDEX_TENANT_DISTRICTNAME = "District Name"
    INDEX_TENANT_DISTRICTCODE = "District Code"
    INDEX_TENANT_REGIONNAME = "Region Name"
    INDEX_TENANT_LATITUDE = "Latitude"
    INDEX_TENANT_LONGITUDE = "Longitude"
    INDEX_TENANT_CONTACT = "Contact Number"
    INDEX_TENANT_EMAIL = "Email Address"
    INDEX_TENANT_ADDRESS = "Address"
    INDEX_TENANT_FB = "FB Link"
    INDEX_TENANT_TWITTER = "Twitter Link"
    INDEX_TENANT_GRADE = "Grade"

    # ° N
    # ° E

    website = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_WEBSITE)])

    citycode = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_CITYCODE)])
    local_name = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_LOCALNAME)])
    district_name = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_DISTRICTNAME)])
    district_code = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_DISTRICTCODE)])
    region_name = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_REGIONNAME)])

    grade = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_GRADE)])
    lat = float(fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_LATITUDE)]))
    long = float(fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_LONGITUDE)]))
    contact = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_CONTACT)])
    email = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_EMAIL)])
    address = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_ADDRESS)])
    fb = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_FB)])
    twitter = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_TWITTER)])

    tenant_object = {
        "code": config.TENANT_ID,
        "name": config.CITY_NAME,
        "description": config.CITY_NAME,
        "logoId": "https://s3.ap-south-1.amazonaws.com/pb-egov-assets/{}/logo.png".format(config.TENANT_ID),
        "imageId": None,
        "domainUrl": website,
        "type": "CITY",
        "twitterUrl": twitter,
        "facebookUrl": fb,
        "emailId": email,
        "OfficeTimings": {
            "Mon - Fri": "9.00 AM - 5.00 PM"
        },
        "city": {
            "name": config.CITY_NAME,
            "localName": local_name,
            "districtCode": str(int(float(district_code))) if district_code else None,
            "districtName": district_name,
            "regionName": region_name,
            "ulbGrade": grade,
            "longitude": long,
            "latitude": lat,
            "shapeFileLocation": None,
            "captcha": None,
            "code": str(int(float(citycode)))
        },
        "address": address,
        "contactNumber": str(int(float(contact)))
    }
    import sys

    json.dump(tenant_object, sys.stdout, indent=2)

    response = os.getenv("ASSUME_YES", None) or input("\nDo you want to append the data in repo (y/[n])? ")

    if response.lower() == "y":
        with io.open(config.TENANT_JSON, mode="w", encoding="utf-8") as f:
            if found:
                print("Tenant - " + config.TENANT_ID + " already exists, overwriting")
                assert tenants_data["tenants"][found_index][
                           "code"] == config.TENANT_ID, "Updating for correct tenant id"
                tenants_data["tenants"][found_index] = tenant_object
            else:
                print("Tenant - " + config.TENANT_ID + " doesn't exists, adding details")
                tenants_data["tenants"].append(tenant_object)
            json.dump(tenants_data, f, indent=2)

        print("Added the tenant to MDMS data")
    else:
        print("Not adding the tenant to MDMS data")


if __name__ == "__main__":
    main()
