from pathlib import Path

BOUNDARIES_FOLDER = Path("/Users/tarunlalwani/Desktop/eGovernments/implementation/scripts/source/")

GOOGLE_AUTH_CONFIG = 'SpreadSheetDBService-2be6caceda84.json'

HOST = "https://egov-micro-dev.egovernments.org"
# HOST = "https://egov-micro-qa.egovernments.org"

URL_LOGIN = HOST + "/user/oauth/token"
URL_BILLING_SLAB_CREATE = HOST + "/pt-calculator-v2/billingslab/_create"

MDMS_LOCATION = Path("/Users/tarunlalwani/Desktop/eGovernments/repos/punjab-mdms-data/data/pb")

MDMS_DEPARTMENT_JSON = MDMS_LOCATION  / "common-masters" / "Department.json"
MDMS_DESIGNATION_JSON = MDMS_LOCATION / "common-masters" / "Designation.json"

TENANT = "pb"
CITY_NAME = "Sangrur"
TENANT_ID = TENANT + "." + CITY_NAME.lower()

SHEET_NAME = CITY_NAME.lower() + ".xlsx"
SHEET = BOUNDARIES_FOLDER / SHEET_NAME

SHEET_ZONES = "Admin Zone"
SHEET_WARDS = "Admin Block"
SHEET_LOCALITY = "Locality"

SHEET_DEPARTMENTS = "Employee-Position"

SHEET_DESIGNATION = SHEET_DEPARTMENTS
SHEET_EMPLOYEE = SHEET_DEPARTMENTS

COLUMN_DESIGNATION = "Designation"
COLUMN_DEPARTMENT = "Department"

COLUMN_WARD_CODE = "Block/Ward Code"
COLUMN_WARD_NAME = "Block/Ward Name"
COLUMN_WARD_ADMIN_ZONE_NAME = "Admin Zone Name"

COLUMN_ZONE_CODE = "Zone Code"
COLUMN_ZONE_NAME = "Zone Name"

COLUMN_LOCALITY_CODE = "Locality Code"
COLUMN_LOCALITY_NAME = "Locality Name"
COLUMN_LOCALITY_ADMIN_BLOCK = "Admin Block/Ward Name"
COLUMN_LOCALITY_AREA = "Area Name"
######################################################

SHEET_ZONES = "Revenue Zone"
SHEET_WARDS = "Revenue Block or Ward"
SHEET_LOCALITY = "Locality"

SHEET_DEPARTMENTS = "Employee-Position"

SHEET_DESIGNATION = SHEET_DEPARTMENTS
SHEET_EMPLOYEE = SHEET_DEPARTMENTS

COLUMN_DESIGNATION = "Designation"
COLUMN_DEPARTMENT = "Department"

COLUMN_WARD_CODE = "Rev Block/Ward Code"
COLUMN_WARD_NAME = "Rev Block/Ward Name"
COLUMN_WARD_ADMIN_ZONE_NAME = "Rev Zone Name"

COLUMN_ZONE_CODE = "Rev Zone Code"
COLUMN_ZONE_NAME = "Rev Zone Name"

COLUMN_LOCALITY_CODE = "Locality Code"
COLUMN_LOCALITY_NAME = "Locality Name"
COLUMN_LOCALITY_ADMIN_BLOCK = "Rev Block/Ward Name"
COLUMN_LOCALITY_AREA = "Area Name"