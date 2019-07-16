import copy

from common import search_receipt, search_property, search_demand, update_demand, generate_bill, create_receipt, \
    update_property, superuser_login
from uploader.PropertyTaxDBProcess import update_db_record


def create_manual_receipt_collection(auth_token, tenant_id, property_id, assessment_year, paid_by,
                                     payment_amount_map: dict
                                     , g8_receiptnumber, g8_receiptdate, total_amount_paid, payment_type="Cash"):
    properties = search_property(auth_token, tenant_id, property_id)
    properties = properties["Properties"]

    if not len(properties):
        raise Exception("Property {} not found".format(property_id))

    consumer_codes = []

    for pd in properties[0]["propertyDetails"]:
        if pd["financialYear"] == assessment_year:
            consumer_codes.append(property_id + ":" + pd["assessmentNumber"])

    if consumer_codes:
        receipts = search_receipt(auth_token, tenantId=tenant_id, businessCode="PT",
                                  consumerCode=",".join(consumer_codes))["Receipt"]

        if len(receipts) > 0:
            raise Exception(
                "Payment has already been collected for {}/{}/{}"
                    .format(property_id, assessment_year, receipts[0]["receiptNumber"]))

        latest_consumer_code = consumer_codes[-1]
    else:
        new_assessment_property = copy.deepcopy(properties)
        new_assessment_property[0]["propertyDetails"] = new_assessment_property[0]["propertyDetails"][:1]
        new_assessment_property[0]["propertyDetails"][0]["financialYear"] = assessment_year
        new_property = update_property(auth_token, tenant_id, new_assessment_property)

        if "Errors" in new_property:
            raise Exception(new_property["Errors"][0]["message"])
        return create_manual_receipt_collection(auth_token, tenant_id, property_id, assessment_year, paid_by,
                                                payment_amount_map, g8_receiptnumber, g8_receiptdate, total_amount_paid,
                                                payment_type)

    demand = search_demand(auth_token, tenant_id, latest_consumer_code, "PT")["Demands"]
    demand_id = demand[0]["id"]

    for demand_detail in demand[0]["demandDetails"]:
        if demand_detail["taxHeadMasterCode"] in payment_amount_map:
            demand_detail["taxAmount"] = payment_amount_map[demand_detail["taxHeadMasterCode"]]
        else:
            demand_detail["taxAmount"] = 0

    update_demand(auth_token, demand)
    bill = generate_bill(auth_token, tenant_id, demand_id, latest_consumer_code, "PT")
    bill = bill["Bill"]

    bill_copy = copy.deepcopy(bill)

    amount_paid = bill[0]["taxAndPayments"][0]["taxAmount"]

    if amount_paid != total_amount_paid:
        raise Exception("Total paid calculated and actual is different. Calculated={} and Actual={}".format(amount_paid,
                                                                                                            total_amount_paid))

    receipt_request = [{
        "Bill": bill_copy,
        "instrument": {
            "transactionNumber": None,
            "transactionDate": None,  # in Date format DD-MM-YYYY
            "transactionDateInput": "",
            "payee": paid_by,
            "ifscCode": "",
            "instrumentType": {
                "name": payment_type
            },
            "tenantId": tenant_id,
            "amount": amount_paid
        },
        "tenantId": tenant_id
    }]

    bill_copy[0]["paidBy"] = paid_by
    bd = bill_copy[0]["billDetails"][0]
    bd["collectionType"] = "COUNTER"
    bd["manualReceiptNumber"] = g8_receiptnumber
    bd["manualReceiptDate"] = g8_receiptdate
    bill_copy[0]["taxAndPayments"][0]["amountPaid"] = amount_paid

    receipt_response = create_receipt(auth_token, tenant_id, receipt_request)
    return receipt_request, receipt_response


amounts = {
    "PT_ADHOC_REBATE": 0,
    "PT_ADVANCE_CARRYFORWARD": 0,
    "PT_OWNER_EXEMPTION": 0,
    "PT_TIME_REBATE": 225,
    "PT_UNIT_USAGE_EXEMPTION": 0,
    "PT_ADHOC_PENALTY": 0,
    "PT_TAX": 2250,
    "PT_FIRE_CESS": 113,
    "PT_CANCER_CESS": 0,
    "PT_TIME_PENALTY": 0,
    "PT_TIME_INTEREST": 0
}


def to_epoch(date_time):
    import time
    try:
        return int(time.mktime(time.strptime(date_time, "%d/%m/%Y")))
    except:
        return int(time.mktime(time.strptime(date_time, "%d/%m/%y")))


if __name__ == "__main__":
    auth_token = superuser_login()["access_token"]
    # print(create_manual_receipt_collection(auth_token, "pb.testing", "PT-1012-072874", "2017-18", "Tarun", amounts,
    #                                        "20992/43",
    #                                        to_epoch("06/04/17"), 2138, "Cash"))
