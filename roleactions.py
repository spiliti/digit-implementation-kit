import json
import io
from config import config
import itertools
from jsonpath import jsonpath

actions = None
actions_map = None
role_actions = None


def load_role_data():
    global actions, role_actions

    with io.open(config.MDMS_ACTIONS_JSON) as f:
        actions = json.load(f)['actions-test']

    with io.open(config.MDMS_ROLEACTIONS_JSON) as f:
        role_actions = json.load(f)["roleactions"]


def save_role_data():
    pass


def add_role(actions, roles):
    if type(roles) is str:
        roles = [roles]

    if type(actions) is str:
        actions = [actions]

    for action, role in itertools.product(roles, actions):
        pass


data = """/tl-services/v1/_create, /tl-services/v1/_update, /tl-services/v1/_search, /tl-calculator/v1/_getbill,egov-mdms-service/v1/_search, hr-employee-v2/employees/_search, egov-location/location/v11/tenant/_search, user/_search, /citizen/_create, /profile/_update, /bill/_search, /receipts/_search,
/otp/v1/_validate, /user-otp/v1/_send"""


data_citizen = """
/tl-services/v1/_create, /tl-services/v1/_update, /tl-services/v1/_search , /transaction/v1/_create, /transaction/v1/_update, /transaction/v1/_search, /gateway/v1/_search, /tl-calculator/v1/_getbill,egov-mdms-service/v1/_search, hr-employee-v2/employees/_search, egov-location/location/v11/tenant/_search, /user/_search, /citizen/_create, /profile/_update, /bill/_search, /receipts/_search,
/otp/v1/_validate, /user-otp/v1/_send
"""

data_employee = """
/tl-services/v1/_create, /tl-services/v1/_update, /tl-services/v1/_search, /tl-calculator/v1/_getbill,egov-mdms-service/v1/_search, hr-employee-v2/employees/_search, egov-location/location/v11/tenant/_search, user/_search, /citizen/_create, /profile/_update, /bill/_search, /receipts/_search,
/otp/v1/_validate, /user-otp/v1/_send
"""

data = """
/tl-services/v1/_update, /tl-services/v1/_search, /tl-calculator/v1/_getbill
SUPERUSER - /tl-calculator/billingslab/_search, /tl-calculator/billingslab/_create, /tl-calculator/billingslab/_update,egov-mdms-service/v1/_search, hr-employee-v2/employees/_search, egov-location/location/v11/tenant/_search, user/_search, /citizen/_create, /profile/_update, /bill/_search, /receipts/_search,
/otp/v1/_validate, /user-otp/v1/_send
"""

data = """
/egov-workflow-v2/egov-wf/process/_transition,
/egov-workflow-v2/egov-wf/process/_search,
/egov-workflow-v2/egov-wf/businessservice/_create,
/egov-workflow-v2/egov-wf/businessservice/_update,
/egov-workflow-v2/egov-wf/businessservice/_search
"""

data = """
/egov-workflow-v2/egov-wf/businessservice/_search
"""


if __name__ == "__main__":
    load_role_data()

    BE_actions = jsonpath(actions, "$[?(@.enabled is False)]")
    UI_actions = jsonpath(actions, "$[?(@.enabled is True)]")
    # print (BE_actions)
    import re
    data = re.sub(r"[\s]+", "", data)


    matched = set()

    for url in data.split(","):
        found = False
        for action in BE_actions:
            if action['url'].lower().endswith(url.lower()):
                matched.add(action['id'])
                found = True
                break

        if not found:
            print("Url - " + url + " has no entry in MDMS")

    role_actions_mapped = jsonpath(role_actions, "$.[?(@.rolecode == '{}')]].actionid".format("CSR"))
    role_actions_mapped2 = jsonpath(role_actions, "$.[?(@.rolecode == '{}')]].actionid".format("GRO"))
    role_actions_mapped3 = jsonpath(role_actions, "$.[?(@.rolecode == '{}')]].actionid".format("DGRO"))
    role_actions_mapped4 = jsonpath(role_actions, "$.[?(@.rolecode == '{}')]].actionid".format("PGR-ADMIN"))
    common = (set(role_actions_mapped).intersection(role_actions_mapped2).intersection(role_actions_mapped3).intersection(role_actions_mapped4))
    for c in common:
        print(c, jsonpath(actions, "$[?(@.id == {})]".format(c)))

    exit(0)
    new_data = []
    for role in ["TL_DOC_VERIFIER", "TL_FIELD_INSPECTOR"]:
        role_actions_mapped = jsonpath(role_actions, "$.[?(@.rolecode == '{}')]].actionid".format(role))

        if role_actions_mapped:
            missing_ids = common - set(role_actions_mapped)
        else:
            missing_ids = common

        for id in missing_ids:
            new_data.append({
                "rolecode": role,
                "actionid": id,
                "actioncode": "",
                "tenantId": "pb"
            })

    print(json.dumps(new_data, indent=2))
    exit(0)


    roles = ["CITIZEN"]

    new_data = []

    for role in roles:
        role_actions_mapped = jsonpath(role_actions, "$.[?(@.rolecode == '{}')]].actionid".format(role))

        if role_actions_mapped:
            missing_ids = matched - set(role_actions_mapped)
        else:
            missing_ids = matched

        for id in missing_ids:
            new_data.append({
                "rolecode": role,
                "actionid": id,
                "actioncode": "",
                "tenantId": "pb"
            })

    print(json.dumps(new_data,indent=2))