activate = False

tenants = ["nawanshahr", "sangrur"]
module = "PGR"
# module = "PT"

import json
from config import config

with open(config.CITY_MODULES_JSON, mode="r") as f:
    data = json.load(f)

found = False
for m in data["citymodule"]:
    if m["code"] == module:
        found = True
        break

if found:
    for tenant in tenants:
        tenant = "pb." + tenant.lower()
        found = False
        for i, et in enumerate(m["tenants"]):
            if et["code"] == tenant:
                found = True
                break

        if found and activate:
            print("tenant already active - " + tenant + " for module = " + module)
        elif not found and activate:
            print("Activating tenant - " + tenant + " for module = " + module)
            m["tenants"].append({"code": tenant})
        elif not found and not activate:
            print("tenant already deactivated - " + tenant + " for module = " + module)
        else:
            print("tenant deactivated - " + tenant + " for module = " + module)
            m["tenants"].remove(et)

    with open(config.CITY_MODULES_JSON, mode="w") as f:
        json.dump(data, f, indent=2)

else:
    print("Module not found - " + module)
