import itertools

row = {}

source_headers = ["PropertyType", "UsageCategoryMajor", "UsageCategoryMinor", "UsageCategorySubMinor", "UsageCategoryDetail", "PropertySubType", "OwnershipCategory", "SubOwnershipCategory", "isPropertyMultiFloored", "FromPlotSize", "ToPlotSize", "OccupancyType", "FromFloor", "ToFloor", "Area 1", "Area 2", "Area 3", "arvPercent"]

desitination_headers = ["propertyType", "usageCategoryMajor", "usageCategoryMinor", "usageCategorySubMinor", "usageCategoryDetail", "propertySubType", "ownerShipCategory", "subOwnerShipCategory", "isPropertyMultiFloored", "fromPlotSize", "toPlotSize", "occupancyType", "fromFloor", "toFloor", "areaType", "unitRate", "unBuiltUnitRate", "arvPercent"]


review_headers = ["PropertyType", "UsageCategoryMajor", "UsageCategoryMinor", "UsageCategorySubMinor", "UsageCategoryDetail", "PropertySubType", "OwnershipCategory", "SubOwnershipCategory", "isPropertyMultiFloored", "FromPlotSize", "ToPlotSize", "OccupancyType", "FromFloor", "ToFloor", "areaType", "unitRate", "unBuiltUnitRate", "arvPercent"]

from common import *

dfs, wks = open_google_spreadsheet(
    "https://docs.google.com/spreadsheets/d/1Grd20oHLoC4B5DfuMY8Yud31w7uKY09gM22E2LbH3cs/edit?ts=5b7d3b2f#gid=0",
    "Category C")


dfs['Category C'].to_csv('slabs.csv', index=False, index_label=False)

import io
import csv
import copy
f = io.open("slabs.csv", encoding="utf-8")
c = csv.DictReader(f)

rows = []

for row in c:

    area1 = copy.deepcopy(row)
    area2 = copy.deepcopy(row)
    area3 = copy.deepcopy(row)

    area1["areaType"] = "AREA1"
    area2["areaType"] = "AREA2"
    area3["areaType"] = "AREA3"

    area1["unitRate"] = float(area1["Area 1"])
    area2["unitRate"] = float(area2["Area 2"])
    area3["unitRate"] = float(area3["Area 3"])

    area1["unBuiltUnitRate"] = float(area1["Area 1"]) * 0.5
    area2["unBuiltUnitRate"] = float(area2["Area 2"]) * 0.5
    area3["unBuiltUnitRate"] = float(area3["Area 3"]) * 0.5

    for area in [area1, area2, area3]:
        area.pop("Area 1")
        area.pop("Area 2")
        area.pop("Area 3")

    rows.extend([area1, area2, area3])

level1_rows = []
for row in rows:
    multi_data_keys = []
    combinations = []
    for key, value in row.items():
        if type(value) is str and "\n" in value:
            multi_data_keys.append(key)
            combinations.append(value.split("\n"))
        # elif value == "ALLE":
        #     multi_data_keys.append(key)
        #     combinations.append(["TEST1", "TEST2"])

    if not combinations or len(combinations) == 0:
        new_row = copy.deepcopy(row)
        level1_rows.append(new_row)
    else:
        for combo in itertools.product(*combinations):
            new_row = copy.deepcopy(row)
            for i, key in enumerate(multi_data_keys):
                new_row[key] = combo[i]

            level1_rows.append(new_row)


# For {PropertySubType= INDEPENDENTPROPERTY} generate slabs for empty land with rate = half of {FromFloor = -10 & ToFloor = -1}
#
# For {PropertySubType= INDEPENDENTPROPERTY} & { isPropertyMultiFloored = TRUE} generate slabs for {FromFloor = -10 & ToFloor = -1} with rate = half of {FromFloor = -10 & ToFloor = -1}
#
# For {PropertySubType= INDEPENDENTPROPERTY} & { isPropertyMultiFloored = TRUE} generate slabs for {FromFloor = 1 & ToFloor = 31} with rate = half of {FromFloor = -10 & ToFloor = -1}
#
# For {PropertySubType= SHAREDPROPERTY} & { isPropertyMultiFloored = TRUE} change slabs {FromFloor = 0 & ToFloor = 0} to {FromFloor = -10 & ToFloor = 31}
#
# For {PropertySubType= SHAREDPROPERTY} & remove { isPropertyMultiFloored = FALSE}
#
# For { OccupancyType = SELFOCCUPIED} generate { OccupancyType = UNOCCUPIED} with rate = half of { OccupancyType = SELFOCCUPIED}
#
# For { UsageCategoryDetail = Malls or MarriagePalace or Multiplex } all rates are same as { PropertySubType = INDEPENDENTPROPERTY} and { FromFloor = 0&ToFloor=0}

f = io.open("level1.csv", encoding="utf-8", mode="w")
c = csv.DictWriter(f, review_headers)
c.writeheader()
c.writerows(level1_rows)
f.close()


level2_rows = []

for row in level1_rows:
    if row["OccupancyType"] == "RENTED":
        if row["isPropertyMultiFloored"] == "TRUE" and row["FromFloor"]=="0" and row["ToFloor"] == "0":
            row["FromFloor"] = -10
            row["ToFloor"] = 31

        level2_rows.append(row)
        continue

    if row["PropertySubType"] == "SHAREDPROPERTY":

        if row["isPropertyMultiFloored"] == "FALSE":
            continue

        if row["isPropertyMultiFloored"] == "TRUE" and row["FromFloor"]=="0" and row["ToFloor"] == "0":
            row["FromFloor"] = -10
            row["ToFloor"] = 31
            row["unBuiltUnitRate"] = row["unitRate"]

    if row["PropertySubType"] == "INDEPENDENTPROPERTY" and row["isPropertyMultiFloored"] == "TRUE":
        lower_floors = copy.deepcopy(row)
        upper_floors = copy.deepcopy(row)

        lower_floors["FromFloor"] = -10
        lower_floors["ToFloor"] = -1
        lower_floors["unitRate"] = row["unitRate"] * 0.5
        lower_floors["unBuiltUnitRate"] = row["unitRate"] * 0.5 * 0.5

        upper_floors["FromFloor"] = 1
        upper_floors["ToFloor"] = 31
        upper_floors["unitRate"] = row["unitRate"] * 0.5
        upper_floors["unBuiltUnitRate"] = row["unitRate"] * 0.5 * 0.5

        level2_rows.extend([lower_floors, upper_floors])

    if row["PropertySubType"] == "INDEPENDENTPROPERTY" and row["UsageCategoryDetail"] == "MALLS":
        row["unBuiltUnitRate"] = row["unitRate"]

    if row["PropertySubType"] == "INDEPENDENTPROPERTY" and row["UsageCategorySubMinor"] in ("ENTERTAINMENT", "EVENTSPACE"):
        if row["UsageCategoryDetail"] in ("ALL", "MARRIAGEPALACE", "MULTIPLEX"):
            row["unBuiltUnitRate"] = row["unitRate"]

    level2_rows.append(row)

f = io.open("level2.csv", encoding="utf-8", mode="w")
c = csv.DictWriter(f, review_headers)
c.writeheader()
c.writerows(level2_rows)
f.close()


level3_rows = []
for row in level2_rows:
    if row["OccupancyType"] == "SELFOCCUPIED":
        unoccupied_row = copy.deepcopy(row)
        unoccupied_row["OccupancyType"] = "UNOCCUPIED"
        unoccupied_row["unitRate"] = row["unitRate"] * 0.5
        unoccupied_row["unBuiltUnitRate"] = row["unBuiltUnitRate"] * 0.5
        level3_rows.append(unoccupied_row)
    level3_rows.append(row)

# print(level3_rows)

f.close()

f = io.open("level3.csv", encoding="utf-8", mode="w")
c = csv.DictWriter(f, review_headers)
c.writeheader()
c.writerows(level3_rows)
f.close()

print("Created billing_slab_generated.csv")

# insert_query = """
# INSERT INTO public.eg_pt_billingslab_v2 (id, tenantid, propertytype, propertysubtype, usagecategorymajor, usagecategoryminor, usagecategorysubminor, usagecategorydetail, ownershipcategory, subownershipcategory, fromfloor, tofloor, areatype, occupancytype, fromplotsize, toplotsize, unitrate, createdby, createdtime, lastmodifiedby, lastmodifiedtime, ispropertymultifloored, unbuiltunitrate, arvpercent) VALUES;
# """
#
# tenant_id = "pb.nawanshahr"
#
# row_template = "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, '{}', )"