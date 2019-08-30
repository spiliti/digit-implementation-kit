import sys
import math
from math import isnan
from common import superuser_login, open_excel_file, get_sheet
from config import config, load_config
import requests
import json


def get_slab_code(slab):
    fields = ["licenseType", "structureType", "tradeType", "accessoryCategory"]
    data = []

    for field in fields:
        value = slab[field]
        if type(value) is not str and value is not None and isnan(value):
            value = None
        if value == "N.A.":
            value = None
        elif value == "NULL":
            value = None
        elif value == "Infinite":
            value = "Infinity"

        if type(value) is float:
            value = int(value)
        data.append(str(value or "-"))

    return "|".join(data)


def remove_nan(data, default=None):
    if type(data) in (float, int) and math.isnan(data):
        return default

    if type(data) is str:
        data = data.strip()

    return data


def get_slab_object(row_data, tenant_id):
    data = {
        "tenantId": tenant_id,
        "licenseType": remove_nan(row_data["licenseType"]),
        "structureType": remove_nan(row_data["structureType"]),
        "tradeType": remove_nan(row_data["tradeType"]),
        "accessoryCategory": remove_nan(row_data["accessoryCategory"]),
        "type": remove_nan(row_data["type"]),
        "uom": remove_nan(row_data["uom"]),
        "fromUom": remove_nan(row_data["fromUom"]),
        "toUom": remove_nan(row_data["toUom"]),
        "rate": remove_nan(row_data["rate"])
    }

    if "id" in row_data and type(row_data['id']) is str and len(row_data["id"]) > 6:
        data["id"] = row_data["id"].replace(' ', '')

    return data


def compare_slabs_with_same_id(row_data, bs_data):
    if type(row_data["rate"]) is str:
        row_data["rate"] = row_data["rate"].strip()

        if row_data["rate"]:
            row_data["rate"] = float(row_data["rate"])
        else:
            row_data["rate"] = math.nan
    # if math.isnan(row_data["rate"]):
    #     row_data["rate"] = 0.0

    if row_data["id"] == bs_data["id"] and \
            row_data["structureType"] == bs_data["structureType"] and \
            row_data["tradeType"] == bs_data["tradeType"] and \
            row_data["toUom"] == bs_data["toUom"] and \
            row_data["fromUom"] == bs_data["fromUom"] and \
            row_data["rate"] == bs_data["rate"] and \
            row_data["accessoryCategory"] == bs_data["accessoryCategory"]:
        return False
    else:

        return True


def check_for_overlapping_slabs(slabs):
    for slab in slabs:
        if slab["fromUom"] == "Infinity":
            slab["fromUom"] = sys.maxsize
        if slab["toUom"] == "Infinity":
            slab["toUom"] = sys.maxsize
        if slab["accessoryCategory"] == "ACC-64":
            print("")

    fromUom_toUom_lis_sorted_by_fromUom = sort_by_uom_from(slabs)
    is_overlapped = not (fromUom_toUom_lis_sorted_by_fromUom == sorted(fromUom_toUom_lis_sorted_by_fromUom))
    diff_slab_having_same_fromUom = check_diff_slab_having_same_fromUom(slabs)

    return is_overlapped or diff_slab_having_same_fromUom


def sort_by_uom_from(slabs):
    temp_slabs = slabs.copy()
    sorted_list = []
    for uom_from in sorted([slab["fromUom"] for slab in temp_slabs]):
        for slab in temp_slabs:
            if uom_from == slab["fromUom"]:
                sorted_list.append(slab["fromUom"])
                sorted_list.append(slab["toUom"])
                temp_slabs.remove(slab)
                break
    return sorted_list


def check_diff_slab_having_same_fromUom(slabs):
    from_uoms = sorted([slab["fromUom"] for slab in slabs])
    for i in range(0, len(from_uoms) - 1):
        if from_uoms[i] == from_uoms[i + 1]:
            return True

    return False


def is_new_billing_slab(row_data):
    return "id" not in row_data and \
           row_data["rate"] is not None and row_data["rate"] >= 0 and \
           row_data["toUom"] is not None and row_data["toUom"] >= 0 and \
           row_data["fromUom"] is not None and row_data["fromUom"] >= 0


def create_billing_slab(new_slabs_data, auth_token, tenant_id):
    print("Creating New billing slabs")
    print(json.dumps(new_slabs_data, indent=2))
    res = requests.post(config.HOST + "/tl-calculator/billingslab/_create?tenantId={}".format(tenant_id), json={
        "RequestInfo": {
            "authToken": auth_token
        },
        "billingSlab": new_slabs_data
    })

    print(json.dumps(res.json(), indent=2))


def update_billing_slab(update_slabs_data, auth_token, tenant_id):
    print("Updating changed billing slabs")
    print(json.dumps(update_slabs_data, indent=2))
    res = requests.post(config.HOST + "/tl-calculator/billingslab/_update?tenantId={}".format(tenant_id), json={
        "RequestInfo": {
            "authToken": auth_token
        },
        "billingSlab": update_slabs_data
    })

    print(json.dumps(res.json(), indent=2))


import os
from tl_billing_slab_download import search_tl_billing_slab


def create_and_update_billing_slab(auth_token, tenant):
    response = os.getenv("ASSUME_YES", None) or input(
        "Your ENV is \"{}\" and TENANT ID is \"{}\", You want to proceed (y/[n])?".format(config.CONFIG_ENV,
                                                                                          tenant))
    if response.lower() == "n":
        os._exit(0)

    tenant_id = tenant
    config.CITY_NAME = tenant.replace(" ", "").replace("pb.", "")
    load_config()

    billing_slabs = search_tl_billing_slab(auth_token)["billingSlab"]

    get_slab_by_id_from_bs = {slab["id"]: slab for slab in billing_slabs if slab["id"]}

    dfs = open_excel_file(config.BASE_PPATH / "source" / "{}_tl_billing_slab.xls".format(tenant_id))
    data = get_sheet(dfs, "Trades_and_Accessories")

    duplicate_id_check = []
    error_lis = []
    row_data_code_map = {}
    update_slabs = []
    new_slabs = []

    for _id, slabs in data.iterrows():
        row_data = get_slab_object(slabs.to_dict(), tenant_id)

        if row_data["tradeType"]:  # valiadate empty structure type
            if row_data["rate"] is not None and row_data["rate"] >= 0:
                if row_data["structureType"]:
                    pass
                else:
                    error_lis.append("empty structure type: {}".format(row_data["tradeType"]))

        if row_data["rate"] is not None and row_data["rate"] >= 0:  # validate rate and fromUom and toUom
            if row_data["licenseType"]:
                pass
            else:
                error_lis.append(
                    "empty license type: {} ".format(row_data["tradeType"] or row_data["accessoryCategory"]))

            if type(row_data["fromUom"]) in (float, int):
                if row_data["fromUom"] is not None and row_data["fromUom"] >= 0:
                    pass
                else:
                    error_lis.append(
                        "empty fromuom : {}".format(row_data["tradeType"] or row_data["accessoryCategory"]))
            else:
                if row_data["fromUom"] == '':
                    pass
                else:
                    error_lis.append(
                        "empty fromUom: {} ".format(row_data["tradeType"] or row_data["accessoryCategory"]))

            if type(row_data["toUom"]) in (float, int):
                if row_data["toUom"] is not None and row_data["toUom"] >= 0:
                    pass
                else:
                    error_lis.append("empty toUom: {} ".format(row_data["tradeType"] or row_data["accessoryCategory"]))
            else:
                if row_data["toUom"] == 'Infinity':
                    pass
                else:
                    error_lis.append("empty toUom: {} ".format(row_data["tradeType"] or row_data["accessoryCategory"]))

        slab_code = get_slab_code(row_data)
        if "id" in row_data:
            if row_data["id"] in duplicate_id_check:  # Checking Duplicate id in sheet
                error_lis.append("Duplicate id in the sheet: {}".format(row_data["id"]))

            elif row_data["id"] not in get_slab_by_id_from_bs:  # Checking Invalid ID in sheet
                error_lis.append("Wrong id in the sheet: {}".format(row_data["id"]))

            else:
                duplicate_id_check.append(row_data["id"])

                if slab_code not in row_data_code_map:
                    row_data_code_map[slab_code] = []
                    row_data_code_map[slab_code].append(row_data)

                    if compare_slabs_with_same_id(row_data, get_slab_by_id_from_bs[row_data["id"]]):
                        update_slabs.append(row_data)

                elif slab_code in row_data_code_map:
                    row_data_code_map[slab_code].append(row_data)

                    if compare_slabs_with_same_id(row_data, get_slab_by_id_from_bs[row_data["id"]]):
                        update_slabs.append(row_data)

            get_slab_by_id_from_bs.pop(row_data["id"], None)


        elif is_new_billing_slab(row_data):
            if slab_code not in row_data_code_map:
                row_data_code_map[slab_code] = []
                row_data_code_map[slab_code].append(row_data)
                new_slabs.append(row_data)

            elif slab_code in row_data_code_map:
                row_data_code_map[slab_code].append(row_data)
                new_slabs.append(row_data)

    if len(get_slab_by_id_from_bs) > 0:  # Checking if any ID is missing in Sheet
        error_lis.append(
            "Missing IDs from sheet: {}".format([missing_id for missing_id in get_slab_by_id_from_bs.keys()]))

    for code, slabs in row_data_code_map.items():
        if len(slabs) > 1:
            is_overlapped = check_for_overlapping_slabs(slabs)
            if is_overlapped:
                error_lis.append("Overlapped Slabs for code : {}".format(code))

    if error_lis:
        for err in error_lis:
            print(err)
    else:
        if update_slabs:
            update_billing_slab(update_slabs, auth_token, tenant_id)
        if new_slabs:
            create_billing_slab(new_slabs, auth_token, tenant_id)
