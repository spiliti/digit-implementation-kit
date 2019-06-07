from urllib.parse import urljoin, urlparse

import requests

from common import superuser_login
from config import config


def api_call(auth_token, url, params={}, data_key=None, data_value=None):
    url_api_call = urljoin(config.HOST, url)
    json_call = {}
    if auth_token:
        json_call["RequestInfo"] = {"authToken": auth_token}

    if data_key:
        json_call[data_key] = data_value

    return requests.post(url_api_call, params=params, json=json_call).json()


def BANKS_CREATE_DEFAULT(tenant_id, bank_code, bank_name, active):
    return {
        "code": bank_code,
        "name": bank_name,
        "description": "",
        "active": active,
        "type": "",
        "tenantId": tenant_id,
        "deleteReason": None
    }


def search_bank(tenant_id, auth_token, code=None):
    search_criteria = {"tenantId": tenant_id}

    if code:
        search_criteria["code"] = code
    return api_call(auth_token, "egf-master/banks/_search", search_criteria)


def upsert_bank(tenant_id, auth_token, bank_code, bank_name, active=True, **kwargs):
    banks = search_bank(tenant_id, auth_token, bank_code)["banks"]

    if len(banks) > 0:
        banks[0]["code"] = bank_code
        banks[0]["name"] = bank_name
        banks[0]["active"] = active
        banks[0].update(kwargs)

        return api_call(auth_token, "egf-master/banks/_update", {"tenantId": tenant_id}, "banks", banks)
    else:

        data = BANKS_CREATE_DEFAULT(tenant_id, bank_code, bank_name, active)
        data.update(kwargs)
        return api_call(auth_token, "egf-master/banks/_create", {"tenantId": tenant_id}, "banks", [data])


def BRANCHES_CREATE_DEFAULT(tenant_id, bank_code, bank_name, bank_city, bank_state, person_number, person_contact,
                            bank_id, active):
    return {
        "bank": {
            "id": bank_id,
            "code": bank_code,
            "name": bank_name,
            "description": None,
            "active": True,
            "type": None,
            "tenantId": tenant_id
        },
        "code": bank_code,
        "name": bank_name,
        "address": bank_city,
        "address2": None,
        "city": bank_city,
        "state": bank_state,
        "pincode": None,
        "phone": person_number,
        "fax": None,
        "contactPerson": person_contact,
        "active": active,
        "description": None,
        "micr": None,
        "tenantId": tenant_id,
        "deleteReason": None
    }


def search_bank_branches(tenant_id, auth_token, bank_code):
    search_criteria = {"tenantId": tenant_id}
    if bank_code:
        search_criteria["code"] = bank_code
    return api_call(auth_token, "egf-master/bankbranches/_search", search_criteria)


def upsert_bankbranches(tenant_id, auth_token, bank_code, bank_name, bank_city, bank_state, person_number,
                        person_contact, active=True, **kwargs):
    banks = search_bank(tenant_id, auth_token, bank_code)["banks"]
    if len(banks) > 0:
        bank_id = banks[0]["id"]
        bank_branches = search_bank_branches(tenant_id, auth_token, bank_code)["bankBranches"]
        if len(bank_branches) > 0:
            bank_branches[0]["code"] = bank_code
            bank_branches[0]["name"] = bank_name
            bank_branches[0]["city"] = bank_city
            bank_branches[0]["state"] = bank_state
            bank_branches[0]["phone"] = person_number
            bank_branches[0]["contactPerson"] = person_contact
            bank_branches[0]["active"] = active
            bank_branches[0].update(kwargs)
            # "Do to this thinks"
            # return api_call(auth_token, "egf-master/bankbranches/_update", {"tenantId": tenant_id}, "bankBranches",
            #                 bank_branches)
        else:
            data = BRANCHES_CREATE_DEFAULT(tenant_id, bank_code, bank_name, bank_city, bank_state, person_number,
                                           person_contact, bank_id, active)
            for bank in banks:
                if bank["code"] == bank_code:
                    data["bank"] = banks[0]
            data.update(kwargs)
            return api_call(auth_token, "egf-master/bankbranches/_create", {"tenantId": tenant_id}, "bankBranches",
                            [data])
    else:
        raise Exception("No banks does not exists for {}".format(tenant_id))


def search_account_code_purposes(tenant_id, auth_token, name=None):
    search_criteria = {"tenantId": tenant_id}
    if name:
        search_criteria["name"] = name
    return api_call(auth_token, "egf-master/accountcodepurposes/_search", search_criteria
                    )


def upsert_account_code_purposes(tenant_id, auth_token, name):
    code_purposes = search_account_code_purposes(tenant_id, auth_token, name)["accountCodePurposes"]

    if len(code_purposes) == 0:
        return api_call(auth_token, "egf-master/accountcodepurposes/_create", {"tenantId": tenant_id},
                        "accountCodePurposes",
                        [{
                            "name": name,
                            "tenantId": tenant_id}])


def CHART_OF_ACCOUNTS_DEFAULT(tenant_id, gl_code, name, type, chart_of_code_id=None, parent_id=None):
    data = {
        "glcode": gl_code,
        "name": name,
        "description": None,
        "isActiveForPosting": False,
        "type": type,
        "classification": 2,
        "functionRequired": False,
        "budgetCheckRequired": False,
        "majorCode": gl_code,
        "isSubLedger": False,
        "tenantId": tenant_id,
    }

    if chart_of_code_id:
        data["accountCodePurpose"] = {
            "id": chart_of_code_id,
            "tenantId": tenant_id
        }
    else:
        data["accountCodePurpose"] = None

    if parent_id:
        data["parentId"] = {
            "id": parent_id,
            "tenantId": tenant_id
        }
    else:
        data["parentId"] = None
    return data


def search_chart_of_accounts(tenant_id, auth_token, gl_code=None):
    search_criteria = {"tenantId": tenant_id}
    if gl_code:
        search_criteria["glcodes"] = gl_code
    return api_call(auth_token, "egf-master/chartofaccounts/_search", search_criteria)


def upsert_chart_of_accounts(tenant_id, auth_token, gl_code, name, type, chart_code_purpose_name, old_gl_code,
                             **kwargs):
    chart_of_account = search_chart_of_accounts(tenant_id, auth_token, gl_code)["chartOfAccounts"]

    if chart_code_purpose_name is not None:
        chart_code_purpose = search_account_code_purposes(tenant_id, auth_token, chart_code_purpose_name)[
            "accountCodePurposes"]
    else:
        chart_code_purpose = []

    if old_gl_code is not None:
        chart_of_old_account = search_chart_of_accounts(tenant_id, auth_token, old_gl_code)["chartOfAccounts"]
    else:
        chart_of_old_account = []

    parent_id = None
    chart_of_code_id = None

    if len(chart_code_purpose) == 1:
        chart_of_code_id = chart_code_purpose[0]["id"]

    if len(chart_of_old_account) == 1:
        parent_id = chart_of_old_account[0]["id"]

    if len(chart_of_account) > 0:
        chart_of_account[0]["name"] = name
        chart_of_account[0]["type"] = type
        chart_of_account[0].update(kwargs)
        # return api_call(auth_token, "egf-master/chartofaccounts/_update", {"tenantId": tenant_id}, "chartOfAccounts",
        #                 chart_of_account)
        # do to think

    else:
        data = CHART_OF_ACCOUNTS_DEFAULT(tenant_id, gl_code, name, type, chart_of_code_id, parent_id)
        data.update(kwargs)
        return api_call(auth_token, "egf-master/chartofaccounts/_create", {"tenantId": tenant_id}, "chartOfAccounts",
                        [data])


def FUNDS_DEFAULT(tenant_id, fund_name, fund_code, identifier):
    return {
        "name": fund_name,
        "code": fund_code,
        "identifier": identifier,
        "level": 0,
        "parent": None,
        "active": True,
        "tenantId": tenant_id,
        "deleteReason": None
    }


def search_funds(tenant_id, auth_token, code):
    search_criteria = {"tenantId": tenant_id}
    if code:
        search_criteria["code"] = code
    return api_call(auth_token, "egf-master/funds/_search", {"tenantId": tenant_id})


def upsert_funds(tenant_id, auth_token, fund_name, fund_code, identifier, **kwargs):
    fund = search_funds(tenant_id, auth_token, fund_code)["funds"]

    if len(fund) > 0:
        raise Exception("funds already exist for {}".format(tenant_id))
    else:
        data = FUNDS_DEFAULT(tenant_id, fund_name, fund_code, identifier)
        data.update(kwargs)
        return api_call(auth_token, "egf-master/funds/_create", {"tenantId": tenant_id}, "funds",
                        [data])


def ACCOUNT_CREATE_DEFAULT(tenant_id, account_number, account_type, gl_code, branch_id, chart_id, fund_id):
    return {
        "bankBranch": {
            "id": branch_id,
            "tenantId": tenant_id
        },
        "chartOfAccount": {
            "id": chart_id,
            "glcode": gl_code,
            "tenantId": tenant_id
        },
        "fund": {
            "id": fund_id,
            "tenantId": tenant_id
        },
        "accountNumber": account_number,
        "accountType": account_type,
        "description": None,
        "active": True,
        "payTo": None,
        "type": "RECEIPTS_PAYMENTS",
        "tenantId": tenant_id,
        "createdBy": None,
        "deleteReason": None

    }


def search_bank_accounts(tenant_id, auth_token):
    return api_call(auth_token, "egf-master/bankaccounts/_search", {"tenantId": tenant_id})


def upsert_bank_accounts(tenant_id, auth_token, account_number, account_type, bank_code, gl_code, fund_code,
                         **kwargs):
    bank_accounts = search_bank_accounts(tenant_id, auth_token)["bankAccounts"]

    bank_branches = search_bank_branches(tenant_id, auth_token, bank_code)["bankBranches"]

    accounts = search_chart_of_accounts(tenant_id, auth_token, gl_code)["chartOfAccounts"]

    funds = search_funds(tenant_id, auth_token)["funds"]

    branch_id = None
    chart_id = None
    fund_id = None

    if len(bank_branches) > 0:
        branch_id = bank_branches[0]["id"]
    else:
        raise Exception("bank branch not exist for bank {}".format(bank_code))

    if len(accounts) > 0:
        chart_id = accounts[0]["id"]
    else:
        raise Exception("chart of account not exist for gl_code{}".format(gl_code))

    if len(funds) > 0:
        fund_id = funds["id"]
    else:
        raise Exception(" funds not exist for {}".format(tenant_id))

    found = False

    for bank_account in bank_accounts:
        if bank_account["accountNumber"] == account_number:
            found = True
            break

    if not found:
        data = ACCOUNT_CREATE_DEFAULT(tenant_id, account_number, account_type, gl_code, branch_id, chart_id, fund_id)
        data.update(kwargs)
        return api_call(auth_token, "egf-master/bankaccounts/_create", {"tenantId": tenant_id}, "bankAccounts", [data])

    else:
        bank_accounts[0]["accountNumber"] = account_number
        bank_accounts[0]["accountType"] = account_type
        bank_accounts[0].update(kwargs)
        return api_call(auth_token, "egf-master/bankaccounts/_update", {"tenantId": tenant_id}, "bankAccounts",
                        bank_account)


def BUSINESS_SERVICES_DEFAULT(tenant_id, business_service):
    return {
        "tenantId": tenant_id,
        "businessService": business_service,
        "collectionModesNotAllowed": [],
        "partPaymentAllowed": True,
        "callBackForApportioning": False,
        "callBackApportionURL": None,
        "auditDetails": None
    }


def search_business_services(tenant_id, auth_token, business_service=None):
    search_criteria = {"tenantId": tenant_id}
    if business_service:
        search_criteria["businessService"] = business_service
    return api_call(auth_token, "billing-service/businessservices/_search",
                    search_criteria)


def upsert_business_services(tenant_id, auth_token, business_service, **kwargs):
    business_services = search_business_services(tenant_id, auth_token, business_service)["BusinessServiceDetails"]
    d = len(business_services)
    if len(business_services) == 0:
        data = BUSINESS_SERVICES_DEFAULT(tenant_id, business_service)
        data.update(kwargs)
        return api_call(auth_token, "billing-service/businessservices/_create",
                        {"tenantId": tenant_id, "businessService": business_service}, "BusinessServiceDetails", [data])
    else:
        raise Exception("business services is already exist for {}".format(tenant_id))


def TAX_PERIODS_DEFAULT(tenant_id, service, period_cycle, financial_year):
    return {
        "tenantId": tenant_id,
        "fromDate": 1396310400000,
        "toDate": 1427846399000,
        "periodCycle": period_cycle,
        "service": service,
        "code": "PTAN" + financial_year,
        "financialYear": financial_year
    }


def search_tax_periods(tenant_id, auth_token, service, financial_year=None):
    search_criteria = {"tenantId": tenant_id, "service": service}
    if financial_year:
        search_criteria["financialYear"] = financial_year
    return api_call(auth_token, "billing-service/taxperiods/_search",
                    search_criteria)


def upsert_tax_periods(tenant_id, auth_token, service, period_cycle, financial_year, **kwargs):
    tax_periods = search_tax_periods(tenant_id, auth_token, service, financial_year)["TaxPeriods"]

    if len(tax_periods) == 0:
        data = TAX_PERIODS_DEFAULT(tenant_id, service, period_cycle, financial_year)
        data.update(kwargs)
        return api_call(auth_token, "billing-service/taxperiods/_create", {"tenantId": tenant_id, "service": service},
                        "TaxPeriods", [data])


def TAX_HEADS_DEFAULT(tenant_id, service, category, name, code):
    return {
        "tenantId": tenant_id,
        "category": category,
        "service": service,
        "name": name,
        "code": code,
        "isDebit": False,
        "isActualDemand": True,
        "validFrom": 1143849600000,
        "validTill": 1554076799000,
        "order": 1
    }


def search_tax_heads(tenant_id, auth_token, service, code):
    search_criteria = {"tenantId": tenant_id}
    if service and code:
        search_criteria["service"] = service
        search_criteria["code"] = code
    return api_call(auth_token, "billing-service/taxheads/_search", search_criteria)


def upsert_tax_heads(tenant_id, auth_token, service, category, name, code, **kwargs):
    tax_heads = search_tax_heads(tenant_id, auth_token, service, code)["TaxHeadMasters"]
    if len(tax_heads) == 0:
        data = TAX_HEADS_DEFAULT(tenant_id, service, category, name, code)
        data.update(kwargs)
        return api_call(auth_token, "billing-service/taxheads/_create", {"tenantId": tenant_id, "service": service},
                        "TaxHeadMasters", [data])
    else:
        raise Exception("tax head alrady exist for {}".format(tenant_id))


def GL_CODE_MASTER_DEFAULT(tenant_id, tax_head, service, gl_code):
    return {
        "tenantId": tenant_id,
        "taxHead": tax_head,
        "service": service,
        "glCode": gl_code,
        "fromDate": 1143849600000,
        "toDate": 1554076799000
    }


def search_gl_code_masters(tenant_id, auth_token, service, gl_code=None):
    search_criteria = {"tenantId": tenant_id, "service": service}
    if gl_code:
        search_criteria["glCode"] = gl_code

    return api_call(auth_token, "billing-service/glcodemasters/_search", search_criteria
                    )


def upsert_gl_code_master(tenant_id, auth_token, tax_head, service, gl_code, **kwargs):
    gl_code_master = search_gl_code_masters(tenant_id, auth_token, service, gl_code)["GlCodeMasters"]
    if len(gl_code_master) == 0:
        data = GL_CODE_MASTER_DEFAULT(tenant_id, tax_head, service, gl_code)
        data.update(kwargs)
        return api_call(auth_token, "billing-service/glcodemasters/_create",
                        {"tenantId": tenant_id, "service": service}, "GlCodeMasters", [data])


def INSTRUMENT_TYPE_DEFAULT(tenant_id, name, description, active):
    import uuid

    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "active": active,
        "instrumentTypeProperties": [],
        "tenantId": tenant_id
    }


def search_instrument_types(tenant_id, auth_token, name=None):
    search_criteria = {"tenantId": tenant_id}
    if name:
        search_criteria["name"] = name
    return api_call(auth_token, "egf-instrument/instrumenttypes/_search", search_criteria)


def upsert_instrument_type(tenant_id, auth_token, name, description, active=True, **kwargs):
    instruments = search_instrument_types(tenant_id, auth_token, name)["instrumentTypes"]

    if len(instruments) > 0:
        instruments[0]["id"] = id
        instruments[0]["name"] = name
        instruments[0].update(kwargs)
        return api_call(auth_token, "egf-instrument/instrumenttypes/_update", {"tenantId": tenant_id},
                        "instrumentTypes",
                        instruments)
    else:
        data = INSTRUMENT_TYPE_DEFAULT(tenant_id, name, description, active)
        data.update(kwargs)
        return api_call(auth_token, "egf-instrument/instrumenttypes/_create", {"tenantId": tenant_id},
                        "instrumentTypes",
                        [data])


def INSTRUMENT_ACCOUNT_CODE_DEFAULT(tenant_id, instruments_type_id, name, gl_code):
    return {
        "instrumentType": {
            "id": instruments_type_id,
            "name": name
        },
        "accountCode": {
            "glcode": gl_code,
            "tenantId": tenant_id
        },
        "tenantId": tenant_id
    }


def search_instrument_account_codes(tenant_id, auth_token, name):
    search_criteria = {"tenantId": tenant_id}
    if name:
        search_criteria["name"] = name
    return api_call(auth_token, "egf-instrument/instrumentaccountcodes/_search", search_criteria)


def upsert_instrument_account_codes(tenant_id, auth_token, name, gl_code):
    instruments_account_code = search_instrument_account_codes(tenant_id, auth_token, name)["instrumentAccountCodes"]
    instruments = search_instrument_types(tenant_id, auth_token, name)["instrumentTypes"]
    if len(instruments) > 0:
        instruments_type_id = instruments[0]["id"]
    else:
        raise Exception("instrument type id is not exist for {}".format(name))
    if len(instruments_account_code) > 0:
        instruments_account_code["instrumentType"]["id"] = instruments_type_id
        instruments_account_code["instrumentType"]["name"] = name
        instruments_account_code["accountCode"]["glcode"] = gl_code
        instruments_account_code["accountCode"]["tenantId"] = tenant_id
        instruments_account_code["tenantId"] = tenant_id
        return api_call(auth_token, "egf-instrument/instrumentaccountcodes/_update", {"tenantId": tenant_id},
                        "instrumentAccountCodes", instruments_account_code)
    else:
        data = INSTRUMENT_ACCOUNT_CODE_DEFAULT(tenant_id, instruments_type_id, name, gl_code)
        return api_call(auth_token, "egf-instrument/instrumentaccountcodes/_create", {"tenantId": tenant_id},
                        "instrumentAccountCodes", [data])


def BUSINESS_CATEGORY_DEFAULT(tenant_id, name, code, active):
    return {
        "name": name,
        "code": code,
        "active": active,
        "tenantId": tenant_id,
        "version": None
    }


def search_business_category(tenant_id, name=None):
    search_criteria = {"tenantId": tenant_id}
    if name:
        search_criteria["name"] = name
    return api_call(auth_token, "egov-common-masters/businessCategory/_search", search_criteria)


def upsert_business_category(tenant_id, auth_token, name, code, active=True, **kwargs):
    business_category = search_business_category(tenant_id, name)["BusinessCategory"]

    if len(business_category) > 0:
        business_category[0]["name"] = name
        business_category[0]["code"] = code
        business_category[0].update(kwargs)
        return api_call(auth_token, "egov-common-masters/businessCategory/_update", {"tenantId": tenant_id},
                        "BusinessCategory", business_category)
    else:
        data = BUSINESS_CATEGORY_DEFAULT(tenant_id, name, code, active)
        data.update(kwargs)
        return api_call(auth_token, "egov-common-masters/businessCategory/_create", {"tenantId": tenant_id},
                        "BusinessCategory", [data])


def BUSINESS_DETAILS_DEFAULT(tenant_id, name, url, type, code, fund_code, category_id, function, depart):
    return {
        "name": name,
        "tenantId": tenant_id,
        "active": True,
        "businessUrl": url,
        "code": code,
        "businesstype": type,
        "fund": fund_code,
        "businessCategory": category_id,
        "function": function,
        "isVoucherApproved": False,
        "department": depart,
        "voucherCreation": False,
        "fundSource": "Online",
        "ordernumber": 1
    }


def search_business_details(tenant_id, code):
    search_criteria = {"tenantId": tenant_id}
    if code:
        # search_criteria["name"] =
        search_criteria["businessDetailsCodes"] = code
    return api_call(auth_token, "egov-common-masters/businessDetails/_search", search_criteria)


def upsert_business_details(tenant_id, auth_token, name, code, url, type, fund_code, function, depart, **kwargs):
    business_details = search_business_details(tenant_id, code)["BusinessDetails"]
    business_category = search_business_category(tenant_id, name)["BusinessCategory"]

    category_id = None
    if len(business_category) > 0:
        category_id = business_category[0]["id"]
    else:
        raise Exception(" business category is not exist  for {}".format(code))

    if len(business_details) > 0:
        business_details[0]["name"] = name
        business_details[0]["code"] = code
        business_details[0]["businessurl"] = url
        business_details[0]["businesstype"] = type
        business_details[0]["fund"] = fund_code
        business_details[0]["function"] = function
        business_details[0]["department"] = depart
        business_details[0].update(kwargs)
        return api_call(auth_token, "egov-common-masters/businessDetails/_update", {"tenantId": tenant_id},
                        "BusinessDetails", business_details)
    else:
        data = BUSINESS_DETAILS_DEFAULT(tenant_id, name, url, type, code, fund_code, category_id,
                                        function, depart)
        data.update(kwargs)
        return api_call(auth_token, "egov-common-masters/businessDetails/_create", {"tenantId": tenant_id},
                        "BusinessDetails", [data])


if __name__ == "__main__":
    auth_token = superuser_login()["access_token"]
    tenant_id = "pb.zirakpur"
    # print(search_bank("pb.zirakpur", auth_token))Cash-Cash In Transit
    # print(search_bank_branches(tenant_id, auth_token, 'AXIS'))
    # upsert_bank(tenant_id, auth_token, 'AXIS', 'AXIS BANK')
    # print(upsert_bankbranches(tenant_id, auth_token, 'AXIS', 'AXIS_BANK', 'zirakpur', 'Punjab', '9876543212', 'deep'))
    # print(upsert_account_code_purposes(tenant_id,auth_token, 'Cheque In Hand'))
    # print(upsert_account_code_purposes(tenant_id,auth_token, 'Demand Draft In Hand'))
    # print(upsert_account_code_purposes(tenant_id,auth_token, 'Online'))
    # print(upsert_account_code_purposes(tenant_id,auth_token, 'Cash In Hand'))
    # print(upsert_chart_of_accounts(tenant_id, auth_token, "1", "Income", "I", None, None))
    # print(upsert_chart_of_accounts(tenant_id,auth_token,'4501003','Cash-Cash ',"A","Cash In Hand","4501001"))
    # print(search_chart_of_accounts(tenant_id,auth_token,'4'))
    # print(upsert_chart_of_accounts(tenant_id, auth_token, '4', 'Assets', "A",None, None))
    # print(upsert_chart_of_accounts(tenant_id,auth_token,'450','Cash and Bank balance',"A",None,"4"))
    # print(upsert_chart_of_accounts(tenant_id,auth_token,'45010','Cash-Cash',"A",None,"450"))
    # #print(upsert_chart_of_accounts(tenant_id,auth_token,'4501056','Cash-Cheques-in-hand',"A","Cheque In Hand","45010"))
    # print(upsert_instrument_type(tenant_id,auth_token,'Cash',"Instrument for Cash payments"))
    # print(upsert_instrument_type(tenant_id,auth_token,'Online',"Instrument for Online payments"))
    # print(upsert_instrument_type(tenant_id,auth_token,'BankChallan',"Instrument for BankChallan payments"))
    # print(upsert_instrument_type(tenant_id,auth_token,'DD',"Instrument for Demand Draft payments"))
    # print(upsert_tax_heads(tenant_id,auth_token,'PT','PENALTYES','Pt adhoc penalty','PT_ADHOC_PENALTY'))
    # print(upsert_chart_of_accounts(tenant_id, auth_token, '4501051', 'Cash-Cheques-in',"A", "Cheque In Hand",  "45010"))
    # print(search_tax_heads(tenant_id,auth_token,'PT'))
    # print(upsert_business_details(tenant_id,auth_token,'Citizen Services','CS',"/receipts/receipt-create.action","BILLBASED","01","909100","AS"))
    print(upsert_tax_periods(tenant_id, auth_token, 'PT', "annual", "2019-20"))
