from common import *
from config import config
import io
with io.open(config.TENANT_JSON, encoding="utf-8") as f:
    tenants_data = json.load(f)

found = False
for tenant in tenants_data["tenants"]:
    if tenant["code"] == config.TENANT_ID:
        found = True
        break

if found:
    print ("Tenant - " + config.TENANT_ID + " already exists, cannot regenerate")
else:
    dfs = open_excel_file(config.SHEET)

    tenant = get_sheet(dfs, config.SHEET_TENANT_DETAILS)
    import numpy

    INDEX_TENANT_WEBSITE = "ULB Website"
    INDEX_TENANT_CITYCODE = "City Code"
    INDEX_TENANT_LATITUDE = "Latitude"
    INDEX_TENANT_LONGITUDE = "Longitude"
    INDEX_TENANT_CONTACT = "Contact Number"
    INDEX_TENANT_EMAIL = "Email Address"
    INDEX_TENANT_ADDRESS = "Address"
    INDEX_TENANT_FB = "FB Link"
    INDEX_TENANT_TWITTER = "Twitter Link"
    # ° N
    # ° E
    def fix_value(val):
        if val is None:
            return ""

        if type(val) is str and "°" in val:
            return val.split("°")[0]

        if type(val) is str:
            return val.strip()
        elif numpy.isnan(val):
            return None
        else:
            return str(val)


    website = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_WEBSITE)])
    citycode = fix_value(tenant.iloc[0][get_column_index(tenant, INDEX_TENANT_CITYCODE)])
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
        "logoId": None,
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
            "localName": None,
            "districtCode": None,
            "districtName": None,
            "regionName": None,
            "ulbGrade": None,
            "longitude": long,
            "latitude": lat,
            "shapeFileLocation": None,
            "captcha": None,
            "code": str(int(float(citycode)))
        },
        "address": address,
        "contactNumber": contact
    }

    print(tenant_object)

    response = input("Do you want to append the data in repo (y/[n])?")

    if response.lower() == "y":
        with io.open(config.TENANT_JSON,mode="w", encoding="utf-8") as f:
            tenants_data["tenants"].append(tenant_object)
            json.dump(tenants_data,f, indent=2)

        print("Added the tenant to MDMS data")
    else:
        print("Not adding the tenant to MDMS data")
