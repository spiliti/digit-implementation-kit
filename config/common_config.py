from .local import *

config.GOOGLE_AUTH_CONFIG = 'SpreadSheetDBService-2be6caceda84.json'

config.URL_LOGIN = config.HOST + "/user/oauth/token"
config.URL_BILLING_SLAB_CREATE = config.HOST + "/pt-calculator-v2/billingslab/_create"

config.MDMS_DEPARTMENT_JSON = config.MDMS_LOCATION / "common-masters" / "Department.json"
config.MDMS_DESIGNATION_JSON = config.MDMS_LOCATION / "common-masters" / "Designation.json"

config.CITY_MODULES_JSON = config.MDMS_LOCATION / "tenant" / "citymodule.json"
config.TENANT_JSON = config.MDMS_LOCATION / "tenant" / "tenants.json"

config.TENANT_ID = config.TENANT + "." + config.CITY_NAME.lower()

config.SHEET_NAME = config.CITY_NAME.lower() + ".xlsx"
config.SHEET = config.BOUNDARIES_FOLDER / config.SHEET_NAME

config.SHEET_DEPARTMENTS = "Employee-Position"

config.SHEET_DESIGNATION = config.SHEET_DEPARTMENTS
config.SHEET_EMPLOYEE = config.SHEET_DEPARTMENTS
config.SHEET_TENANT_DETAILS = "City"

config.COLUMN_DESIGNATION = "Designation"
config.COLUMN_DEPARTMENT = "Department"


def load_admin_boundary_config():
    config.SHEET_ZONES = "Admin Zone"
    config.SHEET_WARDS = "Admin Block"
    config.SHEET_LOCALITY = "Locality"


    config.COLUMN_WARD_CODE = "Block/Ward Code"
    config.COLUMN_WARD_NAME = "Block/Ward Name"
    config.COLUMN_WARD_ADMIN_ZONE_NAME = "Admin Zone Name"

    config.COLUMN_ZONE_CODE = "Zone Code"
    config.COLUMN_ZONE_NAME = "Zone Name"

    config.COLUMN_LOCALITY_CODE = "Locality Code"
    config.COLUMN_LOCALITY_NAME = "Locality Name"
    config.COLUMN_LOCALITY_ADMIN_BLOCK = "Admin Block/Ward Name"
    config.COLUMN_LOCALITY_AREA = "Area Name"


def load_revenue_boundary_config():
    config.SHEET_ZONES = "Revenue Zone"
    config.SHEET_WARDS = "Revenue Block or Ward"
    config.SHEET_LOCALITY = "Locality"

    config.COLUMN_WARD_CODE = "Rev Block/Ward Code"
    config.COLUMN_WARD_NAME = "Rev Block/Ward Name"
    config.COLUMN_WARD_ADMIN_ZONE_NAME = "Rev Zone Name"

    config.COLUMN_ZONE_CODE = "Rev Zone Code"
    config.COLUMN_ZONE_NAME = "Rev Zone Name"

    config.COLUMN_LOCALITY_CODE = "Locality Code"
    config.COLUMN_LOCALITY_NAME = "Locality Name"
    config.COLUMN_LOCALITY_ADMIN_BLOCK = "Rev Block/Ward Name"
    config.COLUMN_LOCALITY_AREA = "Area Name"
