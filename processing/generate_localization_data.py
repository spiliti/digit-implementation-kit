import json
import io
import os
from pathlib import Path

from common import superuser_login, upsert_localization
from config import config


def get_code(prefix, code):
    import re
    patt = re.compile(r"[-.\s'\"+]", re.I)
    return (patt.sub("_", prefix) + "_" + patt.sub("_", code)).upper()


with io.open("existing_local.json", mode="r") as f:
    existing_locale = json.load(f)

auth_token = superuser_login()["access_token"]


def process_master(module, master, path, outputpath, locale_module, code="code", name="name", process_dot=False,
                   tenantid=None, prefix=None):
    if prefix is None:
        prefix = module + "_" + master

    if path is None:
        path = config.MDMS_LOCATION / module / (master + ".json")

    if outputpath is None:
        outputpath = Path(".") / "localization" / config.CONFIG_ENV / (module + "_" + master + ".json")

    with io.open(path, mode="r") as f:
        data = json.load(f)

    data_main = data[master]

    locale_data = []
    process_dots = {}
    codes = set()

    for r in data_main:

        if code in r and name not in r and ("TL_" + r[code]) in existing_locale:
            r[name] = existing_locale["TL_" + r[code]]

        if code not in r or name not in r:
            raise Exception("{} or {} is not available in data".format(code, name))

        if process_dot:
            new_code = r[code].split(".")[0]
            if new_code not in process_dots:
                locale_data.append({
                    "code": get_code(prefix, new_code),
                    "message": existing_locale["TL_" + new_code],
                    "module": locale_module,
                    "locale": "en_IN"
                })
                process_dots[new_code] = True

            if len(r[code].split(".")) > 2:
                new_code = r[code].split(".")[1]
                if new_code not in process_dots:
                    locale_data.append({
                        "code": get_code(prefix, new_code),
                        "message": existing_locale["TL_" + new_code],
                        "module": locale_module,
                        "locale": "en_IN"
                    })
                    process_dots[new_code] = True

        current_code = get_code(prefix, r[code])

        if current_code not in codes:
            codes.add(current_code)
            locale_data.append({
                "code": current_code,
                "message": r[name],
                "module": locale_module,
                "locale": "en_IN"
            })
        else:
            print("Code has been duplicated {} - {}".format(r["code"], r[name]))
    with io.open(outputpath, mode="w") as f:
        data = {
            "RequestInfo": {
                "authToken": "{{access_token}}"
            },
            "tenantId": tenantid or "pb",
            "messages": locale_data
        }
        json.dump(
            data, indent=2, fp=f)

        print(upsert_localization(auth_token, data))


def process_boundary_file(auth_token, boundary_path, generate_file=True, write_localization=True):
    locale_data = []

    with open(boundary_path, mode="r") as f:
        data = json.load(f)
        used_codes = set()
        for b in data["TenantBoundary"]:
            boundary_type = b["hierarchyType"]["code"]
            tenant_id = b["boundary"]["code"]

            locale_module = "rainmaker-" + tenant_id

            for l1 in b["boundary"]["children"]:
                code = get_code(tenant_id + "_" + boundary_type, l1["code"])
                if code not in used_codes:
                    used_codes.add(code)
                    locale_data.append({
                        "code": code,
                        "message": l1["name"],
                        "module": locale_module,
                        "locale": "en_IN"
                    })

                for l2 in l1["children"]:
                    code = get_code(tenant_id + "_" + boundary_type, l2["code"])
                    if code not in used_codes:
                        used_codes.add(code)
                        locale_data.append({
                            "code": get_code(tenant_id + "_" + boundary_type, l2["code"]),
                            "message": l2["name"],
                            "module": locale_module,
                            "locale": "en_IN"
                        })

                    for l3 in l2.get("children", []):
                        code = get_code(tenant_id + "_" + boundary_type, l3["code"])
                        if code not in used_codes:
                            used_codes.add(code)
                            locale_data.append({
                                "code": get_code(tenant_id + "_" + boundary_type, l3["code"]),
                                "message": l3["name"],
                                "module": locale_module,
                                "locale": "en_IN"
                            })

            outputpath = Path(".") / "localization" / config.CONFIG_ENV / (
                    "boundary_" + boundary_type + "_" + tenant_id + ".json")

            data = {
                "RequestInfo": {
                    "authToken": "{{access_token}}"
                },
                "tenantId": tenant_id,
                "messages": locale_data
            }

            if generate_file:
                with io.open(outputpath, mode="w") as f:
                    # print(json.dumps(locale_data, indent=2))
                    json.dump(data
                              , indent=2, fp=f)

            if write_localization:
                localize_response = upsert_localization(auth_token, data)

            print(localize_response)


def process_boundary(auth_token):
    for folder in os.scandir(config.MDMS_LOCATION):
        boundary_path = Path(folder.path) / "egov-location" / "boundary-data.json"
        print(boundary_path)

        if os.path.isfile(boundary_path):
            process_boundary_file(auth_token, boundary_path)

# process_master("common-masters", "Department", None, None, "rainmaker-common")
# process_master("common-masters", "Designation", None, None, "rainmaker-common")
# process_master("common-masters", "DocumentType", None, None, "rainmaker-common")
# process_master("common-masters", "OwnerShipCategory", None, None, "rainmaker-common")
# process_master("common-masters", "OwnerType", None, None, "rainmaker-common")
# process_master("common-masters", "OwnerShipCategory", None, None, "rainmaker-common", process_dot=True)
# process_master("common-masters", "StructureType", None, None, "rainmaker-common", process_dot=True)
# process_master("common-masters", "UOM", None, None, "rainmaker-common")
#
# process_master("TradeLicense", "TradeType", None, None, "rainmaker-tl", process_dot=True)
# process_master("TradeLicense", "AccessoriesCategory", None, None, "rainmaker-tl")
# process_master("TradeLicense", "ApplicationType", None, None, "rainmaker-tl", process_dot=False)
#
# process_master("PropertyTax", "Floor", None, None, "rainmaker-pt")
# process_master("PropertyTax", "OccupancyType",
#                None,
#                None, "rainmaker-pt")
#
# process_master("PropertyTax", "OwnerType",
#                None,
#                None, "rainmaker-pt")
#
# process_master("PropertyTax", "OwnerTypeDocument",
#                None,
#                None, "rainmaker-pt")
#
# process_master("PropertyTax", "OwnerShipCategory",
#                None,
#                None, "rainmaker-pt", prefix="PropertyTax_Billing_Slab")
#
# process_master("PropertyTax", "PropertySubType",
#                None,
#                None, "rainmaker-pt", prefix="PropertyTax_Billing_Slab")
#
# process_master("PropertyTax", "SubOwnerShipCategory",
#                None,
#                None, "rainmaker-pt", prefix="PropertyTax_Billing_Slab")
#
# process_master("PropertyTax", "UsageCategoryDetail",
#                None,
#                None, "rainmaker-pt", prefix="PropertyTax_Billing_Slab")
#
# process_master("PropertyTax", "UsageCategoryMajor",
#                None,
#                None, "rainmaker-pt", prefix="PropertyTax_Billing_Slab")
#
# process_master("PropertyTax", "UsageCategoryMinor",
#                None,
#                None, "rainmaker-pt", prefix="PropertyTax_Billing_Slab")
#
# process_master("PropertyTax", "UsageCategorySubMinor",
#                None,
#                None, "rainmaker-pt", prefix="PropertyTax_Billing_Slab")
#
# process_master("PropertyTax", "PropertyType",
#                None,
#                None, "rainmaker-pt", prefix="PropertyTax_Billing_Slab")

# process_boundary()
