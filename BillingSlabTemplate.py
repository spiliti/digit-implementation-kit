import xlrd
import requests
import xlwt
from xlwt import Workbook
from setupkit import *


def search_localization(tenant_id, auth_token, modules, locale):
    return api_call(auth_token, "/localization/messages/v1/_search",
                    {"tenantId": tenant_id, "modules": modules, "locale": locale})


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
    data1 = search_localization(tenant_id, auth_token, 'rainmaker-common', locale)["messages"]
    data2 = search_localization(tenant_id, auth_token, 'rainmaker-tl', locale)["messages"]

    data = data1 + data2
    message_to_code_map = {}

    for m in data:
        code = m["code"]
        message = m["message"]
        message_to_code_map[message] = message_to_code_map.get(message, set())
        message_to_code_map[message].add(code)
    rows = mapping_file('/Users/deependra/Downloads/newer_TL_rade_and_Accessories_Badhni_Kalan_new.xlsx')

    for i in range(len(rows)):
        messqge_to_code = message_to_code_map[rows[i]["License Type"]]
        license_type_col = prefix_replace(messqge_to_code, 'TRADELICENSE_LICENSETYPE_')

        messqge_to_code = message_to_code_map[rows[i]["Structure sub type"]]
        structure_type = prefix_replace(messqge_to_code, 'COMMON_MASTERS_STRUCTURETYPE_')

        if rows[i]["Trade Category"] == 'Service':
            rows[i]["Trade Category"] = 'Services'
        messqge_to_code = message_to_code_map[rows[i]["Trade Category"]]
        trade_category = prefix_replace(messqge_to_code, 'TRADELICENSE_TRADETYPE_')

        if rows[i]["Trade Type"] == 'Goods Based Service':
            rows[i]["Trade Type"] = 'Goods Based Services'
        if rows[i]["Trade Type"] == 'Non Goods Based Service':
            rows[i]["Trade Type"] = 'Non Goods Based Services'
        messqge_to_code = message_to_code_map[rows[i]["Trade Type"]]
        trade_types = prefix_replace(messqge_to_code, 'TRADELICENSE_TRADETYPE_')
        trade_category_and_type = trade_category + '_' + trade_types

        messqge_to_code = message_to_code_map[rows[i]["Trade Sub-Type"]]
        trade_sub_types = prefix_replace(messqge_to_code, 'TRADELICENSE_TRADETYPE_', trade_category_and_type)

        trade_sub_types = trade_sub_types.replace('.', '-')
        trade_sub_types = trade_sub_types.replace('-', '.', 2)

        j = i + 1
        write_sheet.write(j, 2, license_type_col)
        write_sheet.write(j, 3, structure_type)
        write_sheet.write(j, 4, trade_sub_types)

    row = mapping_file_sheet('/Users/deependra/Downloads/newer_TL_rade_and_Accessories_Badhni_Kalan_new.xlsx')

    for i in range(len(row)):
        messqge_to_code = message_to_code_map[row[i]["Accessories Name"]]
        accessories_name = prefix_replace(messqge_to_code, 'TRADELICENSE_ACCESSORIESCATEGORY_')
        accessories_name = accessories_name.replace('.', '-')
        k = len(rows) + i + 1
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

    localization_mapping(tenant_id, auth_token, locale)
