import requests
from xlwt import Workbook, Worksheet
import xlrd
import xlwt
from setupkit import *
from common import open_excel_file, get_sheet, get_column_index


def search_tl_billing_slab(auth_token):
    tenant_id = "pb.testing"
    return api_call(auth_token, "/tl-calculator/billingslab/_search", {"tenantId": tenant_id})


def search_localization(auth_token):
    tenant_id = "pb"
    modules = "rainmaker-tl"
    locale = "en_IN"
    return api_call(auth_token, "/localization/messages/v1/_search",
                    {"tenantId": tenant_id, "modules": modules, "locale": locale})


def get_billing_slab_localization(auth_token):
    localization_data = search_localization(auth_token)["messages"]
    code_to_message_map = {}
    for loc in localization_data:
        if "TRADELICENSE_TRADETYPE" in loc["code"]:
            code_to_message_map[loc["code"]] = loc["message"]
        elif "TRADELICENSE_ACCESSORIESCATEGORY" in loc["code"]:
            code_to_message_map[loc["code"]] = loc["message"]

    return code_to_message_map


def get_trade_code(tradetype):
    return "TRADELICENSE_TRADETYPE_" + tradetype.replace('.', '_').replace('-', '_')

def get_trade_acc_code(tradetype):
    return "TRADELICENSE_ACCESSORIESCATEGORY_" + tradetype.replace('.', '_').replace('-', '_')

def download_billing_slab(config_function, auth_token):
    wk = xlwt.Workbook()
    trades: Worksheet = wk.add_sheet("Trades")
    accessories: Worksheet = wk.add_sheet("Accessories items")

    for i, col in enumerate(
            ["S.N.","License type", "Structure Type", "Structure sub type", "Trade Category", "Trade Type",
             "Trade Sub-TypeCode", "Trade Sub-Type",
             "Charge", "UOM Unit", "UOM From", "UOM To"]):
        trades.write(0, i, col)

    for i, col in enumerate(
            ["S.N.","Accessories code" ,"Accessories Name"
             "Charge", "UOM Unit", "UOM From", "UOM To"]):
        accessories.write(0, i, col)

    billing_slabs = search_tl_billing_slab(auth_token)["billingSlab"]

    localization_map = get_billing_slab_localization(auth_token)

    row_trade = 1
    row_acc=1

    # print(billing_slabs)
    for billing_slab in billing_slabs:
        if billing_slab["tradeType"] is not None:
            licence_type = billing_slab["licenseType"]
            structure_type, structure_sub_type = billing_slab["structureType"].split('.')
            trade_category, trade_type, trade_sub_type_code = billing_slab["tradeType"].split('.')
            charge = billing_slab["rate"]
            uom_unit = billing_slab["uom"]
            uom_from = billing_slab["fromUom"]
            uom_to = billing_slab["toUom"]
            trade_type_code=get_trade_code(billing_slab["tradeType"])



            trade_sub_type_name = localization_map[trade_type_code]


            trades.write(row_trade, 0, row_trade)
            trades.write(row_trade, 1, licence_type)
            trades.write(row_trade, 2, structure_type)
            trades.write(row_trade, 3, structure_sub_type)
            trades.write(row_trade, 4, trade_category)
            trades.write(row_trade, 5, trade_type)
            trades.write(row_trade, 6, trade_sub_type_code)
            trades.write(row_trade, 7, trade_sub_type_name)
            trades.write(row_trade, 8, charge)
            trades.write(row_trade, 9, uom_unit)
            trades.write(row_trade, 10, uom_from)
            trades.write(row_trade, 11, uom_to)
            row_trade = row_trade + 1

        if billing_slab["accessoryCategory"] is not None:
            accessory_category_code= billing_slab["accessoryCategory"]
            charge = billing_slab["rate"]
            uom_unit = billing_slab["uom"]
            uom_from = billing_slab["fromUom"]
            uom_to = billing_slab["toUom"]

            accessories_name = localization_map[get_trade_acc_code(billing_slab["accessoryCategory"])]

            accessories.write(row_acc, 0, row_acc)
            accessories.write(row_acc, 2, accessories_name)
            accessories.write(row_acc, 1, accessory_category_code)
            accessories.write(row_acc, 3, charge)
            accessories.write(row_acc, 4, uom_unit)
            accessories.write(row_acc, 5, uom_from)
            accessories.write(row_acc, 6, uom_to)
            row_acc = row_acc + 1

    file_name = "tl_billing_slab.xls"
    wk.save(file_name)


from config import load_tl_billing_slab_download_config


def main():
    auth_token = superuser_login()["access_token"]

    download_billing_slab(load_tl_billing_slab_download_config, auth_token)


if __name__ == "__main__":
    main()
