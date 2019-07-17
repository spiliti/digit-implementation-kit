import xlrd
import requests
import xlwt
from xlwt import Workbook
from setupkit import *


def search_localization(tenant_id, auth_token, modules, locale):
    return api_call(auth_token, "/localization/messages/v1/_search",
                    {"tenantId": tenant_id, "modules": modules, "locale": locale})


def search_mdms_data(tenant_id, auth_token):
    return api_call(auth_token, "/egov-mdms-service/v1/_search", tenant_id, "MdmsCriteria", {
        "tenantId": "pb",
        "moduleDetails": [
            {
                "moduleName": "TradeLicense",
                "masterDetails": [
                    {
                        "name": "TradeType"
                    },
                    {
                        "name": "AccessoriesCategory"
                    }
                ]
            },
            {
                "moduleName": "common-masters",
                "masterDetails": [
                    {
                        "name": "UOM"
                    }
                ]
            }
        ]
    })
def uom_mdms_data(tenant_id, auth_token):
    uom_data = search_mdms_data(tenant_id, auth_token)["MdmsRes"]["common-masters"]["UOM"]
    uom_mdms_code = []
    for a in uom_data:
        prefix_uom_for_code = "COMMON_MASTER_UOM_"
        uom_code = prefix_uom_for_code + a["code"]
        uom_mdms_code.append(uom_code)
    return  uom_mdms_code

def acc_mdms_data(tenant_id, auth_token):
    trade_license_data = search_mdms_data(tenant_id, auth_token)["MdmsRes"]["TradeLicense"]["AccessoriesCategory"]
    trade_license_acc_code = []
    for b in trade_license_data:
        prefix_acc_for_code = "TRADELICENSE_ACCESSORIESCATEGORY_"
        trade_license = prefix_acc_for_code + b["code"]
        trade_license_acc_code.append(trade_license.replace('-', '_'))
    return trade_license_acc_code


def type_mdms_data(tenant_id, auth_token):
    trade_license_data_type = search_mdms_data(tenant_id, auth_token)["MdmsRes"]["TradeLicense"]["TradeType"]
    trade_type_code = []
    for c in trade_license_data_type:
        prefix_type_for_code = "TRADELICENSE_TRADETYPE_"
        trade_type = c["code"]
        trade_type = trade_type.replace('.', '-')
        trade_type = trade_type.replace('-', '_')
        trade_type_code.append(prefix_type_for_code + trade_type)
    return trade_type_code


def mapping_file(path):
    # path = ''
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)
    rows = []
    header = 0
    start = header + 1
    for j in range(start, sheet.nrows):
        current_row = {}
        rows.append(current_row)
        for i in range(sheet.ncols):
            current_row[sheet.cell(header, i).value] = sheet.cell_value(j, i)

    return rows


def mapping_file_sheet(path):
    # path = ''
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(1)
    sheet.cell_value(0, 0)
    row = []
    header = 0
    start = header + 1
    for j in range(start, sheet.nrows):
        current_row = {}
        row.append(current_row)
        for i in range(sheet.ncols):
            current_row[sheet.cell(header, i).value] = sheet.cell_value(j, i)

    return row


def localization_mapping(tenant_id, auth_token, locale):
    wb_write_tenant_data = xlwt.Workbook()
    write_sheet = wb_write_tenant_data.add_sheet('jenkins')

    write_sheet.write(0, 0, 'tenantId')
    write_sheet.write(0, 1, 'id')
    write_sheet.write(0, 2, 'licenseType')
    write_sheet.write(0, 3, 'structureType')
    write_sheet.write(0, 4, 'tradeType')
    write_sheet.write(0, 5, 'accessoryCategory')
    write_sheet.write(0, 6, 'type')
    write_sheet.write(0, 7, 'uom')
    write_sheet.write(0, 8, 'fromUom')
    write_sheet.write(0, 9, 'toUom')
    write_sheet.write(0, 10, 'rate')

    localization_common_data = search_localization(tenant_id, auth_token, 'rainmaker-common', locale)["messages"]
    localization_tl_data = search_localization(tenant_id, auth_token, 'rainmaker-tl', locale)["messages"]
    data = localization_common_data + localization_tl_data


    rows = mapping_file('/Users/deependra/Downloads/Trade_and_Accessories_final_sheet_nabha.xlsx')

    uom_mdms_codes=uom_mdms_data(tenant_id,auth_token)
    trade_license_acc_code= acc_mdms_data(tenant_id,auth_token)
    trade_type_code=type_mdms_data(tenant_id,auth_token)

    message_to_code_map_uom = {}
    message_to_code_map_acc = {}
    message_to_code_map_type = {}

    for d in data:
        for e in uom_mdms_codes:
            if d["code"] == e:
                message = d["message"]
                code = e
                message_to_code_map_uom[message] = code
                message_to_code_map_uom[code] = message
        for f in trade_license_acc_code:
            if d["code"] == f:
                message = d["message"]
                code = f
                message_to_code_map_acc[message] = code
                message_to_code_map_acc[code] = message
        for g in trade_type_code:
            if d["code"] == g:
                message = d["message"]
                code = g
                message_to_code_map_type[message] = code
                message_to_code_map_type[code] = message

    message_to_code_map = {}

    for m in data:
        code = m["code"]
        message = m["message"]
        message_to_code_map[message] = message_to_code_map.get(message, set())
        message_to_code_map[message].add(code)


    print(message_to_code_map[rows[1]["License Type"]])

    for i in range(len(rows)):
        for j in message_to_code_map_type:
            if rows[i]["Trade Sub-Type"] in message_to_code_map_type:
                # print(rows[i]["Trade Sub-Type"])
                # print(message_to_code_map_type.get(rows[i]["Trade Sub-Type"]))
                break

        tradetype=message_to_code_map_type.get(rows[i]["Trade Sub-Type"])


        messqge_to_code = message_to_code_map[rows[i]["License Type"]]
        license_type_col = prefix_replace(messqge_to_code, 'TRADELICENSE_LICENSETYPE_')


        messqge_to_code = message_to_code_map[rows[i]["Structure sub type"]]
        structure_type = prefix_replace(messqge_to_code, 'COMMON_MASTERS_STRUCTURETYPE_')
        print(i)

        k = i + 1
        write_sheet.write(k, 2, license_type_col)
        write_sheet.write(k, 3, structure_type)
        write_sheet.write(k, 4, tradetype)

    row = mapping_file_sheet('/Users/deependra/Downloads/Trade_and_Accessories_final_sheet_nabha.xlsx')

    for n in range(len(row)):
        for l in message_to_code_map_acc:
            if row[n]["Accessories Name"] in message_to_code_map_acc:
                # print(row[i]["Accessories Name"])
                # print(message_to_code_map_acc.get(row[i]["Accessories Name"]))
                break
        accessories_name=message_to_code_map_acc.get(row[n]["Accessories Name"])
        #print(accessories_name)
        k=k+1
        write_sheet.write(k, 2, license_type_col)
        write_sheet.write(k, 5, accessories_name)


    wb_write_tenant_data.save('xlwt new_data.xls')


def prefix_replace(set_of_code, prefix, first_string=""):
    for n in set_of_code:
        if n.startswith(prefix + first_string):
            return n.replace(prefix, "").replace("_", ".")

    return None


if __name__ == "__main__":
    auth_token = superuser_login()["access_token"]
    tenant_id = 'pb'
    locale = 'en_IN'

    localization_mapping(tenant_id, auth_token,locale)

