import json

from common import open_excel_file, get_sheet, get_column_index
from config import config
import io

tenants = None

xl = open_excel_file("/Users/tarunlalwani/Downloads/CityCodes.xlsx")

city = get_sheet(xl, "City")

INDEX_CITYNAME = get_column_index(city, "City Name")
INDEX_LOCALNAME = get_column_index(city, "Local Name")
INDEX_CITYCODE = get_column_index(city, "City Code")
INDEX_GRADE = get_column_index(city, "GRADE")
INDEX_DISTRICTNAME = get_column_index(city, "District Name")
INDEX_DISTRICTCODE = get_column_index(city, "District Code")
INDEX_REGIONNAME = get_column_index(city, "Region Name")
INDEX_REGIONCODE = get_column_index(city, "Region Code")
INDEX_MUNICIPALITYNAME = get_column_index(city, "Municipality Name")
INDEX_CONTACTNUMBER = get_column_index(city, "Contact Number")
INDEX_EMAIL = get_column_index(city, "Email Address")

with io.open(config.TENANT_JSON) as f:
    tenants = json.load(f)


def dataload(row):
    print(row)


tenants_information = {}

for _, row in city.iterrows():
    ulbcode = "pb." + row[INDEX_CITYNAME].strip().replace(" ", "").replace("-", "").lower()
    info = {}
    tenants_information[ulbcode] = info

    info["City"] = row[INDEX_CITYNAME].strip()
    info["LocalName"] = row[INDEX_LOCALNAME].strip()
    info["CityCode"] = "{}".format(row[INDEX_CITYCODE])
    info["Grade"] = row[INDEX_GRADE].strip()
    info["DistrictName"] = row[INDEX_DISTRICTNAME].strip()
    info["DistrictCode"] = "{}".format(row[INDEX_DISTRICTCODE])
    info["RegionName"] = row[INDEX_REGIONNAME].strip()
    info["RegionCode"] = "{}".format(row[INDEX_REGIONCODE])
    info["MunicipalityName"] = row[INDEX_MUNICIPALITYNAME].strip()
    info["ContactNo"] = "{}".format(row[INDEX_CONTACTNUMBER])
    info["Email"] = "{}".format(row[INDEX_EMAIL])

# print(tenants_information)

for tenant in tenants["tenants"]:
    code = tenant['code']

    if code not in tenants_information:
        print(code)
        continue
    info = tenants_information[code]

    name = code.replace("pb.", "").capitalize()
    tenant["name"] = name
    tenant["description"] = name
    tenant["logoId"] = 'https://s3.ap-south-1.amazonaws.com/pb-egov-assets/{}/logo.png'.format(code)
    tenant["city"]["name"] = name
    tenant["city"]["localName"] = info["LocalName"]

    tenant["city"]["districtCode"] = info["DistrictCode"]
    tenant["city"]["districtName"] = info["DistrictName"]
    tenant["city"]["regionName"] = info["RegionName"]
    tenant["city"]["regionCode"] = info["RegionCode"]
    tenant["city"]["ulbGrade"] = info["Grade"]
    tenant["city"]["municipalityName"] = info["MunicipalityName"]
    if tenant["emailId"] is None:
        tenant["emailId"] = info["Email"]
    if tenant["contactNumber"] is None and info["ContactNo"] and info["ContactNo"] != "nan":
        tenant["contactNumber"] = info["ContactNo"]
    if tenant["city"]["code"] is not None and tenant["city"]["code"] != info["CityCode"]:
        print("Tenant code mismatch", "NEW:" + code, info["CityCode"], "OLD:" + tenant["city"]["code"])
    tenant["city"]["code"] = info["CityCode"]

with io.open(config.TENANT_JSON, mode="w") as f:
    json.dump(tenants, f, indent=2)
