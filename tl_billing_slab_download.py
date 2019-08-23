from os.path import dirname
from xlwt import Worksheet
import xlwt
from common import *


def get_accessories_from_mdms(auth_token):
    accessories_types = mdms_call(auth_token, "TradeLicense", "AccessoriesCategory")["MdmsRes"]["TradeLicense"][
        "AccessoriesCategory"]
    trade_license_acc_code_map = {}
    for accessories_type in accessories_types:
        trade_license_acc_code_map[accessories_type["code"]] = []
    return trade_license_acc_code_map


def get_trade_type_from_mdms(auth_token):
    trade_types = mdms_call(auth_token, "TradeLicense", "TradeType")["MdmsRes"]["TradeLicense"]["TradeType"]
    trade_type_code_map = {}
    for c in trade_types:
        trade_type_code_map[c["code"]] = []
    return trade_type_code_map


def get_billing_slab_localization(auth_token):
    localization_data = search_localization(auth_token, "rainmaker-tl", "en_IN", 'pb')["messages"]
    code_to_message_map = {}
    for loc in localization_data:
        if "TRADELICENSE_TRADETYPE" in loc["code"] or "TRADELICENSE_ACCESSORIESCATEGORY" in loc["code"]:
            code_to_message_map[loc["code"]] = loc["message"]

    return code_to_message_map


def get_trade_localization_code(tradetype):
    return "TRADELICENSE_TRADETYPE_" + tradetype.replace('.', '_').replace('-', '_')


def get_accessories_localization_code(tradetype):
    return "TRADELICENSE_ACCESSORIESCATEGORY_" + tradetype.replace('.', '_').replace('-', '_')


def sort_by_uom_from(slabs):
    sorted_list = []
    for uom_from in sorted([slab["fromUom"] for slab in slabs]):
        for slab in slabs:
            if uom_from == slab["fromUom"]:
                sorted_list.append(slab)
                slabs.remove(slab)
                break
    return sorted_list


def download_billing_slab(auth_token):
    wk = xlwt.Workbook()
    trd_acc: Worksheet = wk.add_sheet("Trades_and_Accessories")

    for i, col in enumerate(
            ["S.N.", "id", "licenseType", "structureType", "Trade Sub-Type", "tradeType", "Accessories Name",
             "accessoryCategory", "type",
             "rate", "uom", "fromUom", "toUom"]):
        trd_acc.write(0, i, col)

    billing_slabs = search_tl_billing_slab(auth_token)["billingSlab"]

    localization_map = get_billing_slab_localization(auth_token)

    acc_map = get_accessories_from_mdms(auth_token)

    trade_map = get_trade_type_from_mdms(auth_token)

    for billing_slab in billing_slabs:
        if billing_slab["tradeType"] is not None:
            trade_map[billing_slab["tradeType"]].append(billing_slab)
        elif billing_slab["accessoryCategory"] is not None:
            acc_map[billing_slab["accessoryCategory"]].append(billing_slab)

    row_no = 1

    for code, slabs in trade_map.items():
        if len(slabs) != 0:
            for slab in slabs:
                id = slab["id"]

                structure_type = slab["structureType"]
                codes = slab["tradeType"]
                charge = slab["rate"]
                uom_unit = slab["uom"]
                uom_from = slab["fromUom"]
                uom_to = slab["toUom"]

                trade_sub_type_name = localization_map.get(get_trade_localization_code(slab["tradeType"])) or ""

                trd_acc.write(row_no, 0, row_no)

                trd_acc.write(row_no, 1, id)
                trd_acc.write(row_no, 2, "PERMANENT")
                trd_acc.write(row_no, 3, structure_type)
                trd_acc.write(row_no, 4, trade_sub_type_name)
                trd_acc.write(row_no, 5, codes)
                trd_acc.write(row_no, 8, "FLAT")
                trd_acc.write(row_no, 9, charge)
                trd_acc.write(row_no, 10, uom_unit)
                trd_acc.write(row_no, 11, uom_from)
                trd_acc.write(row_no, 12, uom_to)

                row_no = row_no + 1
        else:

            trade_sub_type_name = localization_map.get(get_trade_localization_code(code)) or ""

            trd_acc.write(row_no, 0, row_no)
            trd_acc.write(row_no, 2, "PERMANENT")
            trd_acc.write(row_no, 4, trade_sub_type_name)
            trd_acc.write(row_no, 8, "FLAT")
            trd_acc.write(row_no, 5, code)

            row_no = row_no + 1

    for code, slabs in acc_map.items():
        if len(slabs) != 0:
            if len(slabs) > 1:
                slabs = sort_by_uom_from(slabs)
            for slab in slabs:
                id = slab["id"]
                accessory_category_code = slab["accessoryCategory"]
                charge = slab["rate"]
                uom_unit = slab["uom"]
                uom_from = slab["fromUom"]
                uom_to = slab["toUom"]

                accessories_name = localization_map.get(
                    get_accessories_localization_code(slab["accessoryCategory"])) or ""

                trd_acc.write(row_no, 0, row_no)
                trd_acc.write(row_no, 1, id)
                trd_acc.write(row_no, 2, "PERMANENT")
                trd_acc.write(row_no, 7, accessory_category_code)
                trd_acc.write(row_no, 6, accessories_name)
                trd_acc.write(row_no, 8, "FLAT")
                trd_acc.write(row_no, 9, charge)
                trd_acc.write(row_no, 10, uom_unit)
                trd_acc.write(row_no, 11, uom_from)
                trd_acc.write(row_no, 12, uom_to)
                row_no = row_no + 1
        else:

            accessories_name = localization_map.get(get_accessories_localization_code(code)) or ""
            trd_acc.write(row_no, 0, row_no)
            trd_acc.write(row_no, 2, "PERMANENT")

            trd_acc.write(row_no, 7, code)
            trd_acc.write(row_no, 6, accessories_name)
            trd_acc.write(row_no, 8, "FLAT")
            row_no = row_no + 1

    file_name = "{}_tl_billing_slab.xls".format(config.TENANT_ID)
    wk.save(file_name)
    print("\n", "XLSX file created with file name : {}".format(file_name))
    print(" PATH : {}/{}".format(dirname(__file__), file_name))


def main():
    auth_token = superuser_login()["access_token"]

    download_billing_slab(auth_token)


if __name__ == "__main__":
    main()
