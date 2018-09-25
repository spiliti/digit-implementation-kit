import json
import os

from common import open_excel_file, get_sheet, get_column_index, fix_value
from config import config


def main():
    dfs = open_excel_file(config.SHEET)

    config.SHEET_BANKBRANCH = "Bank Branch"
    config.SHEET_BANKACCOUNT = "Bank Account"

    bankbranch = get_sheet(dfs, config.SHEET_BANKBRANCH)
    bankaccount = get_sheet(dfs, config.SHEET_BANKACCOUNT)

    config.COLUMN_BANKBRANCH_BRANCHCODE = "Branch Code*"
    config.COLUMN_BANKBRANCH_PHONE = "Phone"
    config.COLUMN_BANKBRANCH_CONTACTPERSON = "Contact Person"
    config.COLUMN_BANKACCOUNT_ACCOUNTNUMBER = "Account Number *"
    template = dict()
    template["__city__"] = config.CITY_NAME.lower()
    template["__contact__"] = fix_value(
        bankbranch.iloc[0][get_column_index(bankbranch, config.COLUMN_BANKBRANCH_PHONE)], default_nan="")
    template["__contact_person__"] = fix_value(
        bankbranch.iloc[0][get_column_index(bankbranch, config.COLUMN_BANKBRANCH_CONTACTPERSON)], default_nan="")
    template["__bankbranchcode__"] = fix_value(
        bankbranch.iloc[0][get_column_index(bankbranch, config.COLUMN_BANKBRANCH_BRANCHCODE)])
    template["__account_number__"] = fix_value(
        bankaccount.iloc[0][get_column_index(bankaccount, config.COLUMN_BANKACCOUNT_ACCOUNTNUMBER)])
    print(json.dumps(template, indent=2))

    response = os.getenv("ASSUME_YES", None) or input("Do you want to generate the SQL template (y/[n])?")

    if response.lower() == "y":
        with open("../sql/templates/PTGoLive.template.pgsql") as f:
            data = f.read()
            for key, value in template.items():
                data = data.replace(key, value)

            with open("../sql/output/PT/PTGoLive.{}.pgsql".format(config.CITY_NAME), mode="w") as w:
                w.write(data)
    else:
        print("Not generating sql template")

if __name__ == "__main__":
    main()
