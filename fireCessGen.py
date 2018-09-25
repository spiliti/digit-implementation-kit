import json

from config import config
import os

def main():
    firecess_json = config.MDMS_LOCATION / config.CITY_NAME.lower() / "PropertyTax" / "FireCess.json"
    os.makedirs(config.MDMS_LOCATION / config.CITY_NAME.lower() / "PropertyTax", exist_ok= True)

    if os.path.isfile(firecess_json):
        print("File already exists")
    else:
        data = {
            "tenantId": config.TENANT_ID,
            "moduleName": "PropertyTax",
            "FireCess": [
                {
                    "rate": 0,
                    "minAmount": None,
                    "flatAmount": None,
                    "maxAmount": None,
                    "fromFY": "2014-15",
                    "dynamicFirecess": False,
                    "dynamicRates": {
                        "firecess_inflammable": 10,
                        "firecess_building_height": 2,
                        "firecess_category_major": 5
                    }
                }
            ]
        }
        print(json.dumps(data, indent=2))
        response = os.getenv("ASSUME_YES", None) or input("Do you want to append the data in repo (y/[n])?")

        if response.lower() == "y":

            with open(firecess_json, "w") as f:
                f.write(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()