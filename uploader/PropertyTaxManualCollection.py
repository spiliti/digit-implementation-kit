import copy

from config import config

from common import search_receipt, search_property, search_demand, update_demand, generate_bill, create_receipt, \
    update_property, superuser_login


def create_manual_receipt_collection(auth_token, tenant_id, property_id, assessment_year, paid_by, payment_amount
                                     , payment_type="Cash"):
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
        return create_manual_receipt_collection(auth_token, tenant_id, property_id, assessment_year, paid_by,
                                                payment_amount)

    demand = search_demand(auth_token, tenant_id, latest_consumer_code, "PT")["Demands"]
    demand_id = demand[0]["id"]

    for demand_detail in demand[0]["demandDetails"]:
        if demand_detail["taxHeadMasterCode"] == "PT_TAX":
            demand_detail["taxAmount"] = payment_amount
        else:
            demand_detail["taxAmount"] = 0

    update_demand(auth_token, demand)
    bill = generate_bill(auth_token, tenant_id, demand_id, latest_consumer_code, "PT")
    bill = bill["Bill"]

    bill_copy = copy.deepcopy(bill)

    receipt_request = [{
        "Bill": bill_copy,
        "instrument": {
            "instrumentType": {
                "name": payment_type
            },
            "tenantId": tenant_id,
            "amount": payment_amount
        },
        "tenantId": tenant_id
    }]

    bill_copy[0]["paidBy"] = paid_by
    bill_copy[0]["billDetails"][0]["collectionType"] = "COUNTER"
    bill_copy[0]["taxAndPayments"][0]["amountPaid"] = payment_amount

    receipt_response = create_receipt(auth_token, tenant_id, receipt_request)
    return receipt_response


if __name__ == "__main__":
    auth_token = superuser_login()["access_token"]
    create_manual_receipt_collection(auth_token, "pb.testing", "PT-1012-072874", "2014-15", "Tarun", 2000)
tl