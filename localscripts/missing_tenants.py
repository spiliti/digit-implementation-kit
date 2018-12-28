import json
from config import config

module = "PT"

with open(config.TENANT_JSON, mode="r") as f:
    tenants_data = json.load(f)

tenant_codes = set()
for tenant in tenants_data["tenants"]:
    if tenant["code"] in ("pb.testing", "pb.punjab"):
        continue
    tenant_codes.add(tenant["code"])

with open(config.CITY_MODULES_JSON, mode="r") as f:
    data = json.load(f)

found = False
for m in data["citymodule"]:
    if m["code"] == module:
        found = True
        break

activated_tenants = set()
total_tenants = set()

if found:
    for i, et in enumerate(m["tenants"]):
        activated_tenants.add(et["code"])

    print("Missing tenants", module, len((tenant_codes - activated_tenants)))

    for code in (tenant_codes - activated_tenants):
        print(code)

else:
    print("Module not found - " + module)
