from .local import *

config.ROLE_CODE_MAP = {
    "AE_CREATOR": "Abstract Estimate Creator",
    "Asset Administrator": "Asset Administrator",
    "AssetCreator": "Asset Creator",
    "AssetReportViewer": "Asset Report Viewer",
    "BANK_COLL_OPERATOR": "Bank Collection Operator",
    "CEMP": "Counter Employee",
    "CITIZEN": "Citizen",
    "COLL_OPERATOR": "Collection Operator",
    "COLL_RECEIPT_CREATOR": "Collections Receipt Creator",
    "COLL_REMIT_TO_BANK": "Collections Remitter",
    "COLL_REP_VIEW": "Collection Report Viewer",
    "COMMISSIONER": "Commissioner",
    "CONTRACTOR_ADVANCE_CREATOR": "Contractor Advance creator",
    "CSC_COLL_OPERATOR": "CSC Collection Operator",
    "CSR": "Citizen Service Representative",
    "DE_CREATOR": "Detailed Estimate Creator",
    "DGRO": "Department Grievance Routing Officer",
    "DMA OFFICE OFFICER": "DMA Office Officer",
    "EGF_ADMINISTRATOR": "Finance Admin",
    "EGF_BILL_APPROVER": "EGF Bill Approver",
    "EGF_BILL_CREATOR": "EGF Bill Creator",
    "EGF_MASTER_ADMIN": "Finance Master Admin",
    "EGF_PAYMENT_APPROVER": "Finance Payment Approver",
    "EGF_PAYMENT_CREATOR": "Finance Payment Creator",
    "EGF_REPORT_VIEW": "Finance Report View",
    "EGF_VOUCHER_APPROVER": "Finance Voucher Approver",
    "EGF_VOUCHER_CREATOR": "Finance Voucher Creator",
    "EMPLOYEE": "Employee",
    "EMPLOYEE ADMIN": "Employee Admin",
    "EMPLOYEE_FINANCE": "Employee Finance",
    "FEMP": "Field Employee",
    "GA": "Grivance Administrator",
    "GO": "Grievance Officer",
    "GRO": "Grievance Routing Officer",
    "LEGACY_RECEIPT_CREATOR": "Legacy Receipt Creator",
    "LOA_CREATOR": "LOA Creator",
    "MB_CREATOR": "MB creator",
    "PGR-ADMIN": "PGR Administrator",
    "Property Approver": "Property Approver",
    "Property Verifier": "Property Verifier",
    "PTCEMP": "Property Tax Counter Employee",
    "PTFEMP": "Property Tax Field Employee",
    "PTSTADMIN": "Property Tax State Administrator",
    "PTULBADMIN": "Property Tax ULB Administrator",
    "RO": "Redressal Officer",
    "SRA": "Service request administrator",
    "SRC": "Service request Creator",
    "SRSU": "Service request status update",
    "SRV": "Service request Report viewer",
    "STADMIN": "State Administrator",
    "SUPERUSER": "Super User",
    "SYS_INTEGRATOR_FINANCE": "System Integrator Finance",
    "SYS_INTEGRATOR_WATER_SEW": "System Integrator W&S",
    "TL_ADMIN": "TL Admin",
    "TL_APPROVER": "Trade License Approver Employee",
    "TL_CEMP": "Trade License Counter Employee",
    "TL_CREATOR": "TL Creator",
    "ULB OFFICER": "ULB Officer",
    "ULB Operator": "ULB Operator",
    "ULBADMIN": "ULB Administrator",
    "WO_CREATOR": "WO Creator",
    "WORKS_ADMINISTRATOR": "Works Administrator",
    "WORKS_APPROVER": "Works Approver",
    "WORKS_BILL_CREATOR": "Works Bill Creator",
    "WORKS_FINANCIAL_APPROVER": "Financials Approver",
    "WORKS_MASTER_CREATOR": "Works Master creator"
}


def load_config():
    config.GOOGLE_AUTH_CONFIG = config.BASE_PATH + '/SpreadSheetDBService-2be6caceda84.json'

    config.URL_LOGIN = config.HOST + "/user/oauth/token"
    config.URL_BILLING_SLAB_CREATE = config.HOST + "/pt-calculator-v2/billingslab/_create"

    config.URL_SEARCH_LOCALITIES_USED_IN_REVENUE = config.HOST + "/egov-searcher/rainmaker-pt-customsearch-punjab/searchLocalitiesUsedInRevenue/_get"
    config.URL_SEARCH_LOCALITIES_USED_IN_ADMIN = config.HOST + "/egov-searcher/rainmaker-pt-customsearch-punjab/searchLocalitiesUsedInAdmin/_get"

    config.BOUNDARY_DUPLICATE_CHECK = True
    config.BOUNDARY_USED_CHECK = True

    config.MDMS_DEPARTMENT_JSON = config.MDMS_LOCATION / "common-masters" / "Department.json"
    config.MDMS_DESIGNATION_JSON = config.MDMS_LOCATION / "common-masters" / "Designation.json"

    config.MDMS_ACTIONS_JSON = config.MDMS_LOCATION / "ACCESSCONTROL-ACTIONS-TEST" / "actions-test.json"
    config.MDMS_ROLEACTIONS_JSON = config.MDMS_LOCATION / "ACCESSCONTROL-ROLEACTIONS" / "roleactions.json"

    config.CITY_MODULES_JSON = config.MDMS_LOCATION / "tenant" / "citymodule.json"
    config.TENANT_JSON = config.MDMS_LOCATION / "tenant" / "tenants.json"

    config.TENANT_ID = config.TENANT + "." + config.CITY_NAME.lower()

    config.SHEET_NAME = config.CITY_NAME.lower() + ".xlsx"
    config.SHEET = config.BOUNDARIES_FOLDER / config.SHEET_NAME
    if not os.path.isfile(config.SHEET):
        config.SHEET_NAME = config.CITY_NAME.lower() + ".xls"
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


def load_new_revenue_boundary_config():
    config.SHEET_LOCALITY = "RevenueBoundary"

    config.COLUMN_ZONE_CODE = "Rev Zone Code"
    config.COLUMN_ZONE_NAME = "Rev Zone Name"

    config.COLUMN_WARD_CODE = "Rev Block/Ward Code"
    config.COLUMN_WARD_NAME = "Rev Block/Ward Name"

    config.COLUMN_LOCALITY_CODE = "Locality Code"
    config.COLUMN_LOCALITY_NAME = "Locality Name"
    config.COLUMN_LOCALITY_AREA = "Area Name"

def load_tl_billing_slab_download_config():
    config.SHEET_TRADES ="Trades"
    config.SHEET_ACCESSORIES="Accessories item"

    config.TRADE_COLUMN_LICENSE_TYPE="License type"
    config.TRADE_COLUMN_STRUCTURE_TYPE="Structure Type"
    config.TRADE_COLUMN_STRUCTURE_SUB_TYPE="Structure sub type"
    config.TRADE_COLUMN_TRADE_CATEGORY="Trade Category"
    config.TRADE_COLUMN_TRADE_TYPE="Trade Type"
    config.TRADE_COLUMN_TRADE_SUB_TYPE="Trade Sub-Type"
    config.TRADE_COLUMN_CHARGE="Charge"
    config.TRADE_COLUMN_UOM_UNIT="UOM Unit"
    config.TRADE_COLUMN_UOM_FROM="UOM From"
    config.TRADE_COLUMN_UOM_TO = "UOM To"




load_config()
