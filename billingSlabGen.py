def get_slab_template():
    return {
        "RequestInfo": {
            "authToken": ""
        },
        "BillingSlab": [
            {
                "tenantId": "",
                "propertyType": "",
                "propertySubType": "",
                "usageCategoryMajor": "",
                "usageCategoryMinor": "",
                "usageCategorySubMinor": "",
                "usageCategoryDetail": "",
                "ownerShipCategory": "",
                "subOwnerShipCategory": "",
                "areaType": "",
                "fromPlotSize": -100,
                "toPlotSize": -100,
                "occupancyType": "",
                "fromFloor": -100,
                "toFloor": -100,
                "unitRate": -100,
                "isPropertyMultiFloored": False,
                "unBuiltUnitRate": -100,
                "arvPercent": -100
            }
        ]
    }


from common import *

access_token = login_egov("001", "9872129999", "pb.amritsar")["access_token"]
print(access_token)

dfs, wks = open_google_spreadsheet(
    "https://docs.google.com/spreadsheets/d/1uSuV0azrEVlDj2422Gd1IxMjFDeu55lCHOj2ListV6U/edit?ts=5b7168d7#gid=1486766778",
    "Billing slab_test")

tenant_id = 'pb.nawanshahr'
sheet = get_sheet(dfs, "Billing slab_test")
wk = wks.worksheet("Billing slab_test")

template = get_slab_template()

indexes = {}
for field in template["BillingSlab"][0].keys():
    indexes[field] = get_column_index(sheet, field)

indexes["Created"] = get_column_index(sheet, "Created")

status = []


def process_row(row):
    global status
    try:
        # print(row)
        data = get_slab_template()
        data["BillingSlab"][0]["tenantId"] = tenant_id
        data["RequestInfo"]["authToken"] = access_token
        created = row[indexes["Created"]]

        if created in ["Existing", "Created"]:
            return

        for field in data["BillingSlab"][0].keys():
            if indexes[field] is not None:
                val = row[indexes[field]]

                if field == "fromPlotSize" and str(val) == "ALL":
                    val = 0
                elif field == "toPlotSize" and str(val) == "ALL":
                    val = "+Infinity"
                elif field == "isPropertyMultiFloored":
                    val = val.lower()

                data["BillingSlab"][0][field] = val
        import requests
        res = requests.post(URL_BILLING_SLAB_CREATE, json=data)
        # print(json.dumps(data, indent=2))

        if res.status_code == 400 and res.json()["Errors"][0]["code"] == "EG_PT_BILLING_SLAB_DUPLICATE":
            print(str(row.name) + ", Billing slab already created")
            status.append(str(row.name + 2) + ",Existing")
        elif res.status_code != 201:
            print("-----Failed Request-----------")
            print(res.text)
            print(json.dumps(data, indent=2))
            print("------------------------------")
            status.append(str(row.name + 2) + ",Failed," + res.json()["Errors"][0]["message"])
            # wk.update_acell('T' + str(row.name + 2), "Failed")
            # wk.update_acell('U' + str(row.name + 2), res.json()["Errors"][0]["message"])
        else:
            # wk.update_acell('T' + str(row.name + 2), "Created")
            status.append(str(row.name + 2) + ",Created")
            print(str(row.name) + ", created billing slab successfully")

    except Exception as ex:
        print(ex)


sheet[1880:].apply(process_row, axis=1)
print("\n".join(status))
