import xlrd as xlrd
import xlwt
import os
#from directory_name_list import present_in_active_ulb_list


def create_trade_n_accessory_data(tenant_id, trade_n_accessory_file_path,
                                  template_file_path='template.xlsx',
                                  destination_path='.'):
    wb_read_template = xlrd.open_workbook(template_file_path)
    read_template_sheet = wb_read_template.sheet_by_index(0)

    wb_read_trade_n_accessory = xlrd.open_workbook(trade_n_accessory_file_path)
    read_trade_sheet = wb_read_trade_n_accessory.sheet_by_index(0)
    read_accessory_sheet = wb_read_trade_n_accessory.sheet_by_index(1)

    wb_write_tenant_data = xlwt.Workbook()
    write_sheet = wb_write_tenant_data.add_sheet(tenant_id)

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

    for row_no in range(1, 274):  # Read all the value from the template file and write it to the new file
        write_sheet.write(row_no, 0, tenant_id)
        for col_no in range(2, 7):
            if read_template_sheet.cell_value(row_no, col_no) != '':
                write_sheet.write(row_no, col_no, read_template_sheet.cell_value(row_no, col_no))

    for trade_row_no in range(1, 180):  # Read all the charge from the trade sheet and write it
        print(trade_row_no)
        write_sheet.write(trade_row_no, 10, read_trade_sheet.cell_value(trade_row_no, 7))

    for accessory_row_no in range(1, 95):  # Read charge,uom unit,from,to from the accessories sheet and write it
        charge = read_accessory_sheet.cell_value(accessory_row_no, 2)
        uom_unit = read_accessory_sheet.cell_value(accessory_row_no, 3)
        uom_from = read_accessory_sheet.cell_value(accessory_row_no, 4)
        uom_to = read_accessory_sheet.cell_value(accessory_row_no, 5)

        if uom_unit == 'H.P.':
            uom_unit = 'HP'
        if uom_unit == 'NA':
            uom_unit = ''
        if uom_from == 'NA':
            uom_from = ''
        if uom_to == 'NA':
            uom_to = ''
        elif uom_to == 'Infinite':
            uom_to = 'Infinity'

        write_sheet.write(179 + accessory_row_no, 7, uom_unit)
        write_sheet.write(179 + accessory_row_no, 8, uom_from)
        write_sheet.write(179 + accessory_row_no, 9, uom_to)
        write_sheet.write(179 + accessory_row_no, 10, charge)

    file_name = tenant_id + '.processed.xls'
    destination_file_path = destination_path / file_name

    wb_write_tenant_data.save(destination_file_path)


get_tenant_id = lambda ulb_name: 'pb.' + ulb_name.lower().replace(' ', '')


def get_all_xls_file_path_n_create_data(base_dir="/home/egov/Desktop/ULB wise Trade List with Charges"):
    # base dir contains all ULB folders
    dir_ulb_list = os.listdir(base_dir)
    # listing all the ulb directory inside the base directory
    for ulb_name in dir_ulb_list:
        # present = present_in_active_ulb_list(ulb_name)
        present = True
        # for each ulb directory we are checking if that ulb is in active ulb list
        if present:
            xls_file_path = os.listdir(base_dir + '/' + ulb_name)
            # listing all the file inside each ulb folder
            tenant_id = get_tenant_id(ulb_name)
            ulb_xls_file = base_dir + '/' + ulb_name + '/' + xls_file_path[0]
            create_trade_n_accessory_data(tenant_id, ulb_xls_file)


def process_tenant_id_list_and_create_data(ulb_list, base_file_path):
    for ulb in ulb_list:
        create_trade_n_accessory_data(ulb, base_file_path + '/' + ulb + '.xlsx')


def delta_create_data(list, dest_path, base_dir="/home/egov/Desktop/ULB wise Trade List with Charges"):
    for ulb_name in list:
        print("ULB NAME :", ulb_name)
        present = present_in_active_ulb_list(ulb_name)
        # for each ulb directory we are checking if that ulb is in active ulb list
        if present:
            xls_file_path = os.listdir(base_dir + '/' + ulb_name)
            # listing all the file inside each ulb folder
            print("XLSPATH: ", xls_file_path)
            tenant_id = get_tenant_id(ulb_name)
            ulb_xls_file = base_dir + '/' + ulb_name + '/' + xls_file_path[0]
            create_trade_n_accessory_data(tenant_id=tenant_id, trade_n_accessory_file_path=ulb_xls_file,
                                          destination_path=dest_path)


