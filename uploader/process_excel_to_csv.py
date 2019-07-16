import xlrd
import csv

file = ""
with xlrd.open_workbook(file) as wb:
    total = wb.nsheets

    for i in range(0, total):
        sh = wb.sheet_by_index(i)  # or wb.sheet_by_name('name_of_the_sheet_here')
        with open(file + ".{}.csv".format(i), 'w') as f:   # open('a_file.csv', 'w', newline="") for python 3
            c = csv.writer(f)
            for r in range(sh.nrows):
                c.writerow(sh.row_values(r))