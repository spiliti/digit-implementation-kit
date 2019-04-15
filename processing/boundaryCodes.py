import requests

tenant = 'pb.testing'

url = "https://raw.githubusercontent.com/egovernments/punjab-mdms-data/master/data/{}/egov-location/boundary-data.json".replace(
    "{}", tenant.replace(".", "/"))

response = requests.get(url)

boundary = response.json()['TenantBoundary']

if boundary[0]["hierarchyType"]["code"] == "REVENUE":
    boundary_data = boundary[0]["boundary"]
else:
    boundary_data = boundary[1]["boundary"]

for l1 in boundary_data["children"]:
    for l2 in l1["children"]:
        for value in l2["children"]:
            print(value['name'] + "," + value['code'])